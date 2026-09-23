from pathlib import Path

import pytest

from project_finalizer.io import ProjectFS
from project_finalizer.state import StateStore


def test_failed_transition_does_not_replace_persisted_state(tmp_path: Path, monkeypatch):
    root = tmp_path / "project"
    root.mkdir()
    fs = ProjectFS(root)
    store = StateStore(fs)
    store.initialize()
    before = (root / ".workflow/project-state.yaml").read_bytes()

    def fail_write(path, value):
        raise RuntimeError("serializer failed")

    monkeypatch.setattr(fs, "write_yaml_atomic", fail_write)
    with pytest.raises(RuntimeError, match="serializer failed"):
        store.transition("INTAKE_COMPLETE", {})

    after = (root / ".workflow/project-state.yaml").read_bytes()
    assert after == before
