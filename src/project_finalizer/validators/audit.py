from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from project_finalizer.audit import AuditLedger
from project_finalizer.models import ValidationIssue, ValidationReport
from project_finalizer.validators import ValidationContext


def _read_records(path: Path) -> list[dict[str, Any]]:
    if not path.is_file():
        return []
    raw = yaml.safe_load(path.read_text(encoding="utf-8"))
    if raw is None:
        return []
    if isinstance(raw, dict):
        for key in ("findings", "dispositions"):
            value = raw.get(key)
            if isinstance(value, list):
                return [dict(item) for item in value if isinstance(item, dict)]
    if isinstance(raw, list):
        return [dict(item) for item in raw if isinstance(item, dict)]
    return []


class AuditValidator:
    name = "audit"
    layer = "audit"

    def validate(self, ctx: ValidationContext) -> ValidationReport:
        audit_dir = ctx.project_root / "docs/audits"
        findings_path = audit_dir / "findings.yaml"
        dispositions_path = audit_dir / "dispositions.yaml"
        if not findings_path.exists() and not dispositions_path.exists():
            return ValidationReport()
        try:
            ledger = AuditLedger.from_records(
                findings=_read_records(findings_path),
                dispositions=_read_records(dispositions_path),
            )
            return ledger.closure_report()
        except (OSError, yaml.YAMLError) as exc:
            return ValidationReport(
                (ValidationIssue("AUDIT_PARSE", str(exc), "ERROR", path="docs/audits"),)
            )
