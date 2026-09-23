from __future__ import annotations

from collections.abc import Iterable

from project_finalizer.models import ValidationIssue, ValidationReport
from project_finalizer.validators.base import Validator

LAYER_ORDER = (
    "syntax",
    "structure",
    "references",
    "semantics",
    "authority",
    "contracts",
    "security",
    "work_packages",
    "audit",
    "readiness",
    "release",
)
_LAYER_INDEX = {name: index for index, name in enumerate(LAYER_ORDER)}


def _issue_key(issue: ValidationIssue) -> tuple[str, str, str]:
    return (issue.code, issue.path or "", issue.subject_id or "")


class ValidatorRegistry:
    def __init__(self, validators: Iterable[Validator] = ()) -> None:
        self._validators = tuple(validators)
        for validator in self._validators:
            if validator.layer not in _LAYER_INDEX:
                raise ValueError(f"unknown validator layer: {validator.layer}")

    @property
    def validators(self) -> tuple[Validator, ...]:
        return self._validators

    def run(self, ctx: object) -> ValidationReport:
        issues: list[ValidationIssue] = []
        ordered = sorted(
            self._validators,
            key=lambda validator: (_LAYER_INDEX[validator.layer], validator.name),
        )
        for validator in ordered:
            try:
                report = validator.validate(ctx)  # type: ignore[arg-type]
            except Exception as exc:  # validators are isolation boundaries
                issues.append(
                    ValidationIssue(
                        code="INTERNAL_VALIDATOR_ERROR",
                        message=f"{validator.name}: {exc}",
                        severity="ERROR",
                        subject_id=validator.name,
                    )
                )
                continue
            issues.extend(sorted(report.issues, key=_issue_key))
        return ValidationReport(tuple(issues))
