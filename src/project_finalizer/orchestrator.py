from __future__ import annotations

from pathlib import Path
from typing import Any

from project_finalizer.decisions import DecisionStore
from project_finalizer.errors import ExitCode, WorkflowError
from project_finalizer.io import ProjectFS
from project_finalizer.phases import PhaseContract, phase_for_state
from project_finalizer.runs import RunLedger
from project_finalizer.state import StateStore
from project_finalizer.validation import build_default_registry
from project_finalizer.validators import ValidationContext, ValidatorRegistry


def _packet_paths(contract: PhaseContract) -> tuple[str, str]:
    base = f".workflow/role-packets/{contract.role}"
    return f"{base}/ROLE.md", f"{base}/OUTPUT-CONTRACT.yaml"


def prepare_role_packet(fs: ProjectFS, contract: PhaseContract) -> None:
    role_path, contract_path = _packet_paths(contract)
    role_text = (
        f"# Agent Role Packet — {contract.role}\n\n"
        f"Phase: `{contract.phase_id}`\n\n"
        "Produce only the canonical outputs listed in OUTPUT-CONTRACT.yaml. "
        "Do not invent protected product, API, data, security, privacy, deployment, or irreversible-data decisions.\n"
    )
    payload = {
        "phase": contract.phase_id,
        "role": contract.role,
        "state": contract.state,
        "required_outputs": list(contract.required_outputs),
        "validator_layers": list(contract.validator_layers),
        "next_state": contract.next_state,
        "human_decision_may_block": contract.human_decision_may_block,
    }
    fs.write_text_atomic(role_path, role_text)
    fs.write_yaml_atomic(contract_path, payload)


def _validate_discovery_output(path: str, raw: Any) -> None:
    expected_key = {
        "input-inventory.yaml": "items",
        "requirements.yaml": "requirements",
        "conflicts.yaml": "conflicts",
    }.get(Path(path).name)
    if expected_key is None:
        return
    if not isinstance(raw, dict) or not isinstance(raw.get(expected_key), list):
        raise WorkflowError(
            f"invalid discovery output {path}: expected list field {expected_key}",
            exit_code=ExitCode.VALIDATION_FAILED,
            code="AGENT_ROLE_OUTPUT_INVALID",
        )


def validate_phase_outputs(fs: ProjectFS, contract: PhaseContract) -> tuple[str, ...]:
    missing = tuple(path for path in contract.required_outputs if not fs.resolve(path).is_file())
    if missing:
        prepare_role_packet(fs, contract)
        raise WorkflowError(
            "agent role output required; expected: " + ", ".join(missing),
            exit_code=ExitCode.INVALID_PROJECT_STATE,
            code="AGENT_ROLE_OUTPUT_REQUIRED",
        )
    for path in contract.required_outputs:
        if path.endswith((".yaml", ".yml")):
            raw = fs.read_yaml(path)
            if contract.phase_id == "discover":
                _validate_discovery_output(path, raw)
            elif raw is None:
                raise WorkflowError(
                    f"agent role output is empty: {path}",
                    exit_code=ExitCode.VALIDATION_FAILED,
                    code="AGENT_ROLE_OUTPUT_INVALID",
                )
        else:
            if not fs.read_text(path).strip():
                raise WorkflowError(
                    f"agent role output is empty: {path}",
                    exit_code=ExitCode.VALIDATION_FAILED,
                    code="AGENT_ROLE_OUTPUT_INVALID",
                )
    return contract.required_outputs


def _auxiliary_architecture_contract() -> PhaseContract:
    return PhaseContract(
        state="SOURCE_NORMALIZED",
        phase_id="architecture",
        role="technical-architect",
        required_outputs=("docs/core/TECHNICAL-SPEC.md",),
        validator_layers=("structure", "authority"),
        next_state=None,
        human_decision_may_block=True,
    )


def _run_phase_validators(root: Path, contract: PhaseContract) -> tuple[str, ...]:
    default_registry = build_default_registry()
    validators = tuple(
        validator
        for validator in default_registry.validators
        if validator.layer in contract.validator_layers
    )
    report = ValidatorRegistry(validators).run(
        ValidationContext(
            project_root=root,
            required_paths=contract.required_outputs,
        )
    )
    if not report.ok:
        details = ", ".join(issue.code for issue in report.issues)
        raise WorkflowError(
            f"phase validation failed: {details}",
            exit_code=ExitCode.VALIDATION_FAILED,
            code="PHASE_VALIDATION_FAILED",
        )
    return tuple(f"{validator.name}:PASS" for validator in validators)


