from __future__ import annotations

import argparse
import json
from dataclasses import asdict

from project_finalizer.errors import ExitCode
from project_finalizer.validation import build_default_registry
from project_finalizer.validators import ValidationContext


def _print_human(report) -> None:
    for issue in report.issues:
        path = issue.path or "-"
        subject = issue.subject_id or "-"
        print(f"{issue.severity} {issue.code} {path} {subject}: {issue.message}")


def handle_validate(args: argparse.Namespace) -> int:
    root = args.project.resolve()
    from project_finalizer.commands.release import _is_workflow_repository

    if _is_workflow_repository(root):
        from project_finalizer.models import ValidationReport
        from project_finalizer.testing import validate_self_hosting

        result = validate_self_hosting(root)
        report = ValidationReport(issues=result.issues)
    else:
        report = build_default_registry().run(ValidationContext(project_root=root))
    if args.format == "json":
        print(
            json.dumps(
                {"ok": report.ok, "issues": [asdict(issue) for issue in report.issues]},
                sort_keys=True,
            )
        )
    else:
        _print_human(report)
    if any(issue.code == "INTERNAL_VALIDATOR_ERROR" for issue in report.issues):
        return int(ExitCode.INTERNAL_WORKFLOW_ERROR)
    if not report.ok:
        return int(ExitCode.VALIDATION_FAILED)
    return int(ExitCode.PASS)
