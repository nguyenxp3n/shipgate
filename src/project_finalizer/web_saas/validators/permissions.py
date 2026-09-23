from __future__ import annotations

from project_finalizer.models import ValidationReport
from project_finalizer.web_saas.validators._common import enabled, issue, mapping


class PermissionsValidator:
    name = "web-saas-permissions"
    layer = "security"

    def validate(self, ctx) -> ValidationReport:
        if not enabled(ctx, "authorization"):
            return ValidationReport()
        permissions = mapping(ctx, "permissions")
        issues = []
        if not permissions.get("catalog"):
            issues.append(
                issue("WS_AUTHZ_CATALOG_REQUIRED", "authorization requires a permission catalog")
            )
        if permissions.get("backend_authoritative") is False:
            issues.append(
                issue(
                    "WS_AUTHZ_BACKEND_AUTHORITY_REQUIRED",
                    "backend authorization must be authoritative",
                )
            )
        return ValidationReport(tuple(issues))
