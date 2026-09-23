from __future__ import annotations

import hashlib
import json
import os
import tempfile
from pathlib import Path
from typing import Any

import yaml

from project_finalizer.errors import ExitCode, WorkflowError


class ProjectFS:
    def __init__(self, root: Path) -> None:
        self.root = root

    @property
    def real_root(self) -> Path:
        return self.root.resolve(strict=False)

    def resolve(self, path: str | Path) -> Path:
        raw = Path(path)
        if raw.is_absolute():
            candidate = raw.resolve(strict=False)
        else:
            candidate = (self.real_root / raw).resolve(strict=False)
        root = self.real_root
        if candidate != root and root not in candidate.parents:
            raise WorkflowError(
                f"path is outside project root: {path}",
                exit_code=ExitCode.VALIDATION_FAILED,
                code="PATH_OUTSIDE_ROOT",
            )
        return candidate

    def _resolve_for_write(self, path: str | Path) -> Path:
        raw = Path(path)
        if raw.is_absolute():
            try:
                rel = raw.relative_to(self.real_root)
            except ValueError as exc:
                raise WorkflowError(
                    f"path is outside project root: {path}",
                    exit_code=ExitCode.VALIDATION_FAILED,
                    code="PATH_OUTSIDE_ROOT",
                ) from exc
        else:
            rel = raw

        current = self.real_root
        for part in rel.parts:
            if part in {"", "."}:
                continue
            if part == "..":
                raise WorkflowError(
                    f"path is outside project root: {path}",
                    exit_code=ExitCode.VALIDATION_FAILED,
                    code="PATH_OUTSIDE_ROOT",
                )
            current = current / part
            if current.exists() and current.is_symlink():
                raise WorkflowError(
                    f"write path contains symlink component: {path}",
                    exit_code=ExitCode.VALIDATION_FAILED,
                    code="WRITE_SYMLINK_FORBIDDEN",
                )
        return self.resolve(path)

    def read_text(self, path: str | Path) -> str:
        target = self.resolve(path)
        try:
            return target.read_text(encoding="utf-8")
        except OSError as exc:
            raise WorkflowError(
                f"failed to read {path}: {exc}",
                exit_code=ExitCode.VALIDATION_FAILED,
                code="READ_FAILED",
            ) from exc

    def read_yaml(self, path: str | Path) -> Any:
        text = self.read_text(path)
        try:
            return yaml.safe_load(text)
        except yaml.YAMLError as exc:
            raise WorkflowError(
                f"invalid YAML in {path}: {exc}",
                exit_code=ExitCode.VALIDATION_FAILED,
                code="INVALID_YAML",
            ) from exc

    def read_json(self, path: str | Path) -> Any:
        text = self.read_text(path)
        try:
            return json.loads(text)
        except json.JSONDecodeError as exc:
            raise WorkflowError(
                f"invalid JSON in {path}: {exc}",
                exit_code=ExitCode.VALIDATION_FAILED,
                code="INVALID_JSON",
            ) from exc

    def write_text_atomic(self, path: str | Path, content: str) -> None:
        destination = self._resolve_for_write(path)
        destination.parent.mkdir(parents=True, exist_ok=True)
        temp_path: Path | None = None
        try:
            with tempfile.NamedTemporaryFile(
                mode="w",
                encoding="utf-8",
                dir=destination.parent,
                prefix=f".{destination.name}.",
                suffix=".tmp",
                delete=False,
            ) as handle:
                temp_path = Path(handle.name)
                handle.write(content)
                handle.flush()
                os.fsync(handle.fileno())
            os.replace(temp_path, destination)
            temp_path = None
            self._fsync_directory(destination.parent)
        except OSError as exc:
            raise WorkflowError(
                f"failed to atomically write {path}: {exc}",
                exit_code=ExitCode.INTERNAL_WORKFLOW_ERROR,
                code="ATOMIC_WRITE_FAILED",
            ) from exc
        finally:
            if temp_path is not None:
                try:
                    temp_path.unlink(missing_ok=True)
                except OSError:
                    pass

    def write_yaml_atomic(self, path: str | Path, value: Any) -> None:
        content = yaml.safe_dump(value, sort_keys=False, allow_unicode=True)
        self.write_text_atomic(path, content)

    def write_json_atomic(self, path: str | Path, value: Any) -> None:
        content = json.dumps(value, indent=2, ensure_ascii=False) + "\n"
        self.write_text_atomic(path, content)

    def sha256(self, path: str | Path) -> str:
        target = self.resolve(path)
        try:
            digest = hashlib.sha256()
            with target.open("rb") as handle:
                for chunk in iter(lambda: handle.read(1024 * 1024), b""):
                    digest.update(chunk)
            return digest.hexdigest()
        except OSError as exc:
            raise WorkflowError(
                f"failed to hash {path}: {exc}",
                exit_code=ExitCode.VALIDATION_FAILED,
                code="HASH_FAILED",
            ) from exc

    @staticmethod
    def _fsync_directory(path: Path) -> None:
        if os.name != "posix":
            return
        try:
            fd = os.open(path, os.O_RDONLY)
        except OSError:
            return
        try:
            os.fsync(fd)
        except OSError:
            pass
        finally:
            os.close(fd)
