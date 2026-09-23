from __future__ import annotations

import argparse
import tempfile
from pathlib import Path

import yaml

from project_finalizer.commands.readiness import collect_readiness_inputs
from project_finalizer.errors import ExitCode, WorkflowError
from project_finalizer.io import ProjectFS
from project_finalizer.qa import render_assurance_summary
from project_finalizer.readiness import evaluate_build_readiness
from project_finalizer.release import (
    build_zip,
    stage_release,
    verify_reextract,
    verify_zip,
    write_sha256sums,
    write_zip_sidecar,
)
from project_finalizer.state import StateStore
from project_finalizer.validation import build_default_registry
from project_finalizer.validators import ValidationContext
from project_finalizer.validators.release import ReleaseValidator


def _ensure_output_outside_project(root: Path, output: Path) -> None:
    root = root.resolve()
    output = output.resolve()
    if output == root or root in output.parents:
        raise WorkflowError(
            "release output must be outside the project tree",
            exit_code=ExitCode.RELEASE_INTEGRITY_FAILED,
            code="RELEASE_OUTPUT_INSIDE_PROJECT",
        )


def _is_workflow_repository(root: Path) -> bool:
    manifest_path = root / "WORKFLOW-MANIFEST.yaml"
    self_hosting_project = root / "self-hosting/project.yaml"
    self_hosting_authority = root / "self-hosting/AUTHORITY-MATRIX.yaml"
    if not (manifest_path.is_file() and self_hosting_project.is_file() and self_hosting_authority.is_file()):
        return False
    try:
        manifest = yaml.safe_load(manifest_path.read_text(encoding="utf-8"))
    except (OSError, yaml.YAMLError):
        return False
    if not isinstance(manifest, dict):
        return False
    workflow = manifest.get("workflow")
    return isinstance(workflow, dict) and workflow.get("name") in {"shipgate", "ai-project-finalization-workflow"}


def _require_workflow_repository_license(root: Path) -> None:
    manifest_path = root / "WORKFLOW-MANIFEST.yaml"
    if not manifest_path.is_file():
        return
    try:
        manifest = yaml.safe_load(manifest_path.read_text(encoding="utf-8"))
    except (OSError, yaml.YAMLError):
        return
    if not isinstance(manifest, dict):
        return
    workflow = manifest.get("workflow")
    if not isinstance(workflow, dict) or workflow.get("name") not in {"shipgate", "ai-project-finalization-workflow"}:
        return

    decision_path = root / "docs/decisions/DR-WF-001-license.yaml"
    license_path = root / "LICENSE"
    if not decision_path.is_file() or not license_path.is_file():
        raise WorkflowError(
            "workflow repository license decision is unresolved",
            exit_code=ExitCode.HUMAN_DECISION_REQUIRED,
            code="RELEASE_LICENSE_DECISION_REQUIRED",
        )
    try:
        decision = yaml.safe_load(decision_path.read_text(encoding="utf-8"))
        license_text = license_path.read_text(encoding="utf-8")
    except (OSError, yaml.YAMLError) as exc:
        raise WorkflowError(
            f"workflow repository license decision is unreadable: {exc}",
            exit_code=ExitCode.HUMAN_DECISION_REQUIRED,
            code="RELEASE_LICENSE_DECISION_REQUIRED",
        ) from exc
    if not isinstance(decision, dict):
        raise WorkflowError(
            "workflow repository license decision is invalid",
            exit_code=ExitCode.HUMAN_DECISION_REQUIRED,
            code="RELEASE_LICENSE_DECISION_REQUIRED",
        )
    resolution = decision.get("resolution")
    choice = resolution.get("choice") if isinstance(resolution, dict) else None
    if (
        decision.get("id") != "DR-WF-001"
        or decision.get("subject") != "repository_license"
        or decision.get("status") != "RESOLVED"
        or not isinstance(choice, str)
        or not choice.strip()
        or not license_text.strip()
    ):
        raise WorkflowError(
            "workflow repository license decision is unresolved",
            exit_code=ExitCode.HUMAN_DECISION_REQUIRED,
            code="RELEASE_LICENSE_DECISION_REQUIRED",
        )
    if choice == "C" and "All Rights Reserved" not in license_text:
        raise WorkflowError(
            "resolved proprietary license decision does not match LICENSE",
            exit_code=ExitCode.VALIDATION_FAILED,
            code="RELEASE_LICENSE_MISMATCH",
        )


