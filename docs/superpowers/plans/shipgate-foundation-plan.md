# AI Project Finalization Workflow V2 Foundation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Establish the installable Python package, contributor command gateway, safe filesystem primitives, schema registry, base schemas, manifest/profile compatibility loader, and public CLI shell required by every later subsystem.

**Architecture:** Keep the deterministic runtime small and dependency-light. `src/project_finalizer/` owns Python logic; top-level `schemas/` owns JSON Schemas; static workflow assets stay outside the package and are loaded relative to the repository/install root. The CLI uses standard-library `argparse`; commands return typed `ExitCode` values and never call `sys.exit` below the CLI boundary.

**Tech Stack:** Python `>=3.12,<3.13`; PyYAML `>=6.0.2,<7`; jsonschema `>=4.23,<5`; packaging `>=24.1,<25`; pytest `>=8.3,<9`; pytest-cov `>=5,<6`; Ruff `>=0.6,<1`; mypy `>=1.11,<2`; uv; Taskfile.

**Spec:** `docs/superpowers/specs/shipgate-architecture-spec.md`

## Global Constraints

- The package distribution name is `ai-project-finalization-workflow`; Python import package is `project_finalizer`; console script is `workflow`.
- Runtime compatibility is exactly `Python >=3.12,<3.13`.
- Generic Core must not import or depend on `profiles/web-saas`.
- CLI exit codes must use the fixed mapping from the spec.
- File writes that alter workflow/project state must be atomic.
- File access must reject traversal outside the configured project root and must not follow symlinks that escape that root.
- YAML must use safe loading; arbitrary object construction is forbidden.
- JSON Schema Draft 2020-12 is the schema dialect for V2.0.0.
- All committed example documents must validate against real schemas, never illustrative-only variants.
- `Taskfile.yml` is the contributor command gateway.

## Review Focus

- An invalid YAML file must return `VALIDATION_FAILED` without a traceback in normal CLI mode and without changing state.
- A path like `../../outside.yaml` or a symlink escaping the root must be rejected by `ProjectFS`.
- Missing or incompatible profile/core versions must return `PROFILE_ERROR` with a stable issue code.
- A duplicate schema ID or unknown schema name must fail deterministically instead of selecting an arbitrary file.
- CLI command functions must remain unit-testable without spawning subprocesses or calling `sys.exit` internally.

---

### Task 1: Bootstrap package, dependency lock, Taskfile, and CLI smoke test

**Files:**
- Create: `pyproject.toml`
- Create: `Taskfile.yml`
- Create: `src/project_finalizer/__init__.py`
- Create: `src/project_finalizer/cli.py`
- Create: `tests/unit/test_cli_smoke.py`
- Create: `tests/conftest.py`
- Create: `.gitignore`
- Create: `README.md`
- Create: `START-HERE.md`
- Create during execution: `uv.lock`

**Interfaces:**
- Consumes: none.
- Produces: `project_finalizer.cli.main(argv: Sequence[str] | None = None) -> int`; console script `workflow`.

- [ ] **Step 1: Write the failing CLI smoke test**

```python
# tests/unit/test_cli_smoke.py
from project_finalizer.cli import main


def test_workflow_version_reports_v2(capsys):
    code = main(["--version"])
    captured = capsys.readouterr()
    assert code == 0
    assert captured.out.strip() == "ai-project-finalization-workflow 2.0.0"
```

- [ ] **Step 2: Run the smoke test and verify RED**

Run:

```bash
python -m pytest tests/unit/test_cli_smoke.py -q
```

Expected: collection/import failure because `project_finalizer` does not exist.

- [ ] **Step 3: Create package metadata and minimal CLI**

Use this `pyproject.toml` structure:

```toml
[build-system]
requires = ["hatchling>=1.25,<2"]
build-backend = "hatchling.build"

[project]
name = "ai-project-finalization-workflow"
version = "2.0.0"
description = "Compile heterogeneous project materials into auditable coding-agent-ready specification packages."
requires-python = ">=3.12,<3.13"
dependencies = [
  "PyYAML>=6.0.2,<7",
  "jsonschema>=4.23,<5",
  "packaging>=24.1,<25",
  "openapi-spec-validator>=0.7.1,<0.8",
]

[project.optional-dependencies]
dev = [
  "pytest>=8.3,<9",
  "pytest-cov>=5,<7",
  "ruff>=0.6,<1",
  "mypy>=1.11,<2",
  "types-PyYAML>=6.0.12,<7",
]

[project.scripts]
workflow = "project_finalizer.cli:entrypoint"

[tool.hatch.build.targets.wheel]
packages = ["src/project_finalizer"]

[tool.pytest.ini_options]
testpaths = ["tests"]
addopts = "-ra"

[tool.ruff]
line-length = 100
target-version = "py312"

[tool.mypy]
python_version = "3.12"
strict = true
packages = ["project_finalizer"]
```

Minimal CLI:

```python
# src/project_finalizer/cli.py
from __future__ import annotations

import argparse
from collections.abc import Sequence

VERSION_TEXT = "ai-project-finalization-workflow 2.0.0"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="workflow")
    parser.add_argument("--version", action="version", version=VERSION_TEXT)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    build_parser().parse_args(argv)
    return 0


def entrypoint() -> None:
    raise SystemExit(main())
```

- [ ] **Step 4: Create the Taskfile command gateway**

`Taskfile.yml` must expose these commands and delegate to `uv run`:

```yaml
version: '3'

tasks:
  setup:
    cmds: ["uv sync --all-extras"]
  format:
    cmds: ["uv run ruff format ."]
  format:check:
    cmds: ["uv run ruff format --check ."]
  lint:
    cmds: ["uv run ruff check ."]
  typecheck:
    cmds: ["uv run mypy src"]
  test:
    cmds: ["uv run pytest"]
  test:unit:
    cmds: ["uv run pytest tests/unit"]
  test:integration:
    cmds: ["uv run pytest tests/integration"]
  test:fixtures:
    cmds: ["uv run pytest tests/fixtures"]
  test:release:
    cmds: ["uv run pytest tests/release"]
  qa:
    cmds:
      - task: format:check
      - task: lint
      - task: typecheck
      - task: test
  release:
    cmds: ["uv run workflow release"]
```

- [ ] **Step 5: Lock dependencies and run GREEN**

Run:

```bash
uv lock
uv sync --all-extras
uv run pytest tests/unit/test_cli_smoke.py -q
```

Expected: `1 passed`.

- [ ] **Step 6: Verify contributor commands**

Run:

```bash
task format:check
task lint
task typecheck
task test:unit
```

Expected: all exit `0`.

- [ ] **Step 7: Commit**

```bash
git add pyproject.toml uv.lock Taskfile.yml src tests .gitignore README.md START-HERE.md
git commit -m "build: bootstrap workflow runtime"
```

---

### Task 2: Add stable exit codes, workflow errors, and validation result types

**Files:**
- Create: `src/project_finalizer/errors.py`
- Create: `src/project_finalizer/models.py`
- Modify: `src/project_finalizer/cli.py`
- Create: `tests/unit/test_errors.py`
- Create: `tests/unit/test_models.py`

**Interfaces:**
- Consumes: `project_finalizer.cli.main` from Task 1.
- Produces: `ExitCode`, `WorkflowError`, `ValidationIssue`, `ValidationReport`.

- [ ] **Step 1: Write failing exit-code tests**

```python
# tests/unit/test_errors.py
from project_finalizer.errors import ExitCode


def test_exit_code_contract_is_stable():
    assert ExitCode.PASS == 0
    assert ExitCode.VALIDATION_FAILED == 10
    assert ExitCode.HUMAN_DECISION_REQUIRED == 20
    assert ExitCode.INVALID_PROJECT_STATE == 30
    assert ExitCode.PROFILE_ERROR == 40
    assert ExitCode.STALE_ARTIFACTS == 50
    assert ExitCode.AUDIT_BLOCKERS_REMAIN == 60
    assert ExitCode.BUILD_READINESS_FAILED == 70
    assert ExitCode.RELEASE_INTEGRITY_FAILED == 80
    assert ExitCode.INTERNAL_WORKFLOW_ERROR == 90
```

```python
# tests/unit/test_models.py
from project_finalizer.models import ValidationIssue, ValidationReport


def test_validation_report_ok_only_when_empty():
    assert ValidationReport(issues=()).ok is True
    report = ValidationReport(issues=(ValidationIssue(code="X", message="bad", severity="ERROR"),))
    assert report.ok is False
```

