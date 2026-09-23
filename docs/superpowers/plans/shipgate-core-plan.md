# AI Project Finalization Workflow V2 Core Engine Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Implement the Generic Core execution model: source intake/provenance, lifecycle transitions, Decision Requests, change transactions, typed authority, artifact staleness, module/ownership/interaction graphs, work-package DAGs, run ledger, and failure recovery.

**Architecture:** Represent all durable workflow state as schema-validated YAML/JSON under `.workflow/` inside a target project. Keep models immutable where possible and mutate through service objects that validate before atomic write. Separate canonical state from derived indexes so staleness and regeneration can be reasoned about explicitly.

**Tech Stack:** Python 3.12 dataclasses/enums; ProjectFS and SchemaRegistry from Foundation Plan; PyYAML/jsonschema; hashlib; graph algorithms implemented in small standard-library utilities rather than introducing a graph framework.

**Spec:** `docs/superpowers/specs/shipgate-architecture-spec.md`

## Global Constraints

- Generic Core remains profile-agnostic.
- Project lifecycle states are exactly those in the approved design.
- Illegal state transitions must fail without mutating persisted state.
- Protected ambiguity must produce a Decision Request rather than an invented choice.
- Authority is typed by subject and allows composition only when the Authority Matrix explicitly permits it.
- Historical/advisory artifacts can never satisfy normative authority requirements.
- Generated artifacts must carry upstream source hashes; changed upstream sources make dependents stale.
- Module ownership must detect duplicate ownership and foreign writes.
- Work-package dependencies form an acyclic graph with an explicit entrypoint.
- Run records never contain private reasoning; only inputs, outputs, hashes, rulings, validation evidence, and timestamps.

## Review Focus

- State files modified concurrently or interrupted mid-write must never leave a half-valid state.
- Unicode/casefold-equivalent IDs such as `Users` and `users` must be treated as conflicting logical IDs where an ID namespace is case-insensitive.
- A source artifact deleted after derived artifacts were generated must mark those dependents stale, not silently ignore the missing dependency.
- A Decision Request resolved twice with different content must be rejected as an immutable-resolution conflict.
- Work-package DAG validation must catch self-dependency and multi-node cycles while preserving deterministic error order.

---

### Task 1: Add the complete core schema inventory for durable project records

**Files:**
- Create: `schemas/requirement.schema.json`
- Create: `schemas/conflict.schema.json`
- Create: `schemas/decision-request.schema.json`
- Create: `schemas/authority-matrix.schema.json`
- Create: `schemas/artifact.schema.json`
- Create: `schemas/module.schema.json`
- Create: `schemas/ownership.schema.json`
- Create: `schemas/interaction.schema.json`
- Create: `schemas/command.schema.json`
- Create: `schemas/test-invariant.schema.json`
- Create: `schemas/work-package.schema.json`
- Create: `schemas/work-package-graph.schema.json`
- Create: `schemas/audit-finding.schema.json`
- Create: `schemas/audit-disposition.schema.json`
- Create: `schemas/run-record.schema.json`
- Create: `schemas/change-transaction.schema.json`
- Create: `schemas/readiness-report.schema.json`
- Create: `schemas/release-manifest.schema.json`
- Create: `tests/schema/test_required_schema_inventory.py`
- Modify: `tests/schema/test_base_schemas.py`

**Interfaces:**
- Consumes: `SchemaRegistry`.
- Produces: all root machine schemas required by design Section 54.1.

- [ ] **Step 1: Write the failing inventory test**

```python
# tests/schema/test_required_schema_inventory.py
REQUIRED = {
    "workflow-manifest", "project", "project-state", "profile", "requirement",
    "conflict", "decision-request", "authority-matrix", "artifact", "module",
    "ownership", "interaction", "command", "test-invariant", "work-package",
    "work-package-graph", "audit-finding", "audit-disposition", "run-record",
    "change-transaction", "readiness-report", "release-manifest",
}


def test_required_schema_inventory_exists(repo_root):
    actual = {p.name.removesuffix(".schema.json") for p in (repo_root / "schemas").glob("*.schema.json")}
    assert REQUIRED <= actual
```

- [ ] **Step 2: Run and verify RED**

```bash
uv run pytest tests/schema/test_required_schema_inventory.py -q
```

