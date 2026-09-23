from __future__ import annotations

from typing import Any

import yaml

from project_finalizer.errors import WorkflowError
from project_finalizer.models import ValidationIssue, ValidationReport
from project_finalizer.modules import ModuleCatalog
from project_finalizer.validators import ValidationContext

_ERROR_MAP = {
    "DUPLICATE_DATA_OWNER": "OWN_DUPLICATE_OWNER",
    "FOREIGN_DATA_WRITE": "OWN_FOREIGN_WRITE",
    "FORBIDDEN_DATA_WRITE": "OWN_FOREIGN_WRITE",
    "MODULE_DEPENDENCY_CYCLE": "OWN_DEPENDENCY_CYCLE",
    "MODULE_ID_DUPLICATE": "OWN_MODULE_ID_DUPLICATE",
}


def _load_modules(ctx: ValidationContext) -> list[dict[str, Any]]:
    if ctx.modules:
        return [dict(item) for item in ctx.modules]
    module_dir = ctx.project_root / "docs/agent-spec/modules"
    result: list[dict[str, Any]] = []
    if module_dir.is_dir():
        for path in sorted((*module_dir.glob("*.yaml"), *module_dir.glob("*.yml"))):
            raw = yaml.safe_load(path.read_text(encoding="utf-8"))
            if isinstance(raw, dict):
                result.append(raw)
    return result


class OwnershipValidator:
    name = "ownership"
    layer = "semantics"

    def validate(self, ctx: ValidationContext) -> ValidationReport:
        modules = _load_modules(ctx)
        if not modules:
            return ValidationReport()
        try:
            ModuleCatalog.from_mappings(modules)
        except WorkflowError as exc:
            return ValidationReport(
                (
                    ValidationIssue(
                        _ERROR_MAP.get(exc.code, "OWN_MODEL_INVALID"),
                        str(exc),
                        "ERROR",
                    ),
                )
            )
        return ValidationReport()
