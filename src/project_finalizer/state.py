from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from project_finalizer.errors import ExitCode, WorkflowError
from project_finalizer.io import ProjectFS

LIFECYCLE = (
    "RAW_INPUT",
    "INTAKE_COMPLETE",
    "SOURCE_NORMALIZED",
    "CORE_SPEC_FROZEN",
    "MACHINE_CONTRACTS_READY",
    "AGENT_SPEC_READY",
    "WORK_PACKAGES_READY",
    "SENIOR_AUDITED",
    "CORRECTIVE_COMPLETE",
    "BUILD_READY",
    "FINAL_RELEASE",
)

ADJACENCY: dict[str, tuple[str, ...]] = {
    state: ((LIFECYCLE[index + 1],) if index + 1 < len(LIFECYCLE) else ())
    for index, state in enumerate(LIFECYCLE)
}


@dataclass(frozen=True)
class ProjectState:
    current: str
    previous: str | None
    allowed_next: tuple[str, ...]
    gates: dict[str, Any]

    @classmethod
    def from_mapping(cls, raw: dict[str, Any]) -> ProjectState:
        try:
            current = str(raw["current"])
            previous_raw = raw["previous"]
            previous = None if previous_raw is None else str(previous_raw)
            allowed_next = tuple(str(v) for v in raw["allowed_next"])
            gates = dict(raw["gates"])
        except (KeyError, TypeError, ValueError) as exc:
            raise WorkflowError(
                "project state is invalid",
                exit_code=ExitCode.INVALID_PROJECT_STATE,
                code="PROJECT_STATE_INVALID",
            ) from exc
        if current not in ADJACENCY:
            raise WorkflowError(
                f"unknown project state: {current}",
                exit_code=ExitCode.INVALID_PROJECT_STATE,
                code="PROJECT_STATE_INVALID",
            )
        if previous is not None and previous not in ADJACENCY:
            raise WorkflowError(
                f"unknown previous project state: {previous}",
                exit_code=ExitCode.INVALID_PROJECT_STATE,
                code="PROJECT_STATE_INVALID",
            )
        return cls(current=current, previous=previous, allowed_next=allowed_next, gates=gates)

    def to_mapping(self) -> dict[str, Any]:
        return {
            "current": self.current,
            "previous": self.previous,
            "allowed_next": list(self.allowed_next),
            "gates": self.gates,
        }


def _blocking_gates(gates: dict[str, Any]) -> list[str]:
    blocked: list[str] = []
    for key, value in gates.items():
        if isinstance(value, bool) and value is False:
            blocked.append(key)
        elif isinstance(value, (int, float)) and not isinstance(value, bool):
            lowered = key.casefold()
            if value > 0 and (
                lowered.startswith("unresolved_")
                or lowered.endswith("_blockers")
                or lowered in {"critical", "high"}
            ):
                blocked.append(key)
    return sorted(blocked)


def validate_transition(
    state: ProjectState,
    target: str,
    gate_results: dict[str, Any],
) -> None:
    if target not in ADJACENCY.get(state.current, ()) or target not in state.allowed_next:
        raise WorkflowError(
            f"illegal transition {state.current} -> {target}",
            exit_code=ExitCode.INVALID_PROJECT_STATE,
            code="ILLEGAL_STATE_TRANSITION",
        )
    blocked = _blocking_gates(gate_results)
    if blocked:
        raise WorkflowError(
            f"transition blocked by gate(s): {', '.join(blocked)}",
            exit_code=ExitCode.INVALID_PROJECT_STATE,
            code="TRANSITION_GATE_FAILED",
        )


class StateStore:
    PATH = ".workflow/project-state.yaml"

    def __init__(self, fs: ProjectFS) -> None:
        self.fs = fs

    def exists(self) -> bool:
        return self.fs.resolve(self.PATH).is_file()

    def load(self) -> ProjectState:
        if not self.exists():
            raise WorkflowError(
                "project state is not initialized",
                exit_code=ExitCode.INVALID_PROJECT_STATE,
                code="PROJECT_STATE_MISSING",
            )
        raw = self.fs.read_yaml(self.PATH)
        if not isinstance(raw, dict):
            raise WorkflowError(
                "project state must be a mapping",
                exit_code=ExitCode.INVALID_PROJECT_STATE,
                code="PROJECT_STATE_INVALID",
            )
        return ProjectState.from_mapping(raw)

    def initialize(self) -> ProjectState:
        if self.exists():
            raise WorkflowError(
                "project state is already initialized",
                exit_code=ExitCode.INVALID_PROJECT_STATE,
                code="PROJECT_STATE_ALREADY_INITIALIZED",
            )
        state = ProjectState(
            current="RAW_INPUT",
            previous=None,
            allowed_next=ADJACENCY["RAW_INPUT"],
            gates={},
        )
        self.fs.write_yaml_atomic(self.PATH, state.to_mapping())
        return state

    def transition(self, target: str, gate_results: dict[str, Any]) -> ProjectState:
        current = self.load()
        validate_transition(current, target, gate_results)
        new_state = ProjectState(
            current=target,
            previous=current.current,
            allowed_next=ADJACENCY[target],
            gates=dict(gate_results),
        )
        self.fs.write_yaml_atomic(self.PATH, new_state.to_mapping())
        return new_state
