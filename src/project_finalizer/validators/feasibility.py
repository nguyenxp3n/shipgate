from __future__ import annotations

from project_finalizer.models import ValidationIssue, ValidationReport


class FeasibilityValidator:
    """Validate deterministic declared resource budgets without assuming a specific runner."""

    name = "feasibility"
    layer = "contracts"

    def validate(self, ctx) -> ValidationReport:
        budget = getattr(ctx, "resource_budget", None)
        if not isinstance(budget, dict) or not budget:
            return ValidationReport()
        compile_seconds = float(budget.get("compile_seconds", 0))
        setup_seconds = float(budget.get("setup_seconds", 0))
        case_count = int(budget.get("case_count", 0))
        per_case_seconds = float(budget.get("per_case_seconds", 0))
        overall_seconds = float(budget.get("overall_seconds", 0))
        declared_maximum = compile_seconds + setup_seconds + case_count * per_case_seconds
        if overall_seconds > 0 and declared_maximum > overall_seconds:
            return ValidationReport(
                (
                    ValidationIssue(
                        "FEASIBILITY_TIMEOUT_BUDGET_EXCEEDED",
                        (
                            f"declared maximum workload {declared_maximum:g}s exceeds "
                            f"overall budget {overall_seconds:g}s"
                        ),
                        "ERROR",
                    ),
                )
            )
        return ValidationReport()
