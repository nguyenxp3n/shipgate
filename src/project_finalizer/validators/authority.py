from __future__ import annotations

from pathlib import Path

from project_finalizer.authority import AuthorityMatrix
from project_finalizer.errors import WorkflowError
from project_finalizer.models import ValidationIssue, ValidationReport
from project_finalizer.validators import ValidationContext

_ERROR_MAP = {
    "HISTORICAL_AUTHORITY_FORBIDDEN": "AUTH_HISTORICAL_LEAKAGE",
    "ADVISORY_AUTHORITY_LEAKAGE": "AUTH_HISTORICAL_LEAKAGE",
    "AUTHORITY_PRIMARY_INVALID": "AUTH_PRIMARY_INVALID",
    "AUTHORITY_COMPOSED_EMPTY": "AUTH_PRIMARY_MISSING",
    "AUTHORITY_MERGE_SEMANTICS_MISSING": "AUTH_MERGE_SEMANTICS_MISSING",
    "AUTHORITY_COMPOSITION_INVALID": "AUTH_COMPOSITION_INVALID",
    "AUTHORITY_MATRIX_INVALID": "AUTH_MATRIX_INVALID",
}


def _matrix_path(ctx: ValidationContext) -> Path | None:
    if ctx.authority_matrix_path is not None:
        return ctx.authority_matrix_path
    for candidate in (
        ctx.project_root / "AUTHORITY-MATRIX.yaml",
        ctx.project_root / "docs/agent-spec/AUTHORITY-MATRIX.yaml",
        ctx.project_root / "core/authority/AUTHORITY-MATRIX.yaml",
    ):
        if candidate.is_file():
            return candidate
    return None


class AuthorityValidator:
    name = "authority"
    layer = "authority"

    def validate(self, ctx: ValidationContext) -> ValidationReport:
        issues: list[ValidationIssue] = []
        path = _matrix_path(ctx)
        if path is not None:
            try:
                AuthorityMatrix.load(path)
            except WorkflowError as exc:
                issues.append(
                    ValidationIssue(
                        _ERROR_MAP.get(exc.code, "AUTH_MATRIX_INVALID"),
                        str(exc),
                        "ERROR",
                        path=path.relative_to(ctx.project_root).as_posix() if path.is_relative_to(ctx.project_root) else str(path),
                    )
                )
        for artifact in sorted(ctx.generated_artifacts, key=lambda item: str(item.get("path", ""))):
            if bool(artifact.get("generated", True)) and not artifact.get("source_refs") and not artifact.get("source_hashes"):
                issues.append(
                    ValidationIssue(
                        "AUTH_GENERATED_PROVENANCE_MISSING",
                        "generated artifact is missing source provenance",
                        "ERROR",
                        path=str(artifact.get("path", "")) or None,
                        subject_id=str(artifact.get("id", "")) or None,
                    )
                )
        return ValidationReport(tuple(issues))
