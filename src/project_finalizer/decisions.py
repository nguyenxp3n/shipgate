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


class DecisionStore:
    PENDING_DIR = ".workflow/decisions/pending"
    RESOLVED_DIR = ".workflow/decisions/resolved"

    def __init__(self, fs: ProjectFS) -> None:
        self.fs = fs

    def _pending(self, decision_id: str) -> str:
        return f"{self.PENDING_DIR}/{decision_id}.yaml"

    def _resolved(self, decision_id: str) -> str:
        return f"{self.RESOLVED_DIR}/{decision_id}.yaml"

    def _validate(self, raw: dict[str, Any]) -> None:
        _schema_registry().validate("decision-request", raw)

    def create(
        self,
        decision_id: str,
        *,
        subject: str,
        question: str,
        options: tuple[str, ...] = (),
        evidence: tuple[str, ...] = (),
    ) -> dict[str, Any]:
        if self.fs.resolve(self._pending(decision_id)).exists() or self.fs.resolve(
            self._resolved(decision_id)
        ).exists():
            raise WorkflowError(
                f"decision {decision_id} already exists",
                exit_code=ExitCode.INVALID_PROJECT_STATE,
                code="DECISION_ALREADY_EXISTS",
            )
        raw: dict[str, Any] = {
            "id": decision_id,
            "subject": subject,
            "question": question,
            "options": list(options),
            "evidence": list(evidence),
            "status": "PENDING",
            "created_at": _now(),
            "resolution": None,
        }
        self._validate(raw)
        self.fs.write_yaml_atomic(self._pending(decision_id), raw)
        return raw

    def list_pending(self) -> tuple[str, ...]:
        directory = self.fs.resolve(self.PENDING_DIR)
        if not directory.is_dir():
            return ()
        return tuple(sorted(path.stem for path in directory.glob("*.yaml") if path.is_file()))

    def list_resolved(self) -> tuple[str, ...]:
        directory = self.fs.resolve(self.RESOLVED_DIR)
        if not directory.is_dir():
            return ()
        return tuple(sorted(path.stem for path in directory.glob("*.yaml") if path.is_file()))

    def list(self) -> tuple[str, ...]:
        return tuple(sorted((*self.list_pending(), *self.list_resolved())))

    def show(self, decision_id: str) -> dict[str, Any]:
        resolved = self.fs.resolve(self._resolved(decision_id))
        pending = self.fs.resolve(self._pending(decision_id))
        path = self._resolved(decision_id) if resolved.is_file() else self._pending(decision_id)
        if not (resolved.is_file() or pending.is_file()):
            raise WorkflowError(
                f"unknown decision: {decision_id}",
                exit_code=ExitCode.HUMAN_DECISION_REQUIRED,
                code="DECISION_NOT_FOUND",
            )
        raw = self.fs.read_yaml(path)
        if not isinstance(raw, dict):
            raise WorkflowError(
                f"decision {decision_id} is invalid",
                exit_code=ExitCode.VALIDATION_FAILED,
                code="DECISION_INVALID",
            )
        self._validate(raw)
        return raw

    def _resolve(
        self,
        decision_id: str,
        *,
        choice: str | None,
        original_text: str | None,
    ) -> dict[str, Any]:
        if self.fs.resolve(self._resolved(decision_id)).is_file():
            raise WorkflowError(
                f"decision {decision_id} is already resolved",
                exit_code=ExitCode.INVALID_PROJECT_STATE,
                code="DECISION_ALREADY_RESOLVED",
            )
        raw = self.show(decision_id)
        if raw["status"] != "PENDING":
            raise WorkflowError(
                f"decision {decision_id} is already resolved",
                exit_code=ExitCode.INVALID_PROJECT_STATE,
                code="DECISION_ALREADY_RESOLVED",
            )
        if choice is not None and choice not in raw["options"]:
            raise WorkflowError(
                f"choice {choice!r} is not valid for {decision_id}",
                exit_code=ExitCode.HUMAN_DECISION_REQUIRED,
                code="DECISION_CHOICE_INVALID",
            )
        raw["status"] = "RESOLVED"
        raw["resolution"] = {
            "choice": choice,
            "original_text": original_text,
            "resolved_at": _now(),
        }
        self._validate(raw)
        self.fs.write_yaml_atomic(self._resolved(decision_id), raw)
        self.fs.resolve(self._pending(decision_id)).unlink(missing_ok=True)
        return raw

    def resolve_choice(self, decision_id: str, choice: str) -> dict[str, Any]:
        return self._resolve(decision_id, choice=choice, original_text=None)

    def resolve_text(self, decision_id: str, text: str) -> dict[str, Any]:
        return self._resolve(decision_id, choice=None, original_text=text)


def require_protected_decision(
    store: DecisionStore,
    subject: str,
    evidence: tuple[str, ...],
) -> None:
    for decision_id in store.list_pending():
        raw = store.show(decision_id)
        if raw.get("subject") == subject:
            raise WorkflowError(
                f"protected decision required: {decision_id}",
                exit_code=ExitCode.HUMAN_DECISION_REQUIRED,
                code="PROTECTED_DECISION_REQUIRED",
            )
    used = set(store.list())
    index = 1
    while f"DR-{index:03d}" in used:
        index += 1
    decision_id = f"DR-{index:03d}"
    store.create(
        decision_id,
        subject=subject,
        question=f"Resolve protected decision for {subject}",
        options=(),
        evidence=evidence,
    )
    raise WorkflowError(
        f"protected decision required: {decision_id}",
        exit_code=ExitCode.HUMAN_DECISION_REQUIRED,
        code="PROTECTED_DECISION_REQUIRED",
    )