- [ ] **Step 2: Run tests and verify RED**

```bash
uv run pytest tests/unit/test_errors.py tests/unit/test_models.py -q
```

Expected: import failures for missing modules.

- [ ] **Step 3: Implement exact public types**

```python
# src/project_finalizer/errors.py
from enum import IntEnum


class ExitCode(IntEnum):
    PASS = 0
    VALIDATION_FAILED = 10
    HUMAN_DECISION_REQUIRED = 20
    INVALID_PROJECT_STATE = 30
    PROFILE_ERROR = 40
    STALE_ARTIFACTS = 50
    AUDIT_BLOCKERS_REMAIN = 60
    BUILD_READINESS_FAILED = 70
    RELEASE_INTEGRITY_FAILED = 80
    INTERNAL_WORKFLOW_ERROR = 90


class WorkflowError(Exception):
    def __init__(self, message: str, *, exit_code: ExitCode, code: str) -> None:
        super().__init__(message)
        self.exit_code = exit_code
        self.code = code
```

```python
# src/project_finalizer/models.py
from dataclasses import dataclass


@dataclass(frozen=True)
class ValidationIssue:
    code: str
    message: str
    severity: str
    path: str | None = None
    subject_id: str | None = None


@dataclass(frozen=True)
class ValidationReport:
    issues: tuple[ValidationIssue, ...] = ()

    @property
    def ok(self) -> bool:
        return not self.issues
```

- [ ] **Step 4: Make CLI convert `WorkflowError` to stable exit codes**

Add a `run_cli` boundary that catches `WorkflowError`, writes `ERROR <code>: <message>` to stderr, and returns `int(error.exit_code)`. Do not catch `KeyboardInterrupt` as an internal workflow error.

- [ ] **Step 5: Run GREEN and full unit suite**

```bash
uv run pytest tests/unit/test_errors.py tests/unit/test_models.py tests/unit/test_cli_smoke.py -q
```

Expected: all pass.

- [ ] **Step 6: Commit**

```bash
git add src/project_finalizer/errors.py src/project_finalizer/models.py src/project_finalizer/cli.py tests/unit
git commit -m "feat: define workflow result contracts"
```

---

### Task 3: Implement root-confined filesystem access and atomic writes

**Files:**
- Create: `src/project_finalizer/io.py`
- Create: `tests/unit/test_io.py`

**Interfaces:**
- Consumes: `WorkflowError`, `ExitCode`.
- Produces: `ProjectFS(root: Path)`, `resolve`, `read_text`, `read_yaml`, `read_json`, `write_text_atomic`, `write_yaml_atomic`, `write_json_atomic`, `sha256`.

- [ ] **Step 1: Write traversal, symlink, safe-YAML, and atomic-write tests**

```python
# tests/unit/test_io.py
from pathlib import Path

import pytest

from project_finalizer.errors import WorkflowError
from project_finalizer.io import ProjectFS


def test_project_fs_rejects_parent_traversal(tmp_path: Path):
    fs = ProjectFS(tmp_path / "project")
    fs.root.mkdir()
    with pytest.raises(WorkflowError, match="outside project root"):
        fs.resolve("../secret.txt")


def test_project_fs_rejects_symlink_escape(tmp_path: Path):
    root = tmp_path / "project"
    outside = tmp_path / "outside"
    root.mkdir()
    outside.mkdir()
    (outside / "secret.txt").write_text("secret")
    (root / "escape").symlink_to(outside, target_is_directory=True)
    fs = ProjectFS(root)
    with pytest.raises(WorkflowError, match="outside project root"):
        fs.read_text("escape/secret.txt")


def test_yaml_loader_does_not_construct_python_objects(tmp_path: Path):
    root = tmp_path / "project"
    root.mkdir()
    (root / "bad.yaml").write_text("!!python/object/apply:os.system ['echo unsafe']")
    fs = ProjectFS(root)
    with pytest.raises(WorkflowError, match="invalid YAML"):
        fs.read_yaml("bad.yaml")


def test_atomic_write_replaces_content(tmp_path: Path):
    root = tmp_path / "project"
    root.mkdir()
    fs = ProjectFS(root)
    fs.write_text_atomic("state.txt", "one")
    fs.write_text_atomic("state.txt", "two")
    assert (root / "state.txt").read_text() == "two"
```