Expected: assertion failure listing missing schemas.

- [ ] **Step 3: Create schemas with closed objects and stable ID formats**

Every ID-bearing schema must use a conservative pattern such as:

```json
{"type":"string","pattern":"^[A-Z][A-Z0-9_-]{1,63}$"}
```

for governance IDs (`REQ-001`, `DR-004`, `CHG-0017`, `WP-000`), and lowercase kebab-case patterns for module/profile IDs. All root objects use `additionalProperties: false` except explicitly open maps such as `gates`/`metadata` whose values are themselves constrained.

- [ ] **Step 4: Encode terminal audit dispositions exactly**

`audit-disposition.schema.json` allows only:

```text
FIXED
ALREADY_FIXED
DEFERRED
NOT_APPLICABLE
REJECTED
```

`FIXED` and `ALREADY_FIXED` require non-empty `resolution_refs` and `verification_refs` using JSON Schema `if/then`.

- [ ] **Step 5: Run schema self-validation and inventory GREEN**

```bash
uv run pytest tests/schema -q
```

Expected: all pass.

- [ ] **Step 6: Commit**

```bash
git add schemas tests/schema
git commit -m "feat: define core workflow record schemas"
```

---

### Task 2: Implement source inventory, requirements, conflicts, and provenance normalization primitives

**Files:**
- Create: `src/project_finalizer/intake.py`
- Create: `src/project_finalizer/ids.py`
- Create: `tests/unit/test_ids.py`
- Create: `tests/unit/test_intake.py`
- Create: `core/intake/INPUT-INVENTORY.md`
- Create: `core/intake/REQUIREMENT-EXTRACTION.md`
- Create: `core/intake/CONFLICT-DETECTION.md`
- Create: `core/intake/ASSUMPTION-REGISTER.md`
- Create: `core/intake/UNKNOWN-DECISIONS.md`
- Create: `core/intake/LEGACY-CLASSIFICATION.md`

**Interfaces:**
- Consumes: `ProjectFS`, `SchemaRegistry`.
- Produces: `normalize_id`, `RequirementRecord`, `ConflictRecord`, `InputInventory`, `scan_inputs(root)`, `write_intake_bundle(...)`.

- [ ] **Step 1: Write failing logical-ID collision tests**

```python
# tests/unit/test_ids.py
import pytest

from project_finalizer.ids import assert_unique_ids


def test_casefold_equivalent_ids_are_duplicates():
    with pytest.raises(ValueError, match="duplicate logical identifier"):
        assert_unique_ids(["Users", "users"])


def test_unicode_normalized_equivalent_ids_are_duplicates():
    with pytest.raises(ValueError, match="duplicate logical identifier"):
        assert_unique_ids(["Café", "Cafe\u0301"])
```

- [ ] **Step 2: Write failing intake provenance test**

```python
# tests/unit/test_intake.py
from pathlib import Path

from project_finalizer.intake import scan_inputs


def test_scan_inputs_records_relative_path_size_and_sha256(tmp_path: Path):
    root = tmp_path / "input"
    root.mkdir()
    (root / "notes.md").write_text("hello")
    items = scan_inputs(root)
    assert len(items) == 1
    assert items[0].path == "notes.md"
    assert items[0].size == 5
    assert len(items[0].sha256) == 64
```

- [ ] **Step 3: Run RED**

```bash
uv run pytest tests/unit/test_ids.py tests/unit/test_intake.py -q
```

Expected: missing modules.

- [ ] **Step 4: Implement ID normalization**

Use `unicodedata.normalize("NFC", value).casefold()` only for collision comparison; preserve the original ID bytes for display/provenance.

- [ ] **Step 5: Implement deterministic input inventory**

`scan_inputs` recursively inventories regular files only, sorted by POSIX relative path. It rejects symlinks and any file resolving outside the input root. Record `path`, `size`, `sha256`, and media class inferred from suffix; do not parse document semantics in deterministic code.

- [ ] **Step 6: Implement requirement/conflict record dataclasses and writers**

Require each normalized requirement to retain source path plus a location string. Conflicts store all competing claims and stay unresolved until an explicit authority/decision step resolves them.

- [ ] **Step 7: Add the six normative intake guidance documents**

These documents must explicitly say Discovery Agent records claims and conflicts without choosing a winner; old timestamps do not automatically establish authority.

