from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from project_finalizer.models import ValidationIssue, ValidationReport
from project_finalizer.web_saas.capabilities import CapabilitySet


def enabled(ctx: Any, name: str) -> bool:
    capabilities = getattr(ctx, "capabilities", {})
    if isinstance(capabilities, CapabilitySet):
        return capabilities.enabled(name)
    if isinstance(capabilities, Mapping):
        value = capabilities.get(name, "disabled")
        if isinstance(value, bool):
            return value
        return str(value) in {"required", "optional_enabled", "enabled", "true", "True"}
    return False


def mapping(ctx: Any, name: str) -> dict[str, Any]:
    value = getattr(ctx, name, {})
    return dict(value) if isinstance(value, Mapping) else {}


def report(*issues: ValidationIssue) -> ValidationReport:
    return ValidationReport(tuple(issues))


def issue(code: str, message: str, *, path: str | None = None, subject_id: str | None = None) -> ValidationIssue:
    return ValidationIssue(code=code, message=message, severity="ERROR", path=path, subject_id=subject_id)
