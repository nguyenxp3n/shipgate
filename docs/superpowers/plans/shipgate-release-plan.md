# AI Project Finalization Workflow V2 Evidence and Final Release Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Prove V2.0.0 works as designed by adding a realistic positive example, adversarial negative fixtures, regression lessons from HCN Learning, role-evaluation fixtures, self-hosting checks, CI, generated QA evidence, and the final reproducible release archive.

**Architecture:** Treat examples and fixtures as executable specifications. Positive fixtures must pass the intended static pipeline; each negative fixture declares its expected issue/exit class and fails for exactly that reason. Final release assembly runs only after all test classes and self-hosting checks are green, and it truthfully records review/runtime assurance limits.

**Tech Stack:** Existing workflow CLI/runtime; pytest; Taskfile; GitHub Actions-compatible CI YAML; deterministic release compiler from Validation/Release Plan.

**Spec:** `docs/superpowers/specs/shipgate-architecture-spec.md`

## Global Constraints

- TeamNotes is the canonical positive example and must be non-trivial: users, organizations, notes, sharing, auth/RBAC, PostgreSQL semantics, email invite, background notification job, admin, audit log, deployment, and backup.
- TeamNotes intentionally excludes payments and AI to keep the base positive example focused.
- Negative fixtures must fail for declared stable issue classes, not merely “non-zero”.
- HCN regression fixtures encode classes of workflow defects only; they must not copy HCN domain/product content into the generic workflow.
- Role evaluations test observable output-contract behavior and forbidden actions, not private reasoning.
- Self-hosting applies Generic Core rules that are relevant to this CLI/tooling repository; `web-saas` requirements do not apply to the workflow repository itself.
- Final release cannot proceed until the repository license Decision Request is resolved by the user.
- Final ZIP and `.zip.sha256` are separate artifacts; the archive digest is never embedded inside the archive.
- QA reports must disclose whether independent review and real provider-runtime integration were actually performed.

## Review Focus

- Negative fixtures must not pass because a different earlier error masks the intended error class; fixture tests must assert the expected code is present.
- Positive example must not pass by disabling mandatory capabilities or omitting the surfaces it claims to exercise.
- Self-hosting must not accidentally treat generated QA output as a canonical authority source.
- CI must run the same Taskfile gateway as local QA rather than duplicating divergent shell logic.
- Final staging/re-extract verification must run from a fresh directory so tests cannot pass because source-tree caches or generated leftovers are reused.

---

### Task 1: Build TeamNotes raw input and expected normalized/core project assets

**Files:**
- Create: `examples/teamnotes/raw-input/product-notes.md`
- Create: `examples/teamnotes/raw-input/api-notes.md`
- Create: `examples/teamnotes/raw-input/data-notes.md`
- Create: `examples/teamnotes/raw-input/security-notes.md`
- Create: `examples/teamnotes/raw-input/operations-notes.md`
- Create: `examples/teamnotes/expected-normalized/requirements.yaml`
- Create: `examples/teamnotes/expected-normalized/conflicts.yaml`
- Create: `examples/teamnotes/expected-core-spec/PRODUCT-SPEC.md`
- Create: `examples/teamnotes/expected-core-spec/DOMAIN-MODEL.md`
- Create: `examples/teamnotes/expected-core-spec/TECHNICAL-SPEC.md`
- Create: `examples/teamnotes/expected-core-spec/DATA-MODEL.md`
- Create: `examples/teamnotes/expected-core-spec/SECURITY.md`
- Create: `examples/teamnotes/expected-core-spec/DEPLOYMENT.md`
- Create: `tests/examples/test_teamnotes_intake.py`

**Interfaces:**
- Consumes: intake/provenance schemas and static role contracts.
- Produces: a complete positive example input and canonical expected semantics.

- [ ] **Step 1: Write failing TeamNotes inventory/provenance test**

