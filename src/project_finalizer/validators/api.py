from __future__ import annotations

from collections.abc import Callable
from pathlib import Path
from typing import Any

import yaml

from project_finalizer.models import ValidationIssue, ValidationReport
from project_finalizer.validators import ValidationContext

try:
    from openapi_spec_validator import validate_spec as _library_validate_spec
except ImportError:  # exact dependency gate is handled explicitly at validation time
    _library_validate_spec = None

_HTTP_METHODS = ("delete", "get", "head", "options", "patch", "post", "put")


class ApiValidator:
    name = "api"
    layer = "contracts"

    def __init__(self, *, validate_spec_func: Callable[[dict[str, Any]], None] | None = None) -> None:
        self._validate_spec = validate_spec_func if validate_spec_func is not None else _library_validate_spec

    def _path(self, ctx: ValidationContext) -> Path | None:
        if ctx.openapi_path is not None:
            return ctx.openapi_path
        candidate = ctx.project_root / "contracts/openapi/openapi.yaml"
        return candidate if candidate.is_file() else None

    def validate(self, ctx: ValidationContext) -> ValidationReport:
        path = self._path(ctx)
        if path is None:
            return ValidationReport()
        try:
            document = yaml.safe_load(path.read_text(encoding="utf-8"))
        except (OSError, UnicodeError, yaml.YAMLError) as exc:
            return ValidationReport((ValidationIssue("API_PARSE", str(exc), "ERROR", path=str(path)),))
        if not isinstance(document, dict):
            return ValidationReport((ValidationIssue("API_PARSE", "OpenAPI document must be a mapping", "ERROR", path=str(path)),))

        issues: list[ValidationIssue] = []
        if self._validate_spec is None:
            issues.append(
                ValidationIssue(
                    "API_PARSE",
                    "openapi-spec-validator dependency is unavailable",
                    "ERROR",
                    path=str(path),
                )
            )
        else:
            try:
                self._validate_spec(document)
            except Exception as exc:
                issues.append(ValidationIssue("API_PARSE", str(exc), "ERROR", path=str(path)))

        seen_operation_ids: dict[str, str] = {}
        paths = document.get("paths", {})
        if not isinstance(paths, dict):
            issues.append(ValidationIssue("API_PARSE", "paths must be a mapping", "ERROR", path=str(path)))
            return ValidationReport(tuple(issues))
        for route in sorted(paths):
            path_item = paths[route]
            if not isinstance(path_item, dict):
                continue
            for method in _HTTP_METHODS:
                operation = path_item.get(method)
                if not isinstance(operation, dict):
                    continue
                subject = f"{method.upper()} {route}"
                operation_id = operation.get("operationId")
                if not isinstance(operation_id, str) or not operation_id.strip():
                    issues.append(ValidationIssue("API_OPERATION_ID_MISSING", "public operation requires operationId", "ERROR", subject_id=subject))
                else:
                    previous = seen_operation_ids.get(operation_id)
                    if previous is not None:
                        issues.append(
                            ValidationIssue(
                                "API_DUPLICATE_OPERATION_ID",
                                f"operationId {operation_id} is duplicated by {previous} and {subject}",
                                "ERROR",
                                subject_id=operation_id,
                            )
                        )
                    else:
                        seen_operation_ids[operation_id] = subject
                for code in operation.get("x-error-codes", ()):
                    if ctx.error_catalog and str(code) not in ctx.error_catalog:
                        issues.append(
                            ValidationIssue(
                                "API_ERROR_CODE_UNKNOWN",
                                f"unregistered error code: {code}",
                                "ERROR",
                                subject_id=subject,
                            )
                        )
                if ctx.api_policy.get("require_auth_metadata") and "x-auth-required" not in operation:
                    issues.append(ValidationIssue("API_AUTH_METADATA_MISSING", "auth metadata is required", "ERROR", subject_id=subject))
                if ctx.api_policy.get("require_idempotency_metadata") and "x-idempotency" not in operation:
                    issues.append(ValidationIssue("API_IDEMPOTENCY_METADATA_MISSING", "idempotency metadata is required", "ERROR", subject_id=subject))
        return ValidationReport(tuple(sorted(issues, key=lambda issue: (issue.code, issue.subject_id or ""))))