def _preflight(root: Path) -> None:
    if _is_workflow_repository(root):
        from project_finalizer.testing import validate_self_hosting

        self_hosting = validate_self_hosting(root)
        if not self_hosting.ok:
            raise WorkflowError(
                f"self-hosting validation failed: {self_hosting.format_issues()}",
                exit_code=ExitCode.VALIDATION_FAILED,
                code="RELEASE_SELF_HOSTING_VALIDATION_FAILED",
            )
        _require_workflow_repository_license(root)
        return

    static_report = build_default_registry().run(ValidationContext(project_root=root))
    if not static_report.ok:
        raise WorkflowError(
            "static validation failed",
            exit_code=ExitCode.VALIDATION_FAILED,
            code="RELEASE_STATIC_VALIDATION_FAILED",
        )
    inputs = collect_readiness_inputs(root)
    if inputs.stale_required_artifacts:
        raise WorkflowError(
            f"stale artifacts: {', '.join(inputs.stale_required_artifacts)}",
            exit_code=ExitCode.STALE_ARTIFACTS,
            code="RELEASE_STALE_ARTIFACTS",
        )
    if inputs.critical_blockers or inputs.high_blockers:
        raise WorkflowError(
            "audit blockers remain",
            exit_code=ExitCode.AUDIT_BLOCKERS_REMAIN,
            code="RELEASE_AUDIT_BLOCKERS",
        )
    readiness = evaluate_build_readiness(inputs)
    if readiness.verdict != "PASS":
        raise WorkflowError(
            f"build readiness failed: {', '.join(readiness.blocker_codes)}",
            exit_code=ExitCode.BUILD_READINESS_FAILED,
            code="RELEASE_BUILD_READINESS_FAILED",
        )
    _require_workflow_repository_license(root)


def handle_release(args: argparse.Namespace) -> int:
    root = Path(args.project).resolve()
    output = Path(args.output).resolve() if args.output else root.parent / f"{root.name}-final-spec.zip"
    _ensure_output_outside_project(root, output)
    workflow_repository = _is_workflow_repository(root)
    _preflight(root)
    state: StateStore | None = None
    if workflow_repository:
        qa_path = root / "QA-BUILD-READINESS.md"
        if not qa_path.exists():
            qa_path.write_text(
                render_assurance_summary(independent_audit=False, self_review=False),
                encoding="utf-8",
            )
    else:
        fs = ProjectFS(root)
        state = StateStore(fs)
        current = state.load()
        if current.current == "CORRECTIVE_COMPLETE":
            fs.write_yaml_atomic(
                ".workflow/readiness-report.yaml",
                evaluate_build_readiness(collect_readiness_inputs(root)).to_mapping(),
            )
            state.transition("BUILD_READY", {})
        elif current.current != "BUILD_READY":
            raise WorkflowError(
                f"release requires CORRECTIVE_COMPLETE or BUILD_READY, got {current.current}",
                exit_code=ExitCode.INVALID_PROJECT_STATE,
                code="RELEASE_STATE_INVALID",
            )
        (root / "QA-BUILD-READINESS.md").write_text(
            render_assurance_summary(independent_audit=False, self_review=False),
            encoding="utf-8",
        )
    with tempfile.TemporaryDirectory(prefix="workflow-release-", dir=output.parent) as temp_dir:
        temp = Path(temp_dir)
        stage = temp / "stage"
        extraction = temp / "extract"
        stage_release(root, stage)
        write_sha256sums(stage)
        report = ReleaseValidator().validate(ValidationContext(project_root=stage))
        if not report.ok:
            raise WorkflowError(
                "release staging validation failed",
                exit_code=ExitCode.RELEASE_INTEGRITY_FAILED,
                code="RELEASE_STAGE_VALIDATION_FAILED",
            )
        build_zip(stage, output)
        verify_zip(output)
        verify_reextract(stage, output, extraction)
    write_zip_sidecar(output)
    if state is not None:
        state.transition("FINAL_RELEASE", {})
    print(output)
    return int(ExitCode.PASS)