- [ ] **Step 8: Run GREEN and commit**

```bash
uv run pytest tests/unit/test_ids.py tests/unit/test_intake.py -q
task format:check
task lint
task typecheck
git add src/project_finalizer/intake.py src/project_finalizer/ids.py core/intake tests/unit
git commit -m "feat: add intake provenance primitives"
```

---

### Task 3: Implement lifecycle state store and gated transitions

**Files:**
- Create: `src/project_finalizer/state.py`
- Create: `core/lifecycle/PROJECT-STATE-MACHINE.md`
- Create: `core/lifecycle/PHASE-CONTRACTS.md`
- Create: `core/lifecycle/TRANSITION-GATES.md`
- Create: `core/lifecycle/FAILURE-RECOVERY.md`
- Create: `core/lifecycle/COMPLETION-DEFINITION.md`
- Create: `tests/unit/test_state.py`
- Create: `tests/integration/test_state_atomicity.py`
- Modify: `src/project_finalizer/commands/status.py`
- Replace foundation `transition` stub with real handler in `src/project_finalizer/commands/transition.py`

**Interfaces:**
- Consumes: `ProjectFS`, `SchemaRegistry`, `ExitCode`.
- Produces: `ProjectState`, `StateStore.load()`, `StateStore.initialize()`, `StateStore.transition(target, gate_results)`.

- [ ] **Step 1: Write failing legal/illegal transition tests**

```python
# tests/unit/test_state.py
import pytest

from project_finalizer.errors import ExitCode, WorkflowError
from project_finalizer.state import ProjectState, validate_transition


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
```

- [ ] **Step 2: Write failing atomicity test**

Monkeypatch the low-level serializer to raise before `os.replace`, call transition, then assert the persisted state file still contains the original state.

- [ ] **Step 3: Run RED**

```bash
uv run pytest tests/unit/test_state.py tests/integration/test_state_atomicity.py -q
```

Expected: missing `state` module.

- [ ] **Step 4: Implement the exact state order**

```python
LIFECYCLE = (
    "RAW_INPUT",
    "INTAKE_COMPLETE",
    "SOURCE_NORMALIZED",
    "CORE_SPEC_FROZEN",
    "MACHINE_CONTRACTS_READY",
    "AGENT_SPEC_READY",
    "WORK_PACKAGES_READY",
    "SENIOR_AUDITED",
    "CORRECTIVE_COMPLETE",
    "BUILD_READY",
    "FINAL_RELEASE",
)
```

`validate_transition` must use an explicit adjacency map, not `index + 1`, so future controlled branches remain possible.

- [ ] **Step 5: Implement StateStore with atomic persistence**

Persist `.workflow/project-state.yaml`. Initialize only when absent; refuse destructive reinitialization without a future explicit reset design.

- [ ] **Step 6: Replace CLI `transition`/`status` stubs**

`workflow transition TARGET --project PATH` loads gate evidence already recorded by validators; it cannot accept `--force`. `workflow status` displays current state and next legal action.

- [ ] **Step 7: Run GREEN and commit**

```bash
uv run pytest tests/unit/test_state.py tests/integration/test_state_atomicity.py tests/unit/test_cli_commands.py -q
git add src/project_finalizer/state.py src/project_finalizer/commands core/lifecycle tests
git commit -m "feat: enforce project lifecycle transitions"
```

---

### Task 4: Implement Decision Requests and immutable resolution workflow

**Files:**
- Create: `src/project_finalizer/decisions.py`
- Create: `core/governance/CONTROLLED-AUTONOMY.md`
- Create: `core/governance/STOP-CONDITIONS.md`
- Create: `core/governance/DECISION-REQUEST.template.md`
- Create: `core/governance/ADR.template.md`
- Create: `core/governance/CHANGE-CONTROL.md`
- Create: `core/governance/VERSIONING.md`
- Create: `core/governance/GENERATED-CODE-BOUNDARIES.md`
- Create: `src/project_finalizer/commands/decisions.py`
- Create: `tests/unit/test_decisions.py`
- Create: `tests/integration/test_decision_cli.py`

**Interfaces:**
- Consumes: `ProjectFS`, decision-request schema.
- Produces: `DecisionStore.create`, `list`, `show`, `resolve_choice`, `resolve_text` and CLI `workflow decisions ...`.