```python
# tests/examples/test_teamnotes_intake.py
from project_finalizer.intake import scan_inputs


def test_teamnotes_raw_input_has_multiple_source_classes(repo_root):
    items = scan_inputs(repo_root / "examples/teamnotes/raw-input")
    assert {item.path for item in items} >= {
        "product-notes.md", "api-notes.md", "data-notes.md",
        "security-notes.md", "operations-notes.md",
    }
```

- [ ] **Step 2: Run RED**

```bash
uv run pytest tests/examples/test_teamnotes_intake.py -q
```

Expected: missing example files.

- [ ] **Step 3: Author raw input with one intentional resolvable conflict**

Include a small conflict such as email invitation expiry described differently in two notes, then resolve it explicitly in expected canonical spec through a recorded decision artifact rather than silently choosing. This proves conflict/decision machinery.

- [ ] **Step 4: Author expected normalized/core artifacts with provenance refs**

Every major requirement in `requirements.yaml` must include source path/location refs. `conflicts.yaml` retains both claims plus resolution reference.

- [ ] **Step 5: Run GREEN and commit**

```bash
uv run pytest tests/examples/test_teamnotes_intake.py -q
git add examples/teamnotes tests/examples/test_teamnotes_intake.py
git commit -m "test: add TeamNotes source and core example"
```

---

### Task 2: Complete TeamNotes contracts, agent spec, work packages, audit, corrective, and final expected tree

**Files:**
- Create: `examples/teamnotes/expected-contracts/openapi.yaml`
- Create: `examples/teamnotes/expected-contracts/error-catalog.yaml`
- Create: `examples/teamnotes/expected-contracts/events/*.schema.json`
- Create: `examples/teamnotes/expected-agent-spec/AGENT-OPERATING-MANUAL.md`
- Create: `examples/teamnotes/expected-agent-spec/AUTHORITY-MATRIX.yaml`
- Create: `examples/teamnotes/expected-agent-spec/modules/*.yaml`
- Create: `examples/teamnotes/expected-work-packages/WP-000.md`
- Create: `examples/teamnotes/expected-work-packages/WP-001.md` through dependency-appropriate final WP files
- Create: `examples/teamnotes/expected-work-packages/graph.yaml`
- Create: `examples/teamnotes/expected-audit/findings.yaml`
- Create: `examples/teamnotes/expected-corrective/dispositions.yaml`
- Create: `examples/teamnotes/expected-final/SPEC-MANIFEST.yaml`
- Create: `examples/teamnotes/expected-final/QA-BUILD-READINESS.md`
- Create: `tests/examples/test_teamnotes_pipeline.py`

**Interfaces:**
- Consumes: all Generic Core and web-saas validators.
- Produces: positive pipeline fixture expected to validate to BUILD_READY.

- [ ] **Step 1: Write failing positive-pipeline test**

```python
# tests/examples/test_teamnotes_pipeline.py
from project_finalizer.testing import validate_example_project


def test_teamnotes_positive_static_pipeline(repo_root):
    result = validate_example_project(repo_root / "examples/teamnotes")
    assert result.ok, result.format_issues()
    assert result.build_readiness == "PASS"
```

- [ ] **Step 2: Run RED**

```bash
uv run pytest tests/examples/test_teamnotes_pipeline.py -q
```

- [ ] **Step 3: Author machine contracts and module ownership**

TeamNotes modules at minimum: `auth`, `users`, `organizations`, `notes`, `sharing`, `notifications`, `admin`, `audit`. Define table owners and interactions so no module directly writes another module's data. Email invite/notification delivery is eventual and idempotent.

- [ ] **Step 4: Author WP DAG**

Include `WP-000` repository bootstrap, then toolchain/config/database/API/auth/users-orgs/notes-sharing/notifications/admin-audit/observability/security/E2E/deployment/readiness packages in a valid dependency graph. Each WP includes allowed paths, authority refs, acceptance commands/evidence, and stop conditions.

- [ ] **Step 5: Add one senior-audit finding plus corrective closure**

Use a medium-severity synthetic inconsistency in pre-corrective example data; terminal disposition references corrected canonical artifact and verification. Final expected tree must have zero open Critical/High.

- [ ] **Step 6: Implement `project_finalizer.testing.validate_example_project` as a thin orchestration helper**

