from __future__ import annotations

from project_finalizer.models import ValidationIssue, ValidationReport
from project_finalizer.validators import ValidationContext


class StructureValidator:
    name = "structure"
    layer = "structure"

    def validate(self, ctx: ValidationContext) -> ValidationReport:
        issues = []
        for required in sorted(ctx.required_paths):
            if not (ctx.project_root / required).exists():
                issues.append(
                    ValidationIssue(
                        "STRUCTURE_REQUIRED_PATH_MISSING",
                        f"required path does not exist: {required}",
                        "ERROR",
                        path=required,
                    )
                )
        return ValidationReport(tuple(issues))
