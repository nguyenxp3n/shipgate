from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ReadinessInputs:
    documentation_complete: bool = True
    authority_resolved: bool = True
    machine_contracts_valid: bool = True
    wp_entrypoint_exists: bool = True
    stale_required_artifacts: tuple[str, ...] = ()
    pending_protected_decisions: tuple[str, ...] = ()
    critical_blockers: int = 0
    high_blockers: int = 0
    profile_validators_green: bool = True


@dataclass(frozen=True)
class ReadinessReport:
    documentation_complete: bool
    authority_resolved: bool
    machine_contracts_valid: bool
    wp_entrypoint_exists: bool
    unresolved_protected_decisions: int
    critical_blockers: int
    high_blockers: int
    verdict: str
    blocker_codes: tuple[str, ...]

    def to_mapping(self) -> dict[str, object]:
        return {
            "documentation_complete": self.documentation_complete,
            "authority_resolved": self.authority_resolved,
            "machine_contracts_valid": self.machine_contracts_valid,
            "wp_entrypoint_exists": self.wp_entrypoint_exists,
            "unresolved_protected_decisions": self.unresolved_protected_decisions,
            "critical_blockers": self.critical_blockers,
            "high_blockers": self.high_blockers,
            "verdict": self.verdict,
        }


def evaluate_build_readiness(inputs: ReadinessInputs) -> ReadinessReport:
    blockers: list[str] = []
    if not inputs.documentation_complete:
        blockers.append("READINESS_DOCUMENTATION_INCOMPLETE")
    if not inputs.authority_resolved:
        blockers.append("READINESS_AUTHORITY_UNRESOLVED")
    if not inputs.machine_contracts_valid:
        blockers.append("READINESS_MACHINE_CONTRACTS_INVALID")
    if not inputs.wp_entrypoint_exists:
        blockers.append("READINESS_WP_ENTRYPOINT")
    if inputs.stale_required_artifacts:
        blockers.append("READINESS_STALE_ARTIFACT")
    if inputs.pending_protected_decisions:
        blockers.append("READINESS_PROTECTED_DECISION")
    if inputs.critical_blockers:
        blockers.append("READINESS_CRITICAL_BLOCKER")
    if inputs.high_blockers:
        blockers.append("READINESS_HIGH_BLOCKER")
    if not inputs.profile_validators_green:
        blockers.append("READINESS_PROFILE_VALIDATION")
    return ReadinessReport(
        documentation_complete=inputs.documentation_complete,
        authority_resolved=inputs.authority_resolved,
        machine_contracts_valid=inputs.machine_contracts_valid,
        wp_entrypoint_exists=inputs.wp_entrypoint_exists,
        unresolved_protected_decisions=len(inputs.pending_protected_decisions),
        critical_blockers=inputs.critical_blockers,
        high_blockers=inputs.high_blockers,
        verdict="FAIL" if blockers else "PASS",
        blocker_codes=tuple(blockers),
    )
