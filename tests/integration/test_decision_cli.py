from pathlib import Path

from project_finalizer.cli import main
from project_finalizer.decisions import DecisionStore
from project_finalizer.io import ProjectFS


def test_decision_cli_lists_and_resolves_choice(tmp_path: Path, capsys):
    root = tmp_path / "project"
    root.mkdir()
    store = DecisionStore(ProjectFS(root))
    store.create("DR-001", subject="license", question="Choose license", options=("A", "B"))
    assert main(["decisions", "list", "--project", str(root)]) == 0
    assert "DR-001" in capsys.readouterr().out
    assert main(["decisions", "resolve", "DR-001", "--choice", "A", "--project", str(root)]) == 0
    assert store.show("DR-001")["resolution"]["choice"] == "A"
