from __future__ import annotations

from project_finalizer.models import ValidationIssue, ValidationReport
from project_finalizer.readiness import ReadinessInputs, evaluate_build_readiness
from project_finalizer.validators import ValidationContext


class ReadinessValidator:
    name = "readiness"
    layer = "readiness"

    def validate(self, ctx: ValidationContext) -> ValidationReport:
        inputs = getattr(ctx, "readiness_inputs", None)
        if inputs is None:
            return ValidationReport()
        if not isinstance(inputs, ReadinessInputs):
            return ValidationReport(
                (
                    ValidationIssue(
                        "READINESS_INPUT_INVALID", "readiness inputs are invalid", "ERROR"
                    ),
                )
            )
        report = evaluate_build_readiness(inputs)
        return ValidationReport(
            tuple(
                ValidationIssue(code, code.replace("_", " ").title(), "ERROR")
                for code in report.blocker_codes
            )
        )
