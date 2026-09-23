from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Any

import yaml

from project_finalizer.models import ValidationIssue, ValidationReport
from project_finalizer.validators import ValidationContext

_REQUIRED = (
    "Agent Operating Manual",
    "Authority Matrix",
    "SPEC-MANIFEST",
    "work-packages/README.md",
    "WP-000",
)


def _hash(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class AdapterValidator:
    name = "adapters"
    layer = "references"

    def validate(self, ctx: ValidationContext) -> ValidationReport:
        manifest_path = ctx.project_root / ".workflow/adapter-manifest.yaml"
        if not manifest_path.is_file():
            return ValidationReport()
        raw: Any = yaml.safe_load(manifest_path.read_text(encoding="utf-8"))
        entries = raw.get("adapters", []) if isinstance(raw, dict) else []
        issues: list[ValidationIssue] = []
        for entry in entries:
            if not isinstance(entry, dict):
                continue
            relative = str(entry.get("path", ""))
            path = ctx.project_root / relative
            if not path.is_file():
                issues.append(
                    ValidationIssue("ADAPTER_MISSING", f"generated adapter missing: {relative}", "ERROR", path=relative)
                )
                continue
            text = path.read_text(encoding="utf-8")
            expected = str(entry.get("sha256", ""))
            if _hash(path) != expected:
                issues.append(
                    ValidationIssue(
                        "ADAPTER_NONCANONICAL_TRUTH",
                        f"adapter differs from its generated canonical bootstrap: {relative}",
                        "ERROR",
                        path=relative,
                    )
                )
            positions = [text.find(marker) for marker in _REQUIRED]
            if any(position < 0 for position in positions) or positions != sorted(positions):
                issues.append(
                    ValidationIssue(
                        "ADAPTER_REQUIRED_REFERENCE_MISSING",
                        f"adapter canonical bootstrap order is incomplete: {relative}",
                        "ERROR",
                        path=relative,
                    )
                )
            if "docs/audits/historical" in text:
                issues.append(
                    ValidationIssue(
                        "ADAPTER_HISTORICAL_AUTHORITY",
                        f"adapter must not bootstrap from historical audit authority: {relative}",
                        "ERROR",
                        path=relative,
                    )
                )
        return ValidationReport(tuple(issues))
