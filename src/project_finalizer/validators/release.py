from __future__ import annotations

import hashlib
from pathlib import Path

from project_finalizer.models import ValidationIssue, ValidationReport
from project_finalizer.validators import ValidationContext


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


class ReleaseValidator:
    name = "release"
    layer = "release"

    def validate(self, ctx: ValidationContext) -> ValidationReport:
        stage = ctx.project_root
        checksum = stage / "SHA256SUMS.txt"
        if not checksum.is_file():
            return ValidationReport(
                (ValidationIssue("RELEASE_CHECKSUM_MISSING", "SHA256SUMS.txt is missing", "ERROR"),)
            )
        issues: list[ValidationIssue] = []
        seen: set[str] = set()
        for line in checksum.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            try:
                expected, relative = line.split("  ", 1)
            except ValueError:
                issues.append(
                    ValidationIssue(
                        "RELEASE_CHECKSUM_FORMAT", f"invalid checksum line: {line}", "ERROR"
                    )
                )
                continue
            if relative in seen:
                issues.append(
                    ValidationIssue(
                        "RELEASE_CHECKSUM_DUPLICATE",
                        f"duplicate checksum path: {relative}",
                        "ERROR",
                        path=relative,
                    )
                )
                continue
            seen.add(relative)
            target = stage / relative
            if not target.is_file():
                issues.append(
                    ValidationIssue(
                        "RELEASE_CHECKSUM_TARGET_MISSING",
                        f"checksum target missing: {relative}",
                        "ERROR",
                        path=relative,
                    )
                )
            elif _sha256(target) != expected:
                issues.append(
                    ValidationIssue(
                        "RELEASE_CHECKSUM_MISMATCH",
                        f"checksum mismatch: {relative}",
                        "ERROR",
                        path=relative,
                    )
                )
        actual = {
            path.relative_to(stage).as_posix()
            for path in stage.rglob("*")
            if path.is_file() and path.name != "SHA256SUMS.txt"
        }
        for relative in sorted(actual - seen):
            issues.append(
                ValidationIssue(
                    "RELEASE_CHECKSUM_UNLISTED",
                    f"file missing from checksum inventory: {relative}",
                    "ERROR",
                    path=relative,
                )
            )
        return ValidationReport(tuple(issues))
