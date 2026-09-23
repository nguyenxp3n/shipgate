from pathlib import Path

import pytest

from project_finalizer.errors import WorkflowError
from project_finalizer.intake import scan_inputs


def test_scan_inputs_records_relative_path_size_and_sha256(tmp_path: Path):
    root = tmp_path / "input"
    root.mkdir()
    (root / "notes.md").write_text("hello")
    items = scan_inputs(root)
    assert len(items) == 1
    assert items[0].path == "notes.md"
    assert items[0].size == 5
    assert len(items[0].sha256) == 64


def test_scan_inputs_rejects_symlink(tmp_path: Path):
    root = tmp_path / "input"
    root.mkdir()
    outside = tmp_path / "outside.txt"
    outside.write_text("x")
    (root / "link.txt").symlink_to(outside)
    with pytest.raises(WorkflowError, match="symlink"):
        scan_inputs(root)