- [ ] **Step 1: Write failing immutability test**

```python
# tests/unit/test_decisions.py
from pathlib import Path

import pytest

from project_finalizer.decisions import DecisionStore
from project_finalizer.errors import WorkflowError
from project_finalizer.io import ProjectFS


def test_resolved_decision_cannot_be_changed(tmp_path: Path):
    fs = ProjectFS(tmp_path / "project")
    fs.root.mkdir()
    store = DecisionStore(fs)
    store.create("DR-001", subject="license", question="Choose license", options=("A", "B"))
    store.resolve_choice("DR-001", "A")
    with pytest.raises(WorkflowError, match="already resolved"):
        store.resolve_choice("DR-001", "B")
```

- [ ] **Step 2: Write failing protected-ambiguity contract test**

Create a helper `require_protected_decision(subject, evidence)` that creates/returns a pending DR and raises `WorkflowError(exit_code=HUMAN_DECISION_REQUIRED, code="PROTECTED_DECISION_REQUIRED")`; test exact exit code.

- [ ] **Step 3: Run RED**

```bash
uv run pytest tests/unit/test_decisions.py -q
```

- [ ] **Step 4: Implement decision storage layout**

Use:

```text
.workflow/decisions/pending/DR-xxxx.yaml
.workflow/decisions/resolved/DR-xxxx.yaml
```

Resolution moves the validated artifact atomically from pending to resolved and stores the original question/options plus the user's exact resolution text/choice and resolved timestamp.

- [ ] **Step 5: Implement list/show/resolve CLI handlers**

`resolve --choice` validates against declared options. `resolve --text` preserves exact user input in `resolution.original_text`.

- [ ] **Step 6: Run GREEN and commit**

```bash
uv run pytest tests/unit/test_decisions.py tests/integration/test_decision_cli.py -q
git add src/project_finalizer/decisions.py src/project_finalizer/commands/decisions.py core/governance tests
git commit -m "feat: add protected decision workflow"
```

---

### Task 5: Implement typed Authority Matrix and historical/advisory isolation

**Files:**
- Create: `src/project_finalizer/authority.py`
- Create: `core/authority/SOURCE-OF-TRUTH.md`
- Create: `core/authority/AUTHORITY-MATRIX.yaml`
- Create: `core/authority/PRECEDENCE-RULES.md`
- Create: `core/authority/HISTORICAL-DOC-POLICY.md`
- Create: `core/authority/GENERATED-ARTIFACT-POLICY.md`
- Create: `core/authority/CONFLICT-RESOLUTION.md`
- Create: `tests/unit/test_authority.py`

**Interfaces:**
- Consumes: authority-matrix schema, `ProjectFS`.
- Produces: `AuthorityMatrix.load`, `primary_for(subject_type)`, `assert_normative(path)`, `validate_claim(...)`.

- [ ] **Step 1: Write failing duplicate-primary and historical-leakage tests**

```python
# tests/unit/test_authority.py
import pytest

from project_finalizer.authority import AuthorityMatrix
from project_finalizer.errors import WorkflowError


def test_subject_rejects_two_primary_authorities():
    raw = {
        "subjects": {
            "http_wire_format": {
                "primary": ["contracts/openapi/a.yaml", "contracts/openapi/b.yaml"],
                "composition": "single",
            }
        }
    }
    with pytest.raises(WorkflowError, match="exactly one primary"):
        AuthorityMatrix.from_mapping(raw)


def test_historical_path_cannot_be_normative():
    matrix = AuthorityMatrix.from_mapping({"subjects": {}})
    with pytest.raises(WorkflowError, match="historical"):
        matrix.assert_normative("docs/audits/historical/old.md")
```

- [ ] **Step 2: Run RED**

```bash
uv run pytest tests/unit/test_authority.py -q
```

- [ ] **Step 3: Implement typed authority subject model**

Support `composition: single|composed` explicitly. `single` requires one primary. `composed` requires non-empty ordered authorities and explicit merge semantics; never infer composition.

- [ ] **Step 4: Seed generic authority template**

The root template must include generic subject classes (product behavior, machine contract shape, security invariants, implementation ordering, historical audit) without web-specific terms.

