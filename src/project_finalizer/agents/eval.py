from __future__ import annotations

from collections.abc import Mapping
from pathlib import Path
from typing import Any

from project_finalizer.agents.registry import RoleRegistry
from project_finalizer.models import ValidationIssue, ValidationReport


def _workflow_root() -> Path:
    return Path(__file__).resolve().parents[3]


def evaluate_role_output(
    role_id: str,
    packet: Mapping[str, Any],
    output: Mapping[str, Any],
) -> ValidationReport:
    """Evaluate observable agent output against the role contract.

    This intentionally evaluates only declared writes, provenance, decisions, and
    additions. It never attempts to inspect hidden/private reasoning.
    """
    registry = RoleRegistry.load(_workflow_root() / "prompts/ROLE-REGISTRY.yaml")
    role = registry.get(role_id)
    issues: list[ValidationIssue] = []

    writes = output.get("writes", [])
    if isinstance(writes, list):
        for path in writes:
            relative = str(path)
            if not role.can_write(relative):
                issues.append(
                    ValidationIssue(
                        "ROLE_WRITE_BOUNDARY_VIOLATION",
                        f"role {role_id} may not write {relative}",
                        "ERROR",
                        path=relative,
                    )
                )

    if role_id == "discovery":
        resolutions = output.get("conflict_resolutions", [])
        if isinstance(resolutions, list):
            for item in resolutions:
                if (
                    isinstance(item, Mapping)
                    and item.get("chosen_winner")
                    and not item.get("decision_ref")
                ):
                    issues.append(
                        ValidationIssue(
                            "ROLE_DISCOVERY_CHOSE_WINNER",
                            "discovery output chose a conflict winner without authority or a decision reference",
                            "ERROR",
                            subject_id=str(item.get("id", "")),
                        )
                    )

    if role_id == "technical-architect":
        guessed = output.get("protected_decisions_resolved_without_dr", [])
        if isinstance(guessed, list) and guessed:
            issues.append(
                ValidationIssue(
                    "ROLE_PROTECTED_DECISION_NOT_ESCALATED",
                    "protected architecture/product/security decision was resolved without a Decision Request",
                    "ERROR",
                    subject_id=str(guessed[0]),
                )
            )

    if role_id == "contract-compiler":
        additions = output.get("additions", [])
        if isinstance(additions, list):
            for item in additions:
                if isinstance(item, Mapping) and not item.get("requirement_ref"):
                    issues.append(
                        ValidationIssue(
                            "ROLE_UNSUPPORTED_ADDITION",
                            "contract compiler introduced an artifact without requirement/authority provenance",
                            "ERROR",
                            subject_id=str(item.get("id", "")),
                        )
                    )

    if role_id == "readiness-reviewer":
        guessed = output.get("guessed_protected_decisions", [])
        if isinstance(guessed, list) and guessed:
            issues.append(
                ValidationIssue(
                    "ROLE_READINESS_PROTECTED_GUESS",
                    "readiness reviewer guessed a protected decision instead of reporting a blocker",
                    "ERROR",
                    subject_id=str(guessed[0]),
                )
            )

    return ValidationReport(tuple(issues))
