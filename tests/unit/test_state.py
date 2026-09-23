from pathlib import Path

import pytest

from project_finalizer.errors import ExitCode, WorkflowError
from project_finalizer.io import ProjectFS
from project_finalizer.state import ProjectState, StateStore, validate_transition


def test_raw_input_can_move_only_to_intake_complete():
    state = ProjectState(current="RAW_INPUT", previous=None, allowed_next=("INTAKE_COMPLETE",), gates={})
    validate_transition(state, "INTAKE_COMPLETE", {})
    with pytest.raises(WorkflowError) as exc:
        validate_transition(state, "BUILD_READY", {})
    assert exc.value.exit_code == ExitCode.INVALID_PROJECT_STATE


def test_gate_failure_blocks_transition():
    state = ProjectState(
        current="SENIOR_AUDITED",
        previous="WORK_PACKAGES_READY",
        allowed_next=("CORRECTIVE_COMPLETE",),
        gates={"unresolved_critical": 1},
    )
    with pytest.raises(WorkflowError, match="gate"):
        validate_transition(state, "CORRECTIVE_COMPLETE", state.gates)


def test_state_store_initializes_only_once(tmp_path: Path):
    root = tmp_path / "project"
    root.mkdir()
    store = StateStore(ProjectFS(root))
    first = store.initialize()
    assert first.current == "RAW_INPUT"
    with pytest.raises(WorkflowError, match="already initialized"):
        store.initialize()
