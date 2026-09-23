from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import yaml

from project_finalizer.errors import ExitCode, WorkflowError
from project_finalizer.schemas import SchemaRegistry


@dataclass(frozen=True)
class WorkflowManifest:
    name: str
    version: str
    status: str
    core_version: str
    python: str
    profiles: dict[str, str]
    adapters: dict[str, str]
    schemas_version: str
    normative_artifacts: tuple[str, ...]
    reproducible_release: bool
    release_archive: str
    release_sidecar: str
    qa_reports: tuple[str, ...]


def _find_schema_root(start: Path) -> Path:
    for parent in (start, *start.parents):
        candidate = parent / "schemas"
        if (candidate / "workflow-manifest.schema.json").is_file():
            return candidate
    raise WorkflowError(
        f"could not locate schema root from {start}",
        exit_code=ExitCode.VALIDATION_FAILED,
        code="SCHEMA_ROOT_NOT_FOUND",
    )


def load_workflow_manifest(path: Path) -> WorkflowManifest:
    try:
        raw = yaml.safe_load(path.read_text(encoding="utf-8"))
    except (OSError, yaml.YAMLError) as exc:
        raise WorkflowError(
            f"failed to load workflow manifest {path}: {exc}",
            exit_code=ExitCode.VALIDATION_FAILED,
            code="WORKFLOW_MANIFEST_INVALID",
        ) from exc
    schema_root = _find_schema_root(path.parent)
    SchemaRegistry(schema_root).validate("workflow-manifest", raw)
    assert isinstance(raw, dict)
    workflow = raw["workflow"]
    core = raw["core"]
    runtime = raw["runtime"]
    release = raw["release"]
    return WorkflowManifest(
        name=str(workflow["name"]),
        version=str(workflow["version"]),
        status=str(workflow["status"]),
        core_version=str(core["version"]),
        python=str(runtime["python"]),
        profiles={str(k): str(v) for k, v in raw["profiles"].items()},
        adapters={str(k): str(v) for k, v in raw["adapters"].items()},
        schemas_version=str(raw["schemas_version"]),
        normative_artifacts=tuple(str(value) for value in raw["normative_artifacts"]),
        reproducible_release=bool(release["reproducible"]),
        release_archive=str(release["archive"]),
        release_sidecar=str(release["sidecar"]),
        qa_reports=tuple(str(value) for value in release["qa_reports"]),
    )