It loads the example's expected final project structure and runs the same validator registry/readiness logic used by real projects; no example-only bypasses.

- [ ] **Step 7: Run GREEN and commit**

```bash
uv run pytest tests/examples/test_teamnotes_pipeline.py -q
git add examples/teamnotes src/project_finalizer/testing.py tests/examples/test_teamnotes_pipeline.py
git commit -m "test: prove TeamNotes build-ready pipeline"
```

---

### Task 3: Add negative fixtures with exact expected failure classes

**Files:**
- Create under `fixtures/invalid/`:
  - `duplicate-authority/`
  - `cyclic-wp/`
  - `foreign-table-write/`
  - `open-audit-finding/`
  - `stale-openapi/`
  - `missing-authz/`
  - `tenant-table-without-tenant-key/`
  - `orphan-event-consumer/`
  - `adapter-overrides-core/`
  - `bad-release-hash/`
  - `unsafe-symlink/`
  - `cookie-auth-without-csrf/`
- Create: `fixtures/invalid/EXPECTATIONS.yaml`
- Create: `tests/fixtures/test_invalid_projects.py`

**Interfaces:**
- Consumes: full validator stack.
- Produces: executable adversarial fixture catalog.

- [ ] **Step 1: Write failing parameterized expectation test**

```python
# tests/fixtures/test_invalid_projects.py
import pytest

from project_finalizer.testing import validate_invalid_fixture


@pytest.mark.parametrize("fixture,expected_code", [
    ("duplicate-authority", "AUTH_DUPLICATE_PRIMARY"),
    ("cyclic-wp", "WP_CYCLE"),
    ("foreign-table-write", "OWN_FOREIGN_WRITE"),
    ("open-audit-finding", "AUDIT_HIGH_OPEN"),
    ("stale-openapi", "ARTIFACT_STALE"),
    ("missing-authz", "API_AUTH_METADATA_MISSING"),
    ("tenant-table-without-tenant-key", "WS_DB_TENANT_KEY_REQUIRED"),
    ("orphan-event-consumer", "OWN_EVENT_SCHEMA_MISSING"),
    ("adapter-overrides-core", "ADAPTER_NONCANONICAL_TRUTH"),
    ("bad-release-hash", "RELEASE_HASH_MISMATCH"),
    ("unsafe-symlink", "RELEASE_UNSAFE_SYMLINK"),
    ("cookie-auth-without-csrf", "WS_AUTH_CSRF_REQUIRED"),
])
def test_invalid_fixture_fails_for_expected_reason(repo_root, fixture, expected_code):
    result = validate_invalid_fixture(repo_root / "fixtures/invalid" / fixture)
    assert result.ok is False
    assert expected_code in result.issue_codes
```

- [ ] **Step 2: Run RED**

```bash
uv run pytest tests/fixtures/test_invalid_projects.py -q
```

Expected: missing fixtures/helper behavior.

- [ ] **Step 3: Build each fixture minimally**

Each fixture contains only enough valid surrounding structure to reach the intended failure. Avoid earlier syntax errors that mask the target issue.

- [ ] **Step 4: Implement expectation helper**

`validate_invalid_fixture` runs the same validator stack and returns all issue codes; it does not stop at the first ordinary validation issue.

- [ ] **Step 5: Run GREEN and commit**

```bash
uv run pytest tests/fixtures/test_invalid_projects.py -q
git add fixtures/invalid src/project_finalizer/testing.py tests/fixtures/test_invalid_projects.py
git commit -m "test: add adversarial validation fixtures"
```

---

### Task 4: Encode HCN-derived workflow regression lessons without domain leakage

**Files:**
- Create under `fixtures/regression/hcn-learning-lessons/`:
  - `flat-precedence-bug/`
  - `async-api-contradiction/`
  - `foreign-owner-write/`
  - `missing-outbox-inbox/`
  - `event-schema-drift/`
  - `timeout-arithmetic/`
  - `wp-gate-timing/`
  - `historical-audit-authority/`
