import hashlib
from pathlib import Path

from project_finalizer.cli import main


def _tree_hashes(root: Path) -> dict[str, str]:
    return {
        path.relative_to(root).as_posix(): hashlib.sha256(path.read_bytes()).hexdigest()
        for path in sorted(root.rglob("*"))
        if path.is_file() and not path.is_symlink()
    }


def test_audit_input_dry_run_is_non_mutating(tmp_path: Path, capsys):
    root = tmp_path / "raw"
    root.mkdir()
    (root / "notes.md").write_text("Need login and dashboard")
    before = _tree_hashes(root)
    code = main(["audit-input", "--dry-run", "--project", str(root)])
    after = _tree_hashes(root)
    out = capsys.readouterr().out
    assert code == 0
    assert before == after
    assert "Missing artifact classes" in out
    assert "Estimated phases" in out
    assert "Protected decisions" in out
    assert "Capability proposal" in out
