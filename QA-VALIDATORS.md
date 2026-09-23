# QA — VALIDATORS

Generated from structured release evidence.

- AUTHORITY: PASS
  - evidence: `tests/unit/test_authority.py`
  - evidence: `tests/unit/validators/test_authority_validator.py`
- MODULE_OWNERSHIP: PASS
  - evidence: `tests/unit/test_modules.py`
  - evidence: `tests/unit/validators/test_ownership_validator.py`
- MACHINE_CONTRACTS: PASS
  - evidence: `tests/schema/test_base_schemas.py`
  - evidence: `tests/unit/validators/test_api_validator.py`
- TESTING: PASS
  - evidence: `tests/unit/test_work_packages.py`
  - evidence: `tests/examples/test_teamnotes_pipeline.py`
- WORK_PACKAGES: PASS
  - evidence: `tests/unit/test_work_packages.py`
  - evidence: `tests/unit/validators/test_work_package_validator.py`
- AUDIT: PASS
  - evidence: `tests/unit/test_audit.py`
  - evidence: `tests/fixtures/test_invalid_projects.py`

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