- Create: `fixtures/regression/hcn-learning-lessons/README.md`
- Create: `tests/fixtures/test_hcn_regression_lessons.py`

**Interfaces:**
- Consumes: generic validators/profile validators as applicable.
- Produces: regression tests for defect classes discovered during HCN documentation work.

- [ ] **Step 1: Write failing regression parameterization**

Each fixture declares `expected_codes` in local metadata; test asserts all expected codes appear.

- [ ] **Step 2: Run RED**

```bash
uv run pytest tests/fixtures/test_hcn_regression_lessons.py -q
```

- [ ] **Step 3: Create genericized fixtures**

Use neutral names like `accounts`, `rewards`, `progress`, `worker`; do not copy HCN-specific roadmap/curriculum/mastery domain content. Preserve only structural defect patterns.

- [ ] **Step 4: For timeout arithmetic, implement a deterministic feasibility validator if not already present**

Represent overall timeout and per-case/count limits in a generic resource-budget record; fail when declared maximum per-case workload cannot fit the stated overall limit plus compile/setup overhead. Keep it capability-driven and non-runner-specific.

- [ ] **Step 5: Run GREEN and commit**

```bash
uv run pytest tests/fixtures/test_hcn_regression_lessons.py -q
git add fixtures/regression tests/fixtures/test_hcn_regression_lessons.py src/project_finalizer
git commit -m "test: preserve workflow regression lessons"
```

---

### Task 5: Add observable AI role evaluations

**Files:**
- Create: `fixtures/role-evals/discovery-conflict/`
- Create: `fixtures/role-evals/protected-decision/`
- Create: `fixtures/role-evals/senior-auditor-write-boundary/`
- Create: `fixtures/role-evals/contract-compiler-invention/`
- Create: `fixtures/role-evals/readiness-protected-guess/`
- Create: `src/project_finalizer/agents/eval.py`
- Create: `tests/agents/test_role_evals.py`

**Interfaces:**
- Consumes: role packets and candidate role-output files.
- Produces: `evaluate_role_output(role_id, packet, output) -> ValidationReport`.

- [ ] **Step 1: Write failing discovery-conflict eval**

Candidate output that chooses a conflict winner without authority/decision must fail with `ROLE_DISCOVERY_CHOSE_WINNER`.

- [ ] **Step 2: Write failing senior-auditor mutation eval**

Candidate output manifest that declares a canonical OpenAPI write by Senior Auditor fails with `ROLE_WRITE_BOUNDARY_VIOLATION`.

- [ ] **Step 3: Run RED**

```bash
uv run pytest tests/agents/test_role_evals.py -q
```

- [ ] **Step 4: Implement eval rules against observable outputs only**

Do not attempt to inspect or store private reasoning. Evaluate output schema adherence, provenance retention, created Decision Requests, declared write paths, and unsupported additions.

- [ ] **Step 5: Run GREEN and commit**

```bash
uv run pytest tests/agents/test_role_evals.py -q
git add fixtures/role-evals src/project_finalizer/agents/eval.py tests/agents
git commit -m "test: evaluate agent role contract behavior"
```

---

### Task 6: Implement self-hosting validation for this workflow repository

**Files:**
- Create: `self-hosting/project.yaml`
- Create: `self-hosting/AUTHORITY-MATRIX.yaml`
- Create: `self-hosting/modules/*.yaml`
- Create: `self-hosting/work-packages/graph.yaml`
- Create: `self-hosting/audit/findings.yaml`
- Create: `self-hosting/audit/dispositions.yaml`
- Create: `tests/self_hosting/test_self_hosting.py`

**Interfaces:**
- Consumes: applicable Generic Core validators.
- Produces: proof that the workflow repository can describe/validate itself without pretending to be a web-saas app.

- [ ] **Step 1: Write failing self-hosting test**

```python
# tests/self_hosting/test_self_hosting.py
from project_finalizer.testing import validate_self_hosting


def test_workflow_repo_passes_applicable_generic_core_rules(repo_root):
    result = validate_self_hosting(repo_root)
    assert result.ok, result.format_issues()
```

