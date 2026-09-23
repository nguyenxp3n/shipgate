from __future__ import annotations

from project_finalizer.models import ValidationReport
from project_finalizer.web_saas.validators._common import enabled, issue, mapping


class OperationsValidator:
    name = "web-saas-operations"
    layer = "security"

    def validate(self, ctx) -> ValidationReport:
        if not enabled(ctx, "observability"):
            return ValidationReport()
        operations = mapping(ctx, "operations")
        issues = []
        for field, code in (
            ("health_readiness", "WS_OPS_HEALTH_READINESS_REQUIRED"),
            ("observability", "WS_OPS_OBSERVABILITY_REQUIRED"),
            ("deployment", "WS_OPS_DEPLOYMENT_REQUIRED"),
            ("backup_restore", "WS_OPS_BACKUP_RESTORE_REQUIRED"),
        ):
            if operations.get(field) is False:
                issues.append(issue(code, f"operations contract missing {field.replace('_', ' ')}"))
        return ValidationReport(tuple(issues))