- [ ] **Step 2: Run and verify RED**

```bash
uv run pytest tests/unit/test_io.py -q
```

Expected: missing `project_finalizer.io`.

- [ ] **Step 3: Implement root confinement**

Use `Path.resolve(strict=False)` for the candidate and root; reject unless `candidate == root` or `root in candidate.parents`. For reads, resolve the real target before opening. For writes, reject existing symlink components and write only beneath the real root.

- [ ] **Step 4: Implement safe loaders and atomic writes**

`write_*_atomic` must:

1. serialize fully in memory;
2. create a temporary file in the destination directory with `tempfile.NamedTemporaryFile(delete=False)`;
3. flush and `os.fsync` the file;
4. `os.replace(temp, destination)`;
5. best-effort `fsync` the parent directory on POSIX;
6. remove an uncommitted temp file on exceptions.

YAML loading uses `yaml.safe_load`; dump uses `yaml.safe_dump(sort_keys=False, allow_unicode=True)`.

- [ ] **Step 5: Run GREEN plus format/type checks**

```bash
uv run pytest tests/unit/test_io.py -q
uv run ruff check src/project_finalizer/io.py tests/unit/test_io.py
uv run mypy src/project_finalizer/io.py
```

Expected: all pass.

- [ ] **Step 6: Commit**

```bash
git add src/project_finalizer/io.py tests/unit/test_io.py
git commit -m "feat: add safe project filesystem"
```

---

### Task 4: Create the base schema registry and first canonical schemas

**Files:**
- Create: `src/project_finalizer/schemas.py`
- Create: `schemas/workflow-manifest.schema.json`
- Create: `schemas/project.schema.json`
- Create: `schemas/project-state.schema.json`
- Create: `schemas/profile.schema.json`
- Create: `schemas/validation-issue.schema.json`
- Create: `tests/unit/test_schema_registry.py`
- Create: `tests/schema/test_base_schemas.py`

**Interfaces:**
- Consumes: `ProjectFS`, `WorkflowError`.
- Produces: `SchemaRegistry(schema_root: Path)`, `load(name)`, `validate(name, instance)`.

- [ ] **Step 1: Write failing registry tests**

```python
# tests/unit/test_schema_registry.py
from pathlib import Path

import pytest

from project_finalizer.errors import WorkflowError
from project_finalizer.schemas import SchemaRegistry


def test_registry_rejects_unknown_schema(tmp_path: Path):
    registry = SchemaRegistry(tmp_path)
    with pytest.raises(WorkflowError, match="unknown schema"):
        registry.load("missing")


def test_registry_validates_project_state(repo_root: Path):
    registry = SchemaRegistry(repo_root / "schemas")
    registry.validate(
        "project-state",
        {
            "current": "RAW_INPUT",
            "previous": None,
            "allowed_next": ["INTAKE_COMPLETE"],
            "gates": {},
        },
    )
```

Add a `repo_root` fixture to `tests/conftest.py` returning the repository root.

- [ ] **Step 2: Run and verify RED**

```bash
uv run pytest tests/unit/test_schema_registry.py -q
```

Expected: import failure.

- [ ] **Step 3: Implement the schema registry**

The registry maps a logical schema name to `<schema_root>/<name>.schema.json`, validates each schema itself with `Draft202012Validator.check_schema`, and validates instances with `Draft202012Validator`. Convert `jsonschema.ValidationError` into `WorkflowError(exit_code=VALIDATION_FAILED, code="SCHEMA_VALIDATION_FAILED")` including the JSON path.

- [ ] **Step 4: Create the first schemas using Draft 2020-12**

Each schema must include:

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "https://apfw.local/schemas/<name>.schema.json",
  "type": "object",
  "additionalProperties": false
}
```

`project-state.schema.json` must enumerate the lifecycle states from the approved spec and require `current`, `previous`, `allowed_next`, and `gates`.

`profile.schema.json` must require `profile.id`, `profile.version`, `profile.workflow_core_compatibility`, `required_capabilities`, `optional_capabilities`, and `validators`.

- [ ] **Step 5: Add schema self-validation coverage**

```python
# tests/schema/test_base_schemas.py
import json