- [ ] **Step 5: Enforce advisory-only path policy**

Any path under `docs/audits/historical/**` or tagged `authority: advisory_only` cannot satisfy a required primary authority reference.

- [ ] **Step 6: Run GREEN and commit**

```bash
uv run pytest tests/unit/test_authority.py -q
git add src/project_finalizer/authority.py core/authority tests/unit/test_authority.py
git commit -m "feat: add typed authority model"
```

---

### Task 6: Implement artifact dependency graph and staleness engine

**Files:**
- Create: `src/project_finalizer/artifacts.py`
- Create: `tests/unit/test_artifacts.py`
- Create: `tests/integration/test_staleness.py`

**Interfaces:**
- Consumes: artifact schema, `ProjectFS.sha256`.
- Produces: `ArtifactRecord`, `ArtifactGraph`, `record_build`, `stale_artifacts`, `mark_downstream`.

- [ ] **Step 1: Write failing upstream-change test**

```python
# tests/unit/test_artifacts.py
from project_finalizer.artifacts import ArtifactGraph, ArtifactRecord


def test_changed_upstream_marks_dependent_stale():
    graph = ArtifactGraph(
        records=(
            ArtifactRecord("API_SEMANTICS", "docs/API.md", (), {}),
            ArtifactRecord(
                "OPENAPI",
                "contracts/openapi.yaml",
                ("API_SEMANTICS",),
                {"API_SEMANTICS": "oldhash"},
            ),
        )
    )
    assert graph.stale_artifacts({"API_SEMANTICS": "newhash"}) == ("OPENAPI",)
```

- [ ] **Step 2: Add missing-upstream and deleted-source tests**

A missing required source is stale with issue code `ARTIFACT_SOURCE_MISSING`, not “unchanged”. Downstream propagation must be transitive.

- [ ] **Step 3: Run RED**

```bash
uv run pytest tests/unit/test_artifacts.py tests/integration/test_staleness.py -q
```

- [ ] **Step 4: Implement deterministic DAG and staleness comparison**

Reject dependency cycles in the artifact graph. Record upstream hashes only after generated output exists and validates. Sort stale IDs for deterministic reports.

- [ ] **Step 5: Persist graph under `.workflow/artifacts.yaml` atomically**

A generated artifact's record stores `artifact_id`, `path`, `depends_on`, `built_from_hashes`, and `generated` boolean.

- [ ] **Step 6: Run GREEN and commit**

```bash
uv run pytest tests/unit/test_artifacts.py tests/integration/test_staleness.py -q
git add src/project_finalizer/artifacts.py tests
git commit -m "feat: detect stale derived artifacts"
```

---

### Task 7: Implement module ownership and cross-module interaction graph

**Files:**
- Create: `src/project_finalizer/modules.py`
- Create: `core/decomposition/MODULE-CLASSIFICATION.md`
- Create: `core/decomposition/MODULE-CONTRACT.template.md`
- Create: `core/decomposition/DEPENDENCY-RULES.md`
- Create: `core/decomposition/BOUNDARY-VALIDATION.md`
- Create: `core/contracts/CROSS-MODULE-INTERACTIONS.md`
- Create: `tests/unit/test_modules.py`

**Interfaces:**
- Consumes: module/ownership/interaction schemas.
- Produces: `ModuleCatalog`, `OwnershipIndex`, `InteractionCatalog`, dependency cycle detection.

- [ ] **Step 1: Write failing duplicate-owner and foreign-write tests**

```python
# tests/unit/test_modules.py
import pytest

from project_finalizer.modules import ModuleCatalog
from project_finalizer.errors import WorkflowError


def test_two_modules_cannot_own_same_table():
    raw = [
        {"id": "users", "owned_data": ["users"], "must_not_write": []},
        {"id": "billing", "owned_data": ["users"], "must_not_write": []},
    ]
    with pytest.raises(WorkflowError, match="duplicate owner"):
        ModuleCatalog.from_mappings(raw)


def test_declared_foreign_write_is_rejected():
    raw = [
        {"id": "users", "owned_data": ["users"], "must_not_write": []},
        {"id": "billing", "owned_data": ["invoices"], "writes": ["users"]},
    ]
    with pytest.raises(WorkflowError, match="foreign write"):
        ModuleCatalog.from_mappings(raw)
```

