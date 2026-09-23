from pathlib import Path

from project_finalizer.cli import main


def test_init_creates_project_metadata_and_raw_state(tmp_path: Path):
    root = tmp_path / "project"
    root.mkdir()
    code = main(["init", str(root), "--profile", "web-saas"])
    assert code == 0
    assert (root / ".workflow/project.yaml").exists()
    assert "RAW_INPUT" in (root / ".workflow/project-state.yaml").read_text()
