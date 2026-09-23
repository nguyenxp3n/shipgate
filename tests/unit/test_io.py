from pathlib import Path

import pytest

from project_finalizer.errors import WorkflowError
from project_finalizer.io import ProjectFS


def test_project_fs_rejects_parent_traversal(tmp_path: Path):
    fs = ProjectFS(tmp_path / "project")
    fs.root.mkdir()
    with pytest.raises(WorkflowError, match="outside project root"):
        fs.resolve("../secret.txt")


def test_project_fs_rejects_symlink_escape(tmp_path: Path):
    root = tmp_path / "project"
    outside = tmp_path / "outside"
    root.mkdir()
    outside.mkdir()
    (outside / "secret.txt").write_text("secret")
    (root / "escape").symlink_to(outside, target_is_directory=True)
    fs = ProjectFS(root)
    with pytest.raises(WorkflowError, match="outside project root"):
        fs.read_text("escape/secret.txt")


def test_yaml_loader_does_not_construct_python_objects(tmp_path: Path):
    root = tmp_path / "project"
    root.mkdir()
    (root / "bad.yaml").write_text("!!python/object/apply:os.system ['echo unsafe']")
    fs = ProjectFS(root)
    with pytest.raises(WorkflowError, match="invalid YAML"):
        fs.read_yaml("bad.yaml")


def test_atomic_write_replaces_content(tmp_path: Path):
    root = tmp_path / "project"
    root.mkdir()
    fs = ProjectFS(root)
    fs.write_text_atomic("state.txt", "one")
    fs.write_text_atomic("state.txt", "two")
    assert (root / "state.txt").read_text() == "two"