- [ ] **Step 2: Write failing interaction completeness test**

An interaction must declare one of `SYNC_QUERY`, `SYNC_COMMAND`, `SAME_REQUEST_ORCHESTRATION`, `DOMAIN_EVENT`, `BACKGROUND_JOB`, `OUTBOX_EVENT`, `EXTERNAL_WEBHOOK`, plus producer, consumer, transaction boundary, idempotency, timeout, and failure behavior.

- [ ] **Step 3: Run RED**

```bash
uv run pytest tests/unit/test_modules.py -q
```

- [ ] **Step 4: Implement catalog/index classes and deterministic cycle check**

Dependency cycles are rejected unless the design explicitly marks an edge as a non-module runtime dependency outside the module DAG. Do not silently break cycles.

- [ ] **Step 5: Add normative decomposition/interaction docs**

Document same-transaction vs eventual effects and explicitly prohibit synchronous API promises for foreign-module eventual writes unless a synchronous contract exists.

- [ ] **Step 6: Run GREEN and commit**

```bash
uv run pytest tests/unit/test_modules.py -q
git add src/project_finalizer/modules.py core/decomposition core/contracts tests/unit/test_modules.py
git commit -m "feat: enforce module ownership boundaries"
```

---

### Task 8: Implement work-package model, DAG validator, and deterministic compiler primitives

**Files:**
- Create: `src/project_finalizer/work_packages.py`
- Create: `core/work-packages/WORK-PACKAGE.template.md`
- Create: `core/work-packages/WP-STATE-MACHINE.md`
- Create: `core/work-packages/WP-COMPILER-RULES.md`
- Create: `core/work-packages/WP-ACCEPTANCE-CONTRACT.md`
- Create: `core/work-packages/WP-STOP-CONDITIONS.md`
- Create: `tests/unit/test_work_packages.py`

**Interfaces:**
- Consumes: module graph, command catalog, work-package schemas.
- Produces: `WorkPackage`, `WorkPackageGraph`, `topological_order`, `ready_packages`, `compile_wp_skeletons`.

- [ ] **Step 1: Write failing cycle/entrypoint/readiness tests**

```python
# tests/unit/test_work_packages.py
import pytest

from project_finalizer.work_packages import WorkPackageGraph
from project_finalizer.errors import WorkflowError


def test_wp_graph_rejects_cycle():
    with pytest.raises(WorkflowError, match="cycle"):
        WorkPackageGraph.from_edges({"WP-000": ("WP-001",), "WP-001": ("WP-000",)})


def test_wp_graph_requires_wp000_entrypoint():
    with pytest.raises(WorkflowError, match="WP-000"):
        WorkPackageGraph.from_edges({"WP-001": ()})
```

- [ ] **Step 2: Add scope/acceptance contract tests**

A READY WP must have non-empty purpose, authority refs, allowed paths, acceptance commands/evidence, and stop conditions when touching protected surfaces.

- [ ] **Step 3: Run RED**

```bash
uv run pytest tests/unit/test_work_packages.py -q
```

- [ ] **Step 4: Implement graph and compiler primitives**

Use Kahn topological sort with lexicographically sorted queues for deterministic order. `compile_wp_skeletons` derives dependency skeletons from module dependencies but never invents protected implementation decisions; unresolved protected edges produce DR requirements.

- [ ] **Step 5: Run GREEN and commit**

```bash
uv run pytest tests/unit/test_work_packages.py -q
git add src/project_finalizer/work_packages.py core/work-packages tests/unit/test_work_packages.py
git commit -m "feat: add work package DAG engine"
```

---

### Task 9: Implement run ledger, partial-output trust model, and corrective change transactions

**Files:**
- Create: `src/project_finalizer/runs.py`
- Create: `src/project_finalizer/changes.py`
- Create: `src/project_finalizer/commands/change.py`
- Create: `tests/unit/test_runs.py`
- Create: `tests/unit/test_changes.py`
- Create: `tests/integration/test_partial_run_recovery.py`

**Interfaces:**
- Consumes: run-record/change-transaction schemas, ArtifactGraph.
- Produces: `RunLedger.start/complete/fail`, `ChangeStore.begin/validate/close`, CLI `workflow change ...`.

- [ ] **Step 1: Write failing partial-run trust test**

