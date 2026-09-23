from __future__ import annotations

from project_finalizer.models import ValidationReport
from project_finalizer.web_saas.validators._common import enabled, issue, mapping


class AsyncContractsValidator:
    name = "web-saas-async"
    layer = "contracts"

    _FIELDS = {
        "idempotency": "WS_ASYNC_IDEMPOTENCY_REQUIRED",
        "retry": "WS_ASYNC_RETRY_REQUIRED",
        "failure": "WS_ASYNC_FAILURE_REQUIRED",
        "dead_letter": "WS_ASYNC_DEAD_LETTER_REQUIRED",
    }

    def validate(self, ctx) -> ValidationReport:
        if not (enabled(ctx, "events") or enabled(ctx, "jobs") or enabled(ctx, "background_processing")):
            return ValidationReport()
        contract = mapping(ctx, "async_contracts")
        issues = []
        for field, code in self._FIELDS.items():
            if not contract.get(field):
                issues.append(issue(code, f"asynchronous processing requires {field.replace('_', ' ')} semantics"))
        return ValidationReport(tuple(issues))
