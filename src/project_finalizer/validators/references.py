from __future__ import annotations

from glob import glob
from pathlib import Path
from typing import Any

import yaml

from project_finalizer.models import ValidationIssue, ValidationReport
from project_finalizer.validators import ValidationContext


def _authority_matrix_path(ctx: ValidationContext) -> Path | None:
    if ctx.authority_matrix_path is not None:
        return ctx.authority_matrix_path
    candidates = (
        ctx.project_root / "AUTHORITY-MATRIX.yaml",
        ctx.project_root / "docs/agent-spec/AUTHORITY-MATRIX.yaml",
        ctx.project_root / "core/authority/AUTHORITY-MATRIX.yaml",
    )
    return next((path for path in candidates if path.is_file()), None)


def _authority_refs(ctx: ValidationContext) -> set[str]:
    refs = set(ctx.authority_refs)
    path = _authority_matrix_path(ctx)
    if path is None:
        return refs
    try:
        raw: Any = yaml.safe_load(path.read_text(encoding="utf-8"))
    except (OSError, yaml.YAMLError):
        return refs
    subjects = raw.get("subjects", {}) if isinstance(raw, dict) else {}
    if isinstance(subjects, dict):
        for value in subjects.values():
            if isinstance(value, dict):
                primary = value.get("primary", [])
                if isinstance(primary, list):
                    refs.update(str(item) for item in primary)
    return refs


def _exists(root: Path, ref: str) -> bool:
    if any(ch in ref for ch in "*?["):
        return bool(glob(str(root / ref), recursive=True))
    return (root / ref).exists()


class ReferenceValidator:
    name = "references"
    layer = "references"

    def validate(self, ctx: ValidationContext) -> ValidationReport:
        issues: list[ValidationIssue] = []
        for ref in sorted(_authority_refs(ctx)):
            if not _exists(ctx.project_root, ref):
                issues.append(
                    ValidationIssue(
                        "REF_MISSING_PATH",
                        f"referenced path does not exist: {ref}",
                        "ERROR",
                        path=ref,
                    )
                )
        referenced_ids = getattr(ctx, "referenced_ids", ())
        for logical_id in sorted(str(value) for value in referenced_ids):
            if logical_id not in ctx.known_ids:
                issues.append(
                    ValidationIssue(
                        "REF_UNKNOWN_ID",
                        f"unknown logical ID: {logical_id}",
                        "ERROR",
                        subject_id=logical_id,
                    )
                )
        return ValidationReport(tuple(issues))