A started run with output files present but no validated completion record must classify outputs as `UNTRUSTED_PARTIAL`; tests assert those outputs cannot be registered as authority/artifact sources.

- [ ] **Step 2: Write failing change-close staleness test**

Begin `CHG-0017`, mark an affected downstream artifact stale, call close, and assert `ExitCode.STALE_ARTIFACTS`.

- [ ] **Step 3: Run RED**

```bash
uv run pytest tests/unit/test_runs.py tests/unit/test_changes.py tests/integration/test_partial_run_recovery.py -q
```

- [ ] **Step 4: Implement ledger records without chain-of-thought fields**

Allowed fields: run ID, agent role, timestamps, input path/hash pairs, output path/hash pairs, rulings, validator result summaries, decision IDs, status.

- [ ] **Step 5: Implement change transaction lifecycle**

`OPEN -> VALIDATED -> CLOSED`. `close` requires all affected downstream artifacts current and required validators green. No `--force` path exists.

- [ ] **Step 6: Replace CLI change stub and run GREEN**

```bash
uv run pytest tests/unit/test_runs.py tests/unit/test_changes.py tests/integration/test_partial_run_recovery.py tests/unit/test_cli_commands.py -q
```

- [ ] **Step 7: Run Core Engine verification gate**

```bash
task format:check
task lint
task typecheck
task test
git diff --check
```

Expected: all pass.

- [ ] **Step 8: Commit**

```bash
git add src/project_finalizer/runs.py src/project_finalizer/changes.py src/project_finalizer/commands/change.py tests
git commit -m "feat: add run recovery and corrective transactions"
```

---

### Task 10: Implement project initialization, dry-run inspection, and phase artifact contracts

**Files:**
- Create: `src/project_finalizer/project.py`
- Create: `src/project_finalizer/phases.py`
- Create: `src/project_finalizer/commands/init.py`
- Create: `src/project_finalizer/commands/inspect.py`
- Create: `src/project_finalizer/commands/audit_input.py`
- Create: `tests/integration/test_project_init.py`
- Create: `tests/integration/test_audit_input_dry_run.py`

**Interfaces:**
- Consumes: `ProjectFS`, manifests, intake scanner, StateStore.
- Produces: `.workflow/project.yaml`, initialized RAW_INPUT state, non-mutating dry-run inspection, `PhaseContract` registry.

- [ ] **Step 1: Write failing initialization test**

```python
# tests/integration/test_project_init.py
from pathlib import Path

from project_finalizer.cli import main


def test_init_creates_project_metadata_and_raw_state(tmp_path: Path):
    root = tmp_path / "project"
    root.mkdir()
    code = main(["init", str(root), "--profile", "web-saas"])
    assert code == 0
    assert (root / ".workflow/project.yaml").exists()
    assert "RAW_INPUT" in (root / ".workflow/project-state.yaml").read_text()
```

- [ ] **Step 2: Write failing dry-run immutability test**

Hash every file below the project root, run `workflow audit-input --dry-run --project ROOT`, hash again, and assert byte-identical tree. Output must list missing artifact classes, discovered conflicts if machine-detectable, estimated phases, likely protected-decision categories, and proposed profile capability states without creating canonical project files.

- [ ] **Step 3: Run RED**

```bash
uv run pytest tests/integration/test_project_init.py tests/integration/test_audit_input_dry_run.py -q
```

- [ ] **Step 4: Implement project metadata and `init`**

`project.yaml` records project ID/name, workflow/core/profile versions, input root, current selected profile, and capability resolution location. Refuse initialization if `.workflow` already exists unless it is a valid initialized project; there is no destructive overwrite flag in V2.

- [ ] **Step 5: Implement phase contracts**

Create a registry mapping lifecycle states to required role/artifact outputs. Each phase contract declares required canonical outputs, schemas, validator layers, next state, and whether a human decision may block it.

- [ ] **Step 6: Implement `inspect` and `audit-input --dry-run` as read-only commands**

`inspect` reports project metadata, current state, active profile, pending decisions, stale artifacts, and next action. Dry-run never calls state transition or artifact writers.

- [ ] **Step 7: Run GREEN and commit**

