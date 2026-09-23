from pathlib import Path

import pytest

from project_finalizer.decisions import DecisionStore, require_protected_decision
from project_finalizer.errors import ExitCode, WorkflowError
from project_finalizer.io import ProjectFS


def test_resolved_decision_cannot_be_changed(tmp_path: Path):
    fs = ProjectFS(tmp_path / "project")
    fs.root.mkdir()
    store = DecisionStore(fs)
    store.create("DR-001", subject="license", question="Choose license", options=("A", "B"))
    store.resolve_choice("DR-001", "A")
    with pytest.raises(WorkflowError, match="already resolved"):
        store.resolve_choice("DR-001", "B")


def test_require_protected_decision_returns_human_decision_exit(tmp_path: Path):
    root = tmp_path / "project"
    root.mkdir()
    store = DecisionStore(ProjectFS(root))
    with pytest.raises(WorkflowError) as exc:
        require_protected_decision(store, "license", ("legal approval missing",))
    assert exc.value.exit_code == ExitCode.HUMAN_DECISION_REQUIRED
    assert exc.value.code == "PROTECTED_DECISION_REQUIRED"
    assert store.list_pending()