- [ ] **Step 2: Run RED**

```bash
uv run pytest tests/self_hosting/test_self_hosting.py -q
```

- [ ] **Step 3: Model workflow repository modules**

At minimum: `cli`, `core-engine`, `validators`, `profiles`, `agents-adapters`, `release`. Authority matrix points to approved design, schemas, code/toolchain, and QA evidence by subject; generated QA output remains derived evidence, not canonical architecture authority.

- [ ] **Step 4: Run GREEN and commit**

```bash
uv run pytest tests/self_hosting/test_self_hosting.py -q
git add self-hosting tests/self_hosting src/project_finalizer/testing.py
git commit -m "test: add workflow self-hosting validation"
```

---

### Task 7: Add CI contract and finish Taskfile QA/release wiring

**Files:**
- Create: `.github/workflows/ci.yml`
- Modify: `Taskfile.yml`
- Create: `tests/unit/test_taskfile_contract.py`
- Create: `tests/unit/test_ci_contract.py`

**Interfaces:**
- Consumes: existing Taskfile commands.
- Produces: CI that calls the same gateway used locally.

- [ ] **Step 1: Write failing Taskfile command inventory test**

Parse YAML and assert all required tasks from design Section 41 exist. Assert `qa` delegates to `format:check`, `lint`, `typecheck`, and `test`; `release` invokes workflow release logic rather than duplicating archive shell commands.

- [ ] **Step 2: Write failing CI gateway test**

Parse `.github/workflows/ci.yml`; assert job steps invoke `task format:check`, `task lint`, `task typecheck`, `task test`, `task test:fixtures`, and a release dry-run/gate. Reject duplicated direct pytest/mypy/ruff command lines in CI after Taskfile exists.

- [ ] **Step 3: Run RED**

```bash
uv run pytest tests/unit/test_taskfile_contract.py tests/unit/test_ci_contract.py -q
```

- [ ] **Step 4: Implement CI and Taskfile integration**

CI installs uv and go-task, runs `task setup`, then Taskfile gates. Automatic publishing remains absent.

- [ ] **Step 5: Run GREEN and commit**

```bash
uv run pytest tests/unit/test_taskfile_contract.py tests/unit/test_ci_contract.py -q
git add .github/workflows/ci.yml Taskfile.yml tests/unit
git commit -m "ci: enforce workflow quality gateway"
```

---

### Task 8: Complete the workflow release-package root inventory and self-describing manifests

**Files:**
- Create: `CHANGELOG.md`
- Create: `VERSION`
- Create: `AGENTS.md`
- Create: `CLAUDE.md`
- Create: `GEMINI.md`
- Create: `core/README.md`
- Create: `core/CORE-MANIFEST.yaml`
- Create: `validators/README.md`
- Create: `generators/README.md`
- Create: `cli/README.md`
- Create: `release/README.md`
- Create: `release/RELEASE-POLICY.md`
- Create: `tests/release/test_package_blueprint.py`

**Interfaces:**
- Consumes: approved package blueprint, executable module locations, adapter bootstrap rules.
- Produces: the exact top-level package shape promised by the design while keeping executable Python under `src/project_finalizer/`.

- [ ] **Step 1: Write failing package-blueprint test**

```python
# tests/release/test_package_blueprint.py
REQUIRED_ROOT = {
    "START-HERE.md", "README.md", "CHANGELOG.md", "VERSION",
    "AGENTS.md", "CLAUDE.md", "GEMINI.md", "Taskfile.yml", "pyproject.toml",
    "uv.lock", "WORKFLOW-MANIFEST.yaml", "core", "profiles", "adapters",
    "schemas", "prompts", "validators", "generators", "cli", "tests",
    "examples", "docs", "fixtures", "release",
}


def test_release_source_tree_matches_blueprint(repo_root):
    assert REQUIRED_ROOT <= {p.name for p in repo_root.iterdir()}
    assert (repo_root / "VERSION").read_text().strip() == "2.0.0"
```

- [ ] **Step 2: Run RED**

