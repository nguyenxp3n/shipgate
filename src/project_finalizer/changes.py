from __future__ import annotations

from pathlib import Path
from typing import Any

from project_finalizer.artifacts import ArtifactGraph
from project_finalizer.errors import ExitCode, WorkflowError
from project_finalizer.io import ProjectFS
from project_finalizer.schemas import SchemaRegistry


def _registry() -> SchemaRegistry:
    return SchemaRegistry(Path(__file__).resolve().parents[2] / "schemas")


class ChangeStore:
    DIR = ".workflow/changes"

    def __init__(self, fs: ProjectFS) -> None:
        self.fs = fs

    def _path(self, change_id: str) -> str:
        return f"{self.DIR}/{change_id}.yaml"

    def _load(self, change_id: str) -> dict[str, Any]:
        path = self.fs.resolve(self._path(change_id))
        if not path.is_file():
            raise WorkflowError(
                f"unknown change transaction: {change_id}",
                exit_code=ExitCode.INVALID_PROJECT_STATE,
                code="CHANGE_NOT_FOUND",
            )
        raw = self.fs.read_yaml(self._path(change_id))
        if not isinstance(raw, dict):
            raise WorkflowError(
                f"change transaction is invalid: {change_id}",
                exit_code=ExitCode.VALIDATION_FAILED,
                code="CHANGE_INVALID",
            )
        _registry().validate("change-transaction", raw)
        return raw

    def begin(
        self,
        change_id: str,
        *,
        reason: str,
        finding: str | None,
        affected_authorities: tuple[str, ...],
        downstream_artifacts: tuple[str, ...],
        version_impact: str,
    ) -> dict[str, Any]:
        if self.fs.resolve(self._path(change_id)).exists():
            raise WorkflowError(
                f"change transaction already exists: {change_id}",
                exit_code=ExitCode.INVALID_PROJECT_STATE,
                code="CHANGE_ALREADY_EXISTS",
            )
        raw: dict[str, Any] = {
            "id": change_id,
            "status": "OPEN",
            "reason": reason,
            "finding": finding,
            "affected_authorities": list(affected_authorities),
            "downstream_artifacts": list(downstream_artifacts),
            "version_impact": version_impact,
            "validators_green": False,
        }
        _registry().validate("change-transaction", raw)
        self.fs.write_yaml_atomic(self._path(change_id), raw)
        return raw

    def validate(self, change_id: str, *, validators_green: bool) -> dict[str, Any]:
        raw = self._load(change_id)
        if raw["status"] != "OPEN":
            raise WorkflowError(
                f"change {change_id} is not OPEN",
                exit_code=ExitCode.INVALID_PROJECT_STATE,
                code="CHANGE_NOT_OPEN",
            )
        if not validators_green:
            raise WorkflowError(
                f"change {change_id} validators are not green",
                exit_code=ExitCode.VALIDATION_FAILED,
                code="CHANGE_VALIDATION_FAILED",
            )
        raw["status"] = "VALIDATED"
        raw["validators_green"] = True
        _registry().validate("change-transaction", raw)
        self.fs.write_yaml_atomic(self._path(change_id), raw)
        return raw

    def close(
        self,
        change_id: str,
        *,
        artifact_graph: ArtifactGraph,
        current_hashes: dict[str, str],
    ) -> dict[str, Any]:
        raw = self._load(change_id)
        if raw["status"] != "VALIDATED" or not raw["validators_green"]:
            raise WorkflowError(
                f"change {change_id} is not validated",
                exit_code=ExitCode.INVALID_PROJECT_STATE,
                code="CHANGE_NOT_VALIDATED",
            )
        stale = set(artifact_graph.stale_artifacts(current_hashes))
        affected = set(str(item) for item in raw["downstream_artifacts"])
        blocking = sorted(stale & affected)
        if blocking:
            raise WorkflowError(
                f"change {change_id} cannot close with stale artifacts: {', '.join(blocking)}",
                exit_code=ExitCode.STALE_ARTIFACTS,
                code="CHANGE_STALE_ARTIFACTS",
            )
        raw["status"] = "CLOSED"
        _registry().validate("change-transaction", raw)
        self.fs.write_yaml_atomic(self._path(change_id), raw)
        return raw

    def next_id(self) -> str:
        directory = self.fs.resolve(self.DIR)
        used = {path.stem for path in directory.glob("CHG-*.yaml")} if directory.is_dir() else set()
        index = 1
        while f"CHG-{index:04d}" in used:
            index += 1
        return f"CHG-{index:04d}"
