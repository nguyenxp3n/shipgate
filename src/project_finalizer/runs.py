from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from project_finalizer.errors import ExitCode, WorkflowError
from project_finalizer.io import ProjectFS
from project_finalizer.schemas import SchemaRegistry


def _now() -> str:
    return datetime.now(UTC).isoformat().replace("+00:00", "Z")


def _schema_registry() -> SchemaRegistry:
    return SchemaRegistry(Path(__file__).resolve().parents[2] / "schemas")


class RunLedger:
    DIR = ".workflow/runs"

    def __init__(self, fs: ProjectFS) -> None:
        self.fs = fs

    def _path(self, run_id: str) -> str:
        return f"{self.DIR}/{run_id}.yaml"

    def _load(self, run_id: str) -> dict[str, Any]:
        path = self.fs.resolve(self._path(run_id))
        if not path.is_file():
            raise WorkflowError(
                f"unknown run: {run_id}",
                exit_code=ExitCode.INVALID_PROJECT_STATE,
                code="RUN_NOT_FOUND",
            )
        raw = self.fs.read_yaml(self._path(run_id))
        if not isinstance(raw, dict):
            raise WorkflowError(
                f"run record is invalid: {run_id}",
                exit_code=ExitCode.VALIDATION_FAILED,
                code="RUN_RECORD_INVALID",
            )
        _schema_registry().validate("run-record", raw)
        return raw

    def start(
        self,
        run_id: str,
        *,
        agent_role: str,
        inputs: tuple[dict[str, str], ...],
        rulings: tuple[str, ...] = (),
        decision_ids: tuple[str, ...] = (),
    ) -> dict[str, Any]:
        if self.fs.resolve(self._path(run_id)).exists():
            raise WorkflowError(
                f"run already exists: {run_id}",
                exit_code=ExitCode.INVALID_PROJECT_STATE,
                code="RUN_ALREADY_EXISTS",
            )
        raw: dict[str, Any] = {
            "run_id": run_id,
            "agent_role": agent_role,
            "status": "STARTED",
            "started_at": _now(),
            "completed_at": None,
            "inputs": list(inputs),
            "outputs": [],
            "rulings": list(rulings),
            "validator_results": [],
            "decision_ids": list(decision_ids),
        }
        _schema_registry().validate("run-record", raw)
        self.fs.write_yaml_atomic(self._path(run_id), raw)
        return raw

    def record_partial_outputs(self, run_id: str, paths: tuple[str, ...]) -> dict[str, Any]:
        raw = self._load(run_id)
        if raw["status"] != "STARTED":
            raise WorkflowError(
                f"run {run_id} is not active",
                exit_code=ExitCode.INVALID_PROJECT_STATE,
                code="RUN_NOT_ACTIVE",
            )
        outputs = []
        for path in paths:
            if not self.fs.resolve(path).is_file():
                raise WorkflowError(
                    f"run output does not exist: {path}",
                    exit_code=ExitCode.VALIDATION_FAILED,
                    code="RUN_OUTPUT_MISSING",
                )
            outputs.append({"path": path, "sha256": self.fs.sha256(path)})
        raw["outputs"] = outputs
        _schema_registry().validate("run-record", raw)
        self.fs.write_yaml_atomic(self._path(run_id), raw)
        return raw

    def complete(
        self,
        run_id: str,
        *,
        validator_results: tuple[str, ...],
        rulings: tuple[str, ...] = (),
        decision_ids: tuple[str, ...] = (),
    ) -> dict[str, Any]:
        raw = self._load(run_id)
        if raw["status"] != "STARTED":
            raise WorkflowError(
                f"run {run_id} is not active",
                exit_code=ExitCode.INVALID_PROJECT_STATE,
                code="RUN_NOT_ACTIVE",
            )
        raw["status"] = "COMPLETE"
        raw["completed_at"] = _now()
        raw["validator_results"] = list(validator_results)
        raw["rulings"] = [*raw.get("rulings", []), *rulings]
        raw["decision_ids"] = sorted(set([*raw.get("decision_ids", []), *decision_ids]))
        _schema_registry().validate("run-record", raw)
        self.fs.write_yaml_atomic(self._path(run_id), raw)
        return raw

    def fail(self, run_id: str, *, validator_results: tuple[str, ...] = ()) -> dict[str, Any]:
        raw = self._load(run_id)
        raw["status"] = "FAILED"
        raw["completed_at"] = _now()
        raw["validator_results"] = list(validator_results)
        _schema_registry().validate("run-record", raw)
        self.fs.write_yaml_atomic(self._path(run_id), raw)
        return raw


    def next_id(self) -> str:
        directory = self.fs.resolve(self.DIR)
        used = {path.stem for path in directory.glob("RUN-*.yaml")} if directory.is_dir() else set()
        index = 1
        while f"RUN-{index:03d}" in used:
            index += 1
        return f"RUN-{index:03d}"

    def output_trust(self, run_id: str) -> str:
        raw = self._load(run_id)
        if raw["status"] == "COMPLETE":
            return "TRUSTED_COMPLETE"
        if raw.get("outputs"):
            return "UNTRUSTED_PARTIAL"
        return "NO_OUTPUT"

    def trusted_outputs(self, run_id: str) -> tuple[dict[str, str], ...]:
        raw = self._load(run_id)
        if raw["status"] != "COMPLETE":
            return ()
        return tuple(dict(item) for item in raw.get("outputs", []))