```bash
uv run pytest tests/release/test_package_blueprint.py -q
```

- [ ] **Step 3: Create root workflow bootstrap files**

Root `AGENTS.md`, `CLAUDE.md`, and `GEMINI.md` are for contributors/agents working on the workflow repository itself. Each points to the approved design, master implementation plan, Taskfile command gateway, and applicable self-hosting authority. They must not duplicate target-project business rules.

- [ ] **Step 4: Create Core/package inventory documents**

`core/CORE-MANIFEST.yaml` indexes all Generic Core normative assets by category and version. Root `validators/`, `generators/`, and `cli/` directories contain concise human-facing architecture/inventory READMEs pointing to the executable code under `src/project_finalizer/`; they are not duplicate implementations.

- [ ] **Step 5: Create release policy and changelog/version**

`CHANGELOG.md` records the V2.0.0 initial release scope. `release/RELEASE-POLICY.md` records staging exclusions, sidecar rule, assurance wording, and fresh re-extract requirement.

- [ ] **Step 6: Run GREEN and commit**

```bash
uv run pytest tests/release/test_package_blueprint.py -q
git add CHANGELOG.md VERSION AGENTS.md CLAUDE.md GEMINI.md core/CORE-MANIFEST.yaml core/README.md validators generators cli release tests/release/test_package_blueprint.py
git commit -m "docs: complete workflow package blueprint"
```

---

### Task 9: Resolve license decision before release content is frozen

**Files:**
- Create during execution after human resolution: `docs/decisions/DR-WF-001-license.yaml`
- Create after resolution: `LICENSE`
- Create: `tests/release/test_license_gate.py`

**Interfaces:**
- Consumes: human-provided license decision.
- Produces: immutable decision artifact and release license file.

- [ ] **Step 1: Write failing release-gate test before asking for the decision**

The test asserts final release preflight fails with `HUMAN_DECISION_REQUIRED` / `RELEASE_LICENSE_DECISION_REQUIRED` while no resolved `DR-WF-001` exists.

- [ ] **Step 2: Run RED and confirm the intended blocker**

```bash
uv run pytest tests/release/test_license_gate.py -q
```

Expected: release preflight is blocked specifically by license decision.

- [ ] **Step 3: Ask the human partner for the license choice at execution time**

Do not infer a license from project style or prior projects. Record the exact human resolution in `DR-WF-001-license.yaml`.

- [ ] **Step 4: Create the corresponding `LICENSE` file and make the test GREEN**

Run:

