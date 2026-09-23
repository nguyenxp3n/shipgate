from __future__ import annotations

from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator
from jsonschema.exceptions import SchemaError, ValidationError

from project_finalizer.errors import ExitCode, WorkflowError
from project_finalizer.io import ProjectFS


class SchemaRegistry:
    def __init__(self, schema_root: Path) -> None:
        self.schema_root = schema_root
        self.fs = ProjectFS(schema_root)

    def load(self, name: str) -> dict[str, Any]:
        filename = f"{name}.schema.json"
        target = self.fs.resolve(filename)
        if not target.is_file():
            raise WorkflowError(
                f"unknown schema: {name}",
                exit_code=ExitCode.VALIDATION_FAILED,
                code="UNKNOWN_SCHEMA",
            )
        raw = self.fs.read_json(filename)
        if not isinstance(raw, dict):
            raise WorkflowError(
                f"schema must be an object: {name}",
                exit_code=ExitCode.VALIDATION_FAILED,
                code="INVALID_SCHEMA",
            )
        try:
            Draft202012Validator.check_schema(raw)
        except SchemaError as exc:
            raise WorkflowError(
                f"invalid schema {name}: {exc.message}",
                exit_code=ExitCode.VALIDATION_FAILED,
                code="INVALID_SCHEMA",
            ) from exc
        return raw

    def validate(self, name: str, instance: Any) -> None:
        schema = self.load(name)
        validator = Draft202012Validator(schema)
        try:
            validator.validate(instance)
        except ValidationError as exc:
            path = "$"
            for part in exc.absolute_path:
                if isinstance(part, int):
                    path += f"[{part}]"
                else:
                    path += f".{part}"
            raise WorkflowError(
                f"schema validation failed for {name} at {path}: {exc.message}",
                exit_code=ExitCode.VALIDATION_FAILED,
                code="SCHEMA_VALIDATION_FAILED",
            ) from exc
