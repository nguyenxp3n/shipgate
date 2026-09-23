from __future__ import annotations

import re
from pathlib import Path
from typing import Any

from project_finalizer.errors import ExitCode, WorkflowError
from project_finalizer.io import ProjectFS
from project_finalizer.manifest import load_workflow_manifest
from project_finalizer.state import StateStore


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _project_id(name: str) -> str:
    value = re.sub(r"[^a-z0-9]+", "-", name.casefold()).strip("-")
    return value or "project"


def initialize_project(root: Path, *, profile: str) -> dict[str, Any]:
    root = root.resolve()
    root.mkdir(parents=True, exist_ok=True)
    fs = ProjectFS(root)
    workflow_dir = root / ".workflow"
    project_path = workflow_dir / "project.yaml"
    if workflow_dir.exists():
        if project_path.is_file() and (workflow_dir / "project-state.yaml").is_file():
            raw = fs.read_yaml(".workflow/project.yaml")
            if isinstance(raw, dict) and isinstance(raw.get("project"), dict):
                return raw
        raise WorkflowError(
            ".workflow already exists but is not a valid initialized project",
            exit_code=ExitCode.INVALID_PROJECT_STATE,
            code="PROJECT_WORKFLOW_DIR_CONFLICT",
        )

    manifest = load_workflow_manifest(_repo_root() / "WORKFLOW-MANIFEST.yaml")
    if profile not in manifest.profiles:
        raise WorkflowError(
            f"unknown profile: {profile}",
            exit_code=ExitCode.PROFILE_ERROR,
            code="PROFILE_UNKNOWN",
        )
    metadata: dict[str, Any] = {
        "project": {
            "id": _project_id(root.name),
            "name": root.name or "project",
            "profile": profile,
            "profile_version": manifest.profiles[profile],
            "workflow_version": manifest.version,
            "core_version": manifest.core_version,
            "input_root": ".",
            "capability_resolution": ".workflow/capabilities.yaml",
        }
    }
    fs.write_yaml_atomic(".workflow/project.yaml", metadata)
    fs.write_yaml_atomic(
        ".workflow/capabilities.yaml",
        {"profile": profile, "capabilities": {}},
    )
    StateStore(fs).initialize()
    return metadata


def load_project_metadata(root: Path) -> dict[str, Any]:
    fs = ProjectFS(root.resolve())
    raw = fs.read_yaml(".workflow/project.yaml")
    if not isinstance(raw, dict) or not isinstance(raw.get("project"), dict):
        raise WorkflowError(
            "project metadata is invalid",
            exit_code=ExitCode.INVALID_PROJECT_STATE,
            code="PROJECT_METADATA_INVALID",
        )
    return raw
