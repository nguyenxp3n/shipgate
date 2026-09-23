from __future__ import annotations

from typing import Any

import yaml

from project_finalizer.errors import WorkflowError
from project_finalizer.models import ValidationIssue, ValidationReport
from project_finalizer.validators import ValidationContext
from project_finalizer.work_packages import WorkPackage, WorkPackageGraph


def _load_packages(ctx: ValidationContext) -> list[dict[str, Any]]:
    if ctx.work_packages:
        return [dict(item) for item in ctx.work_packages]
    directory = ctx.project_root / "docs/agent-spec/work-packages"
    result: list[dict[str, Any]] = []
    if directory.is_dir():
        for path in sorted((*directory.glob("WP-*.yaml"), *directory.glob("WP-*.yml"))):
            raw = yaml.safe_load(path.read_text(encoding="utf-8"))
            if isinstance(raw, dict):
                result.append(raw)
    return result


def _to_package(raw: dict[str, Any]) -> WorkPackage:
    return WorkPackage(
        wp_id=str(raw.get("id", "")),
        title=str(raw.get("title", "")),
        state=str(raw.get("state", "")),
        purpose=str(raw.get("purpose", "")),
        depends_on=tuple(str(v) for v in raw.get("depends_on", [])),
        authority_refs=tuple(str(v) for v in raw.get("authority_refs", [])),
        allowed_paths=tuple(str(v) for v in raw.get("allowed_paths", [])),
        forbidden_paths=tuple(str(v) for v in raw.get("forbidden_paths", [])),
        acceptance_commands=tuple(str(v) for v in raw.get("acceptance_commands", [])),
        stop_conditions=tuple(str(v) for v in raw.get("stop_conditions", [])),
        protected_surface=bool(raw.get("protected_surface", False)),
        completion_evidence=tuple(str(v) for v in raw.get("completion_evidence", [])),
        decision_requirements=tuple(str(v) for v in raw.get("decision_requirements", [])),
    )


class WorkPackageValidator:
    name = "work_packages"
    layer = "work_packages"

    def validate(self, ctx: ValidationContext) -> ValidationReport:
        raw_packages = _load_packages(ctx)
        if not raw_packages:
            return ValidationReport()
        issues: list[ValidationIssue] = []
        ids = [str(raw.get("id", "")) for raw in raw_packages]
        if len(ids) != len(set(ids)):
            issues.append(
                ValidationIssue("WP_ID_DUPLICATE", "work package IDs must be unique", "ERROR")
            )
            return ValidationReport(tuple(issues))
        packages = {str(raw.get("id", "")): raw for raw in raw_packages}
        try:
            WorkPackageGraph.from_edges(
                {
                    wp_id: tuple(str(dep) for dep in raw.get("depends_on", []))
                    for wp_id, raw in packages.items()
                }
            )
        except WorkflowError as exc:
            issues.append(ValidationIssue(exc.code, str(exc), "ERROR"))
        for wp_id in sorted(packages):
            raw = packages[wp_id]
            package = _to_package(raw)
            try:
                package.validate()
            except WorkflowError as exc:
                issues.append(ValidationIssue(exc.code, str(exc), "ERROR", subject_id=wp_id))
            if package.state == "READY":
                blocked_deps = [
                    dep
                    for dep in package.depends_on
                    if packages.get(dep, {}).get("state") == "BLOCKED"
                ]
                if blocked_deps:
                    issues.append(
                        ValidationIssue(
                            "WP_DEPENDENCY_NOT_READY",
                            f"READY package depends on BLOCKED package(s): {', '.join(sorted(blocked_deps))}",
                            "ERROR",
                            subject_id=wp_id,
                        )
                    )
                if not package.completion_evidence:
                    issues.append(
                        ValidationIssue(
                            "WP_COMPLETION_EVIDENCE_MISSING",
                            "READY package requires completion evidence",
                            "ERROR",
                            subject_id=wp_id,
                        )
                    )
            overlap = sorted(set(package.allowed_paths) & set(package.forbidden_paths))
            if overlap:
                issues.append(
                    ValidationIssue(
                        "WP_PATH_SCOPE_CONTRADICTION",
                        f"paths are both allowed and forbidden: {', '.join(overlap)}",
                        "ERROR",
                        subject_id=wp_id,
                    )
                )
            known_authorities = ctx.known_authority_ids
            for ref in sorted(package.authority_refs):
                if (
                    known_authorities
                    and ref not in known_authorities
                    and not (ctx.project_root / ref).exists()
                ):
                    issues.append(
                        ValidationIssue(
                            "WP_AUTHORITY_REF_UNKNOWN",
                            f"unknown authority reference: {ref}",
                            "ERROR",
                            subject_id=wp_id,
                        )
                    )
            for invariant in sorted(str(v) for v in raw.get("activated_invariants", [])):
                if ctx.activated_invariants and invariant not in ctx.activated_invariants:
                    issues.append(
                        ValidationIssue(
                            "WP_INVARIANT_UNKNOWN",
                            f"unknown activated invariant: {invariant}",
                            "ERROR",
                            subject_id=wp_id,
                        )
                    )
            if bool(raw.get("protected_surface", False)) and not package.stop_conditions:
                issues.append(
                    ValidationIssue(
                        "WP_PROTECTED_STOP_MISSING",
                        "protected-surface package requires stop conditions",
                        "ERROR",
                        subject_id=wp_id,
                    )
                )
        return ValidationReport(
            tuple(sorted(issues, key=lambda issue: (issue.code, issue.subject_id or "")))
        )
