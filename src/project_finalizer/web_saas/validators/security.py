from __future__ import annotations

from project_finalizer.models import ValidationReport
from project_finalizer.web_saas.validators._common import enabled, issue, mapping


class SecurityValidator:
    name = "web-saas-security"
    layer = "security"

    def validate(self, ctx) -> ValidationReport:
        security = mapping(ctx, "security")
        issues = []
        if enabled(ctx, "files") and not security.get("file_policy"):
            issues.append(issue("WS_SEC_FILE_POLICY_REQUIRED", "enabled file storage requires an upload/storage security policy"))
        if enabled(ctx, "webhooks") and not security.get("webhook_policy"):
            issues.append(issue("WS_SEC_WEBHOOK_POLICY_REQUIRED", "enabled webhooks require signature/replay policy"))
        ssrf = security.get("ssrf")
        if isinstance(ssrf, dict):
            status = str(ssrf.get("status", ""))
            evidence = ssrf.get("evidence")
            if status == "NOT_APPLICABLE" and not evidence:
                issues.append(issue("WS_SEC_NA_EVIDENCE_REQUIRED", "NOT_APPLICABLE security surfaces require evidence", subject_id="ssrf"))
            if status in {"APPLICABLE", "ENABLED"} and not ssrf.get("policy"):
                issues.append(issue("WS_SEC_SSRF_POLICY_REQUIRED", "applicable outbound URL surface requires SSRF policy", subject_id="ssrf"))
        return ValidationReport(tuple(issues))
