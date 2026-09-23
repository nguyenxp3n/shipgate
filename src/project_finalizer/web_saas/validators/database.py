from __future__ import annotations

from project_finalizer.models import ValidationReport
from project_finalizer.web_saas.validators._common import enabled, issue, mapping


class DatabaseValidator:
    name = "web-saas-database"
    layer = "contracts"

    def validate(self, ctx) -> ValidationReport:
        database = mapping(ctx, "database")
        test_matrix = mapping(ctx, "test_matrix")
        issues = []
        if enabled(ctx, "multi_tenant"):
            for entity in database.get("entities", []):
                if not isinstance(entity, dict) or not entity.get("tenant_owned"):
                    continue
                if not entity.get("tenant_key") or not entity.get("enforcement"):
                    issues.append(
                        issue(
                            "WS_DB_TENANT_BOUNDARY_REQUIRED",
                            "tenant-owned entity requires tenant key and enforcement",
                            subject_id=str(entity.get("id", "unknown")),
                        )
                    )
            security_tests = {str(v) for v in test_matrix.get("security", [])}
            if "tenant_isolation" not in security_tests and "tenant isolation" not in security_tests:
                issues.append(issue("WS_TEST_TENANT_ISOLATION_REQUIRED", "multi-tenant projects require tenant-isolation test evidence"))
        if database and database.get("ownership_resolved") is False:
            issues.append(issue("WS_DB_OWNERSHIP_REQUIRED", "database entities require a single owning module"))
        return ValidationReport(tuple(issues))