def _run_record(
    fs: ProjectFS,
    contract: PhaseContract,
    outputs: tuple[str, ...],
    validator_results: tuple[str, ...],
) -> None:
    ledger = RunLedger(fs)
    run_id = ledger.next_id()
    ledger.start(run_id, agent_role=contract.role, inputs=())
    ledger.record_partial_outputs(run_id, outputs)
    ledger.complete(run_id, validator_results=validator_results)


def run_phase(phase_id: str, project_root: Path) -> ExitCode:
    root = project_root.resolve()
    fs = ProjectFS(root)
    state_store = StateStore(fs)
    state = state_store.load()
    decisions = DecisionStore(fs)

    if phase_id == "resolve":
        pending = decisions.list_pending()
        if pending:
            raise WorkflowError(
                "protected decisions pending: " + ", ".join(pending),
                exit_code=ExitCode.HUMAN_DECISION_REQUIRED,
                code="PROTECTED_DECISION_REQUIRED",
            )
        print("Resolution prerequisites clear")
        return ExitCode.PASS

    if phase_id == "architecture":
        contract = _auxiliary_architecture_contract()
        if state.current != contract.state:
            raise WorkflowError(
                f"architecture requires state {contract.state}; current state is {state.current}",
                exit_code=ExitCode.INVALID_PROJECT_STATE,
                code="PHASE_STATE_MISMATCH",
            )
        outputs = validate_phase_outputs(fs, contract)
        validator_results = _run_phase_validators(root, contract)
        _run_record(fs, contract, outputs, validator_results)
        print("Architecture output validated")
        return ExitCode.PASS

    contract = phase_for_state(state.current)
    if contract is None:
        if state.current == "FINAL_RELEASE":
            print("State: FINAL_RELEASE")
            return ExitCode.PASS
        raise WorkflowError(
            f"no phase contract for state {state.current}",
            exit_code=ExitCode.INVALID_PROJECT_STATE,
            code="PHASE_CONTRACT_MISSING",
        )
    if contract.phase_id != phase_id:
        raise WorkflowError(
            f"phase {phase_id} is not valid in state {state.current}; expected {contract.phase_id}",
            exit_code=ExitCode.INVALID_PROJECT_STATE,
            code="PHASE_STATE_MISMATCH",
        )
    outputs = validate_phase_outputs(fs, contract)
    validator_results = _run_phase_validators(root, contract)
    _run_record(fs, contract, outputs, validator_results)
    if contract.next_state is not None:
        state_store.transition(contract.next_state, {"phase_outputs_valid": True})
    print(f"Phase {phase_id}: PASS")
    return ExitCode.PASS


def resume_project(project_root: Path) -> ExitCode:
    fs = ProjectFS(project_root.resolve())
    state = StateStore(fs).load()
    contract = phase_for_state(state.current)
    if contract is None:
        print(f"State: {state.current}")
        return ExitCode.PASS
    return run_phase(contract.phase_id, project_root)


def finalize_project(project_root: Path) -> ExitCode:
    root = project_root.resolve()
    fs = ProjectFS(root)
    store = StateStore(fs)
    decisions = DecisionStore(fs)
    while True:
        pending = decisions.list_pending()
        if pending:
            raise WorkflowError(
                "protected decisions pending: " + ", ".join(pending),
                exit_code=ExitCode.HUMAN_DECISION_REQUIRED,
                code="PROTECTED_DECISION_REQUIRED",
            )
        state = store.load()
        if state.current == "FINAL_RELEASE":
            print("State: FINAL_RELEASE")
            return ExitCode.PASS
        if state.current in {"CORRECTIVE_COMPLETE", "BUILD_READY"}:
            import argparse

            from project_finalizer.commands.release import handle_release

            return ExitCode(
                handle_release(argparse.Namespace(project=root, output=None))
            )
        contract = phase_for_state(state.current)
        if contract is None:
            raise WorkflowError(
                f"no phase contract for state {state.current}",
                exit_code=ExitCode.INVALID_PROJECT_STATE,
                code="PHASE_CONTRACT_MISSING",
            )
        run_phase(contract.phase_id, root)