```bash
uv run pytest tests/release/test_license_gate.py -q
```

Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add docs/decisions/DR-WF-001-license.yaml LICENSE tests/release/test_license_gate.py
git commit -m "docs: record workflow license decision"
```

---

### Task 10: Generate final QA evidence and acceptance-matrix traceability

**Files:**
- Create: `src/project_finalizer/generators/qa_reports.py`
- Create generated-at-release templates/outputs:
  - `QA-CORE-ARCHITECTURE.md`
  - `QA-WEB-SAAS-PROFILE.md`
  - `QA-VALIDATORS.md`
  - `QA-AGENT-ROLE-CONTRACTS.md`
  - `QA-EXAMPLE-PROJECT.md`
  - `QA-RELEASE-INTEGRITY.md`
  - `QA-BUILD-READINESS.md`
- Create: `docs/ACCEPTANCE-TRACEABILITY.yaml`
- Create: `tests/release/test_qa_evidence.py`

**Interfaces:**
- Consumes: test/validator/release evidence, approved design Final Acceptance Matrix.
- Produces: QA reports and row-by-row traceability.

- [ ] **Step 1: Write failing traceability completeness test**

Encode the 18 acceptance areas from design Section 56 as IDs and assert each has at least one automated evidence reference plus report destination.

- [ ] **Step 2: Write assurance truthfulness test**

If no independent reviewer evidence artifact exists, generated QA must say `Independent senior review: NOT PERFORMED`. If no provider-runtime integration test exists, state `AI-provider execution integration: NOT PERFORMED`.

- [ ] **Step 3: Run RED**

```bash
uv run pytest tests/release/test_qa_evidence.py -q
```

- [ ] **Step 4: Implement QA generator**

Generate reports from machine evidence, not hand-edited PASS prose. Every PASS claim must include command/test evidence or validator result summary.

- [ ] **Step 5: Run GREEN and commit**

```bash
uv run pytest tests/release/test_qa_evidence.py -q
git add src/project_finalizer/generators/qa_reports.py docs/ACCEPTANCE-TRACEABILITY.yaml tests/release/test_qa_evidence.py
git commit -m "feat: generate evidence-backed QA reports"
```

---

### Task 11: Final whole-repository verification and release assembly

**Files:**
- Modify as required only by verified failures found in this task; any code fix requires its own regression test before modification.
- Generate: `SHA256SUMS.txt`
- Generate: `/mnt/data/ai-project-finalization-workflow-v2.0.0.zip`
- Generate: `/mnt/data/ai-project-finalization-workflow-v2.0.0.zip.sha256`

**Interfaces:**
- Consumes: entire implementation.
- Produces: final V2.0.0 ZIP and sidecar.

- [ ] **Step 1: Run full static QA from a clean working tree**

```bash
task format:check
task lint
task typecheck
task test
task test:fixtures
task test:release
task qa
git diff --check
```

Expected: all exit `0`.

- [ ] **Step 2: Run focused evidence suites explicitly**

```bash
uv run pytest tests/examples -q
uv run pytest tests/fixtures -q
uv run pytest tests/agents -q
uv run pytest tests/self_hosting -q
uv run pytest tests/release -q
```

Expected: all pass.

- [ ] **Step 3: Run `workflow validate` against self-hosting and TeamNotes**

Expected: both applicable positive targets PASS; TeamNotes readiness exactly `PASS`.

- [ ] **Step 4: Run final release command**

```bash
task release
```

Expected: release compiler exits `0` and emits source-tree/staging artifacts according to configuration.

- [ ] **Step 5: Verify final ZIP from a new temporary directory**

Commands must independently:

1. `unzip -t` the archive;
2. extract into a fresh directory;
3. run `sha256sum -c SHA256SUMS.txt` inside extracted root;
4. compare staged and extracted regular-file relative paths;
5. compare SHA-256 for every file;
6. verify sidecar digest against the ZIP.

Expected: all PASS.

- [ ] **Step 6: Confirm package hygiene**

Fail if archive contains `.git`, `.venv`, `__pycache__`, `.pytest_cache`, `.mypy_cache`, `.ruff_cache`, `*.pyc`, or untrusted partial-run files.

- [ ] **Step 7: Read generated QA reports and verify assurance wording**

Do not claim runtime target-product validation or production validation. Do not claim independent senior review/provider integration unless corresponding evidence exists.

- [ ] **Step 8: Commit final release metadata**

```bash
git add SHA256SUMS.txt QA-*.md docs/ACCEPTANCE-TRACEABILITY.yaml
git commit -m "qa: certify workflow v2.0.0 release"
```

Do not commit `/mnt/data/*.zip` into the repository unless the human partner explicitly requests repository-tracked binary releases.

---

## Final release completion evidence

The release report must include at least:

```text
Generic Core complete: PASS
web-saas profile complete: PASS
Codex adapter complete: PASS
Claude Code adapter complete: PASS
Gemini/Antigravity adapter complete: PASS
All schemas valid: PASS
All positive fixtures: PASS
All negative fixtures fail for expected class: PASS
TeamNotes static pipeline: PASS
Staleness detection: PASS
Audit closure: PASS
Self-hosting: PASS
Critical blockers: 0
High blockers: 0
ZIP integrity: PASS
Fresh re-extract checksum: PASS
Staged-tree/file-hash comparison: PASS
AI-provider execution integration: PERFORMED or NOT PERFORMED (truthful)
Independent senior review: PERFORMED or NOT PERFORMED (truthful)
Runtime target-project validation: NOT PERFORMED
Production target-project validation: NOT PERFORMED
```