from jsonschema import Draft202012Validator


def test_every_root_schema_is_valid(repo_root):
    for path in sorted((repo_root / "schemas").glob("*.schema.json")):
        Draft202012Validator.check_schema(json.loads(path.read_text()))
```

- [ ] **Step 6: Run GREEN**

```bash
uv run pytest tests/unit/test_schema_registry.py tests/schema/test_base_schemas.py -q
```

Expected: all pass.

- [ ] **Step 7: Commit**

```bash
git add schemas src/project_finalizer/schemas.py tests/conftest.py tests/unit/test_schema_registry.py tests/schema/test_base_schemas.py
git commit -m "feat: add schema registry and base schemas"
```

---

### Task 5: Implement workflow manifest and profile compatibility loading

**Files:**
- Create: `WORKFLOW-MANIFEST.yaml`
- Create: `src/project_finalizer/manifest.py`
- Create: `src/project_finalizer/profiles.py`
- Create: `tests/unit/test_manifest.py`
- Create: `tests/unit/test_profiles.py`
- Create: `tests/fixtures/profiles/compatible/PROFILE-MANIFEST.yaml`
- Create: `tests/fixtures/profiles/incompatible/PROFILE-MANIFEST.yaml`

**Interfaces:**
- Consumes: `ProjectFS`, `SchemaRegistry`, `packaging.specifiers.SpecifierSet`, `packaging.version.Version`.
- Produces: `WorkflowManifest`, `ProfileManifest`, `load_workflow_manifest`, `load_profile_manifest`, `assert_core_compatible`.

- [ ] **Step 1: Write failing manifest/profile tests**

```python
# tests/unit/test_profiles.py
from pathlib import Path

import pytest

from project_finalizer.errors import ExitCode, WorkflowError
from project_finalizer.profiles import load_profile_manifest


def test_incompatible_profile_returns_profile_error(repo_root: Path):
    with pytest.raises(WorkflowError) as exc:
        load_profile_manifest(
            repo_root / "tests/fixtures/profiles/incompatible/PROFILE-MANIFEST.yaml",
            core_version="2.0.0",
        )
    assert exc.value.exit_code == ExitCode.PROFILE_ERROR
    assert exc.value.code == "PROFILE_CORE_INCOMPATIBLE"
```

```python
# tests/unit/test_manifest.py
from project_finalizer.manifest import load_workflow_manifest


def test_root_manifest_declares_v2_and_python_range(repo_root):
    manifest = load_workflow_manifest(repo_root / "WORKFLOW-MANIFEST.yaml")
    assert manifest.version == "2.0.0"
    assert manifest.python == ">=3.12,<3.13"
    assert manifest.profiles["web-saas"] == "2.0.0"
```

- [ ] **Step 2: Run tests and verify RED**

```bash
uv run pytest tests/unit/test_manifest.py tests/unit/test_profiles.py -q
```

Expected: missing modules/files.

- [ ] **Step 3: Implement frozen dataclass loaders**

Use dataclasses, not a second modeling framework. `WorkflowManifest` exposes `version`, `python`, `profiles`, and `adapters`. `ProfileManifest` exposes `profile_id`, `version`, `core_compatibility`, required/optional capabilities, and validators.

Validate raw YAML through `SchemaRegistry` before constructing dataclasses.

- [ ] **Step 4: Create root manifest exactly matching approved version semantics**

```yaml
workflow:
  name: ai-project-finalization-workflow
  version: 2.0.0
  status: active
core:
  version: 2.0.0
profiles:
  web-saas: 2.0.0
adapters:
  generic: 2.0.0
  codex: 2.0.0
  claude-code: 2.0.0
  gemini-antigravity: 2.0.0
runtime:
  python: ">=3.12,<3.13"
schemas_version: 2.0.0
release:
  reproducible: true
