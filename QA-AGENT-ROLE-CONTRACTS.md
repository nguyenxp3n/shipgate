# QA — AGENT ROLE CONTRACTS

Generated from structured release evidence.

- CONTROLLED_AUTONOMY: PASS
  - evidence: `tests/unit/test_decisions.py`
  - evidence: `tests/agents/test_role_evals.py`
- ADAPTERS: PASS
  - evidence: `tests/unit/generators/test_adapters.py`
  - evidence: `tests/unit/validators/test_adapters.py`

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
