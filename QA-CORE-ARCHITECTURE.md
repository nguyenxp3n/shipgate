# QA — CORE ARCHITECTURE

Generated from structured release evidence.

- LIFECYCLE: PASS
  - evidence: `tests/unit/test_state.py`
  - evidence: `tests/integration/test_phase_commands.py`
- PROVENANCE: PASS
  - evidence: `tests/unit/test_intake.py`
  - evidence: `tests/unit/test_artifacts.py`
- CROSS_MODULE_CONTRACTS: PASS
  - evidence: `tests/unit/test_modules.py`
  - evidence: `tests/fixtures/test_hcn_regression_lessons.py`
- STALENESS: PASS
  - evidence: `tests/integration/test_staleness.py`
  - evidence: `tests/unit/test_artifacts.py`

## Verification commands

- `PYTHONPATH=src:/tmp/workflow-test-support python3 -m pytest -q -> 152 passed`
- `PYTHONPATH=src:/tmp/workflow-test-support python3 -m pytest tests/examples -q -> 3 passed`
- `PYTHONPATH=src:/tmp/workflow-test-support python3 -m pytest tests/fixtures -q -> 13 passed`
- `PYTHONPATH=src:/tmp/workflow-test-support python3 -m pytest tests/agents -q -> 5 passed`
- `PYTHONPATH=src:/tmp/workflow-test-support python3 -m pytest tests/self_hosting -q -> 1 passed`
- `PYTHONPATH=src:/tmp/workflow-test-support python3 -m pytest tests/release -q -> 14 passed`
- `python3 -m compileall -q src -> PASS`
- `git diff --check -> PASS`
- `validate_self_hosting(.) -> PASS`
- `validate_example_project(examples/teamnotes) -> PASS`
- `Final whole-branch review -> self-review (no subagent tool); 2 Important findings fixed RED→GREEN`