```bash
uv run pytest tests/integration/test_project_init.py tests/integration/test_audit_input_dry_run.py -q
git add src/project_finalizer/project.py src/project_finalizer/phases.py src/project_finalizer/commands tests/integration
git commit -m "feat: initialize and inspect workflow projects"
```

---

### Task 11: Replace remaining phase stubs with role-output validation, resume, and finalize orchestration

**Files:**
- Create: `src/project_finalizer/orchestrator.py`
- Create: `src/project_finalizer/commands/phases.py`
- Create: `src/project_finalizer/commands/resume.py`
- Create: `src/project_finalizer/commands/finalize.py`
- Modify: `src/project_finalizer/cli.py`
- Create: `tests/integration/test_phase_commands.py`
- Create: `tests/integration/test_finalize_orchestration.py`

**Interfaces:**
- Consumes: PhaseContract registry, StateStore, DecisionStore, RunLedger, validators.
- Produces: real handlers for `discover`, `normalize`, `resolve`, `spec`, `architecture`, `contracts`, `agent-spec`, `wp`, `audit`, `correct`, `resume`, `finalize`.

- [ ] **Step 1: Write failing missing-role-output test**

For an initialized RAW_INPUT project, run `workflow discover`. It must not return success. It must write/refresh a deterministic role packet under `.workflow/role-packets/discovery/` and return exit `30` with code `AGENT_ROLE_OUTPUT_REQUIRED`, naming the exact expected output contract paths.

- [ ] **Step 2: Write failing valid-role-output transition test**

Seed schema-valid Discovery Agent outputs under the phase contract output paths, rerun `workflow discover`, assert relevant validators run and state transitions to `INTAKE_COMPLETE` only after success.

- [ ] **Step 3: Write failing pending-human-decision finalize test**

With a protected pending DR, `workflow finalize` must stop with exit `20`, print the pending DR IDs, and not advance state.

- [ ] **Step 4: Write failing next-agent-action finalize test**

Without pending human decisions but with missing next phase role output, `workflow finalize` returns exit `30` / `AGENT_ROLE_OUTPUT_REQUIRED` and creates the role packet. It must never return `0` while the project is short of `FINAL_RELEASE`.

- [ ] **Step 5: Run RED**

```bash
uv run pytest tests/integration/test_phase_commands.py tests/integration/test_finalize_orchestration.py -q
```

- [ ] **Step 6: Implement provider-agnostic role-output protocol**

V2.0.0 does not invoke proprietary AI APIs. A phase command prepares a complete role packet, validates externally/agent-authored output at fixed paths, records a run ledger entry, and transitions only after validation. This makes the workflow usable inside Codex/Claude/Gemini sessions without binding the deterministic core to a provider SDK.

- [ ] **Step 7: Implement all phase handlers from one generic phase runner**

Each public phase command calls `run_phase(phase_id, project_root)`; do not duplicate state/validation logic per command. `resolve` verifies required conflicts/DRs are terminal before `SOURCE_NORMALIZED`; `correct` verifies change transactions and audit dispositions; `audit` enforces Senior Auditor output contract; `wp` validates DAG/WP-000.

- [ ] **Step 8: Implement `resume` and `finalize`**

`resume` is an alias for “inspect current state and run exactly the current phase once.” `finalize` repeatedly executes deterministic no-AI steps only; it stops at the first required AgentRoleAction or HumanDecisionAction with a non-zero stable exit, preserving truthful completion semantics.

- [ ] **Step 9: Run GREEN and all CLI command tests**

```bash
uv run pytest tests/integration/test_phase_commands.py tests/integration/test_finalize_orchestration.py tests/unit/test_cli_commands.py -q
```

- [ ] **Step 10: Commit**

```bash
git add src/project_finalizer/orchestrator.py src/project_finalizer/commands src/project_finalizer/cli.py tests/integration
git commit -m "feat: orchestrate workflow phases safely"
```

---

## Core Engine completion evidence

Record:

```text
Core schema inventory: PASS
Input provenance: PASS
Conflict records preserve competing claims: PASS
Lifecycle transitions: PASS
Protected decisions: PASS
Typed authority: PASS
Historical authority leakage blocked: PASS
Staleness propagation: PASS
Module ownership/cycles: PASS
WP DAG and WP-000 entrypoint: PASS
Partial run outputs trusted automatically: NO
Change transaction closes with stale artifacts: NO
```
