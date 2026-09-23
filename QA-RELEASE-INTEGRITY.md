# QA — RELEASE INTEGRITY

Generated from structured release evidence.

- RELEASE: PASS
  - evidence: `tests/release/test_release_archive.py`
  - evidence: `tests/release/test_release_security.py`
  - evidence: `tests/integration/test_release_command.py`

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

## Environment limitations

- Exact Python 3.12 execution was not performed because this environment provides Python 3.13.5 and uv cannot download Python 3.12 due DNS/network failure.
- Official go-task execution was not performed because task/go-task is not installed and network installation is unavailable.
- Ruff and mypy execution was not performed because those tools are not installed and dependency installation is network-blocked.
- A frozen uv dependency installation/lock resolution was not certified in this environment because the required Python/dependency downloads are network-blocked.
- Real openapi-spec-validator integration was not performed because the dependency is unavailable; behavioral OpenAPI-dependent tests used an uncommitted /tmp compatibility shim only for interim static-path execution.
- AI-provider execution integration was not performed in this environment.
- Independent senior review was not performed because this harness exposes no subagent review tool; final review mode is author self-review.
