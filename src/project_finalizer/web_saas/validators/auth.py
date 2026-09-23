from __future__ import annotations

from project_finalizer.models import ValidationReport
from project_finalizer.web_saas.validators._common import issue, mapping


class AuthValidator:
    name = "web-saas-auth"
    layer = "security"

    def validate(self, ctx) -> ValidationReport:
        auth = mapping(ctx, "auth")
        issues = []
        if auth.get("credential_transport") == "cookie" and not auth.get("csrf"):
            issues.append(
                issue(
                    "WS_AUTH_CSRF_REQUIRED",
                    "cookie credentials require an explicit CSRF disposition",
                )
            )
        if auth.get("cross_origin_credentials"):
            origins = auth.get("cors_allowed_origins")
            if not isinstance(origins, list) or not origins or "*" in origins:
                issues.append(
                    issue(
                        "WS_AUTH_CORS_EXACT_ORIGINS_REQUIRED",
                        "credentialed cross-origin access requires exact origins",
                    )
                )
        if auth.get("credential_transport") and not auth.get("session_or_token_model", True):
            issues.append(
                issue(
                    "WS_AUTH_SESSION_MODEL_REQUIRED",
                    "authentication requires explicit session/token lifecycle semantics",
                )
            )
        return ValidationReport(tuple(issues))