```

- [ ] **Step 5: Add compatible/incompatible fixtures**

Compatible uses `workflow_core_compatibility: ">=2.0,<3.0"`; incompatible uses `">=3.0,<4.0"`.

- [ ] **Step 6: Run GREEN and all schema tests**

```bash
uv run pytest tests/unit/test_manifest.py tests/unit/test_profiles.py tests/schema -q
```

Expected: all pass.

- [ ] **Step 7: Commit**

```bash
git add WORKFLOW-MANIFEST.yaml src/project_finalizer/manifest.py src/project_finalizer/profiles.py tests
git commit -m "feat: load workflow and profile manifests"
```

---

### Task 6: Build the public CLI command tree and non-mutating status shell

**Files:**
- Create: `src/project_finalizer/commands/__init__.py`
- Create: `src/project_finalizer/commands/status.py`
- Create: `src/project_finalizer/commands/stubs.py`
- Modify: `src/project_finalizer/cli.py`
- Create: `tests/unit/test_cli_commands.py`

**Interfaces:**
- Consumes: `ExitCode`, `WorkflowError`, future `StateStore` through a dependency-injected status function.
- Produces: parser entries for every public command in spec; `status` works against a minimal project metadata file; not-yet-implemented phase commands fail explicitly with `INVALID_PROJECT_STATE`/`VALIDATION_FAILED` rather than silently succeeding.

- [ ] **Step 1: Write command-tree tests**

```python
# tests/unit/test_cli_commands.py
from project_finalizer.cli import build_parser, main


PUBLIC_COMMANDS = {
    "init",
    "inspect",
    "discover",
    "normalize",
    "resolve",
    "spec",
    "architecture",
    "contracts",
    "agent-spec",
    "wp",
    "audit",
    "correct",
    "readiness",
    "validate",
    "status",
    "transition",
    "release",
    "resume",
    "decisions",
    "change",
    "audit-input",
    "finalize",
}


def test_parser_exposes_every_public_command():
    parser = build_parser()
    subparsers_action = next(
        action for action in parser._actions if action.__class__.__name__ == "_SubParsersAction"
    )
    assert PUBLIC_COMMANDS == set(subparsers_action.choices)


def test_unimplemented_phase_never_returns_success(capsys):
    code = main(["discover", "--project", "."])
    assert code != 0
    assert "NOT_IMPLEMENTED" in capsys.readouterr().err
```

- [ ] **Step 2: Run and verify RED**

```bash
uv run pytest tests/unit/test_cli_commands.py -q
```

Expected: missing subcommands.

- [ ] **Step 3: Implement subparser registration with handler injection**

Each subcommand sets a callable `handler(args) -> ExitCode`. Nested commands:

```text
decisions list|show|resolve
change begin|validate|close
```

`audit-input` accepts `--dry-run`. Every project-bound command accepts `--project PATH` defaulting to `.`.

- [ ] **Step 4: Implement explicit stubs**

Until later plans replace them, phase handlers raise:

```python
WorkflowError(
    "phase command is not implemented in foundation build",
    exit_code=ExitCode.INVALID_PROJECT_STATE,
    code="NOT_IMPLEMENTED",
)
```

This prevents false-green automation.

- [ ] **Step 5: Implement minimal `status` behavior**

If `.workflow/project-state.yaml` does not exist, return `RAW_INPUT` plus next action `workflow init`. If it exists, parse only the schema-valid fields without mutating the project.

- [ ] **Step 6: Run GREEN and CLI help smoke**

```bash
uv run pytest tests/unit/test_cli_commands.py -q
uv run workflow --help >/tmp/workflow-help.txt
uv run workflow decisions --help >/tmp/workflow-decisions-help.txt
uv run workflow change --help >/tmp/workflow-change-help.txt
```

Expected: tests pass and help commands exit `0`.

- [ ] **Step 7: Run foundation verification gate**

```bash
task format:check
task lint
task typecheck
task test:unit
uv run pytest tests/schema -q
git diff --check
```

Expected: all pass.

- [ ] **Step 8: Commit**

```bash
git add src/project_finalizer/cli.py src/project_finalizer/commands tests/unit/test_cli_commands.py
git commit -m "feat: define workflow CLI command surface"
```

---

## Foundation plan completion evidence

Before moving to the Core Engine Plan, record:

```text
Package import: PASS
workflow --version: 2.0.0
Stable exit-code contract: PASS
Root-confined ProjectFS: PASS
Atomic writes: PASS
Base schemas self-valid: PASS
Manifest/profile compatibility: PASS
Public CLI command surface: PASS
Unimplemented phases falsely succeeding: 0
```
