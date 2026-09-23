from __future__ import annotations

import argparse
from pathlib import Path

from project_finalizer.errors import ExitCode, WorkflowError
from project_finalizer.intake import scan_inputs


def handle_audit_input(args: argparse.Namespace) -> ExitCode:
    if not args.dry_run:
        raise WorkflowError(
            "audit-input requires --dry-run in V2.0.0",
            exit_code=ExitCode.INVALID_PROJECT_STATE,
            code="DRY_RUN_REQUIRED",
        )
    root = Path(args.project).resolve()
    items = scan_inputs(root)
    print(f"Input files: {len(items)}")
    print(
        "Missing artifact classes: canonical-core-spec, authority-matrix, agent-spec, work-packages, audit"
    )
    print("Conflicts: none machine-detectable without semantic agent review")
    print(
        "Estimated phases: discover, normalize, spec, contracts, agent-spec, wp, audit, correct, readiness, release"
    )
    print("Protected decisions: product/security/data/API/deployment decisions may be required")
    print(
        "Capability proposal: web-saas core capabilities require human/profile resolution after discovery"
    )
    return ExitCode.PASS
