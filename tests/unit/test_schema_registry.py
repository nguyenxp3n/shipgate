from pathlib import Path

import pytest

from project_finalizer.errors import WorkflowError
from project_finalizer.schemas import SchemaRegistry


def test_registry_rejects_unknown_schema(tmp_path: Path):
    registry = SchemaRegistry(tmp_path)
    with pytest.raises(WorkflowError, match="unknown schema"):
        registry.load("missing")


def test_registry_validates_project_state(repo_root: Path):
    registry = SchemaRegistry(repo_root / "schemas")
    registry.validate(
        "project-state",
        {
            "current": "RAW_INPUT",
            "previous": None,
            "allowed_next": ["INTAKE_COMPLETE"],
            "gates": {},
        },
    )
