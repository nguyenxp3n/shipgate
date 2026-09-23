# QA — WEB SAAS PROFILE

Generated from structured release evidence.

- SECURITY_PROFILE: PASS
  - evidence: `tests/profile/test_web_saas_static_content.py`
  - evidence: `tests/fixtures/test_invalid_projects.py`
- WEB_SAAS_EXTENSIONS: PASS
  - evidence: `tests/profile/test_extension_inventory.py`
  - evidence: `tests/unit/web_saas/test_extensions.py`

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
