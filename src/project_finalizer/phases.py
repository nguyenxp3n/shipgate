from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class PhaseContract:
    state: str
    phase_id: str
    role: str
    required_outputs: tuple[str, ...]
    validator_layers: tuple[str, ...]
    next_state: str | None
    human_decision_may_block: bool


PHASE_CONTRACTS: dict[str, PhaseContract] = {
    "RAW_INPUT": PhaseContract(
        state="RAW_INPUT",
        phase_id="discover",
        role="discovery",
        required_outputs=(
            ".workflow/phase-outputs/discovery/input-inventory.yaml",
            ".workflow/phase-outputs/discovery/requirements.yaml",
            ".workflow/phase-outputs/discovery/conflicts.yaml",
        ),
        validator_layers=("structure", "references"),
        next_state="INTAKE_COMPLETE",
        human_decision_may_block=False,
    ),
    "INTAKE_COMPLETE": PhaseContract(
        "INTAKE_COMPLETE",
        "normalize",
        "normalization",
        (".workflow/phase-outputs/normalization/normalized-project.yaml",),
        ("structure", "references"),
        "SOURCE_NORMALIZED",
        False,
    ),
    "SOURCE_NORMALIZED": PhaseContract(
        "SOURCE_NORMALIZED",
        "spec",
        "product-architect",
        ("docs/core/PRODUCT-SPEC.md", "docs/core/DOMAIN-MODEL.md"),
        ("structure", "authority"),
        "CORE_SPEC_FROZEN",
        True,
    ),
    "CORE_SPEC_FROZEN": PhaseContract(
        "CORE_SPEC_FROZEN",
        "contracts",
        "contract-compiler",
        ("contracts/CONTRACT-MANIFEST.yaml",),
        ("contracts", "security"),
        "MACHINE_CONTRACTS_READY",
        True,
    ),
    "MACHINE_CONTRACTS_READY": PhaseContract(
        "MACHINE_CONTRACTS_READY",
        "agent-spec",
        "agent-spec-compiler",
        ("docs/agent-spec/AGENT-OPERATING-MANUAL.md",),
        ("structure", "authority"),
        "AGENT_SPEC_READY",
        False,
    ),
    "AGENT_SPEC_READY": PhaseContract(
        "AGENT_SPEC_READY",
        "wp",
        "wp-compiler",
        ("docs/agent-spec/work-packages/WP-000.md", "docs/agent-spec/work-packages/WP-GRAPH.yaml"),
        ("work_packages",),
        "WORK_PACKAGES_READY",
        True,
    ),
    "WORK_PACKAGES_READY": PhaseContract(
        "WORK_PACKAGES_READY",
        "audit",
        "senior-auditor",
        ("docs/audits/QA-SENIOR-AUDIT.yaml",),
        ("audit",),
        "SENIOR_AUDITED",
        False,
    ),
    "SENIOR_AUDITED": PhaseContract(
        "SENIOR_AUDITED",
        "correct",
        "corrective-agent",
        ("docs/audits/QA-AUDIT-DISPOSITION.yaml",),
        ("audit", "authority", "contracts"),
        "CORRECTIVE_COMPLETE",
        True,
    ),
    "CORRECTIVE_COMPLETE": PhaseContract(
        "CORRECTIVE_COMPLETE",
        "readiness",
        "readiness-reviewer",
        ("QA-BUILD-READINESS.yaml",),
        ("readiness",),
        "BUILD_READY",
        False,
    ),
    "BUILD_READY": PhaseContract(
        "BUILD_READY",
        "release",
        "release-compiler",
        ("release/RELEASE-MANIFEST.yaml",),
        ("release",),
        "FINAL_RELEASE",
        True,
    ),
}


def phase_for_state(state: str) -> PhaseContract | None:
    return PHASE_CONTRACTS.get(state)
