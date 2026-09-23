# AI Project Finalization Workflow V2 Validation and Release Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the layered static-analysis engine, audit/readiness gates, deterministic generators, and reproducible release compiler that convert core project records into evidence-backed PASS/FAIL outcomes and final ZIP artifacts.

**Architecture:** Validators implement a common `Validator` protocol and are registered by layer. A `ValidationContext` exposes project filesystem, schema registry, manifest/profile data, state, authority, artifacts, modules, and work packages without hidden global state. Deterministic generators operate only on validated inputs and register source hashes before their outputs become current.

**Tech Stack:** Python 3.12; openapi-spec-validator; jsonschema; zipfile; hashlib; tempfile; shutil; pytest.

**Spec:** `docs/superpowers/specs/shipgate-architecture-spec.md`

## Global Constraints

- `workflow validate` runs every applicable validator in deterministic layer order.
- Validation reports must be stable-sorted and machine-readable.
- Mechanical validators may never silently repair canonical input.
- An audit finding is not closed until there is exactly one valid terminal disposition.
- Critical or High unresolved blockers prevent `BUILD_READY`.
- Release assembly must re-extract and independently verify staged content.
- Release reports must distinguish static build readiness from runtime/production validation.
- The release compiler must not include `.git`, caches, virtual environments, test temporary files, or untrusted partial outputs.
- Final archive creation must be deterministic with normalized entry order and timestamps; if exact byte reproducibility cannot be maintained across Python/OS implementations, tree/hash reproducibility remains mandatory and the report must state the archive-byte limitation explicitly.

## Review Focus

- One validator raising an internal exception must produce an internal-error result without suppressing already-collected findings.
- OpenAPI documents with duplicate `operationId` or unresolved `$ref` must fail before build readiness.
- Audit disposition records referring to unknown findings or duplicate findings must fail closure.
- Staging must not follow symlinks or accidentally package secrets/caches outside the allowed source tree.
- A malicious ZIP entry name (`../x`, absolute path) must never be created or accepted by release verification.

---

### Task 1: Implement validator protocol, context, registry, and deterministic report ordering

**Files:**
- Create: `src/project_finalizer/validators/__init__.py`
- Create: `src/project_finalizer/validators/base.py`
- Create: `src/project_finalizer/validators/registry.py`
- Create: `src/project_finalizer/validation.py`
- Create: `tests/unit/test_validator_registry.py`
- Replace CLI `validate` stub with: `src/project_finalizer/commands/validate.py`

**Interfaces:**
- Consumes: core services from Foundation/Core plans.
- Produces: `ValidationContext`, `Validator`, `ValidatorRegistry`, `run_validators`, CLI `workflow validate`.

- [ ] **Step 1: Write failing deterministic-order test**

```python
# tests/unit/test_validator_registry.py
from project_finalizer.models import ValidationIssue, ValidationReport
from project_finalizer.validators import ValidatorRegistry


class ZValidator:
    name = "z"
    layer = "structure"

    def validate(self, ctx):
        return ValidationReport(
            (ValidationIssue("Z2", "b", "ERROR"), ValidationIssue("Z1", "a", "ERROR"))
        )


class AValidator:
    name = "a"
    layer = "syntax"

    def validate(self, ctx):
        return ValidationReport((ValidationIssue("A1", "a", "ERROR"),))


def test_registry_runs_layers_then_names_then_issue_codes():
    report = ValidatorRegistry([ZValidator(), AValidator()]).run(object())
    assert [i.code for i in report.issues] == ["A1", "Z1", "Z2"]
```

- [ ] **Step 2: Add internal-exception test**

A validator that raises `RuntimeError("boom")` must yield a single `INTERNAL_VALIDATOR_ERROR` issue tagged with validator name; `workflow validate` returns `INTERNAL_WORKFLOW_ERROR` only if internal errors exist, otherwise `VALIDATION_FAILED` for ordinary findings.

- [ ] **Step 3: Run RED**

```bash
uv run pytest tests/unit/test_validator_registry.py -q
```

- [ ] **Step 4: Implement protocol/registry**

Layer order is fixed:

```python
LAYER_ORDER = (
    "syntax",
    "structure",
    "references",
    "semantics",
    "authority",
    "contracts",
    "security",
    "work_packages",
    "audit",
    "readiness",
    "release",
)
```

Reject unknown layers at registration.

- [ ] **Step 5: Implement CLI output**

Default human output prints one line per issue: `SEVERITY CODE path subject: message`. Add `--format json` to print `{"ok":...,"issues":[...]}` without changing exit semantics.

- [ ] **Step 6: Run GREEN and commit**

```bash
uv run pytest tests/unit/test_validator_registry.py -q
git add src/project_finalizer/validators src/project_finalizer/validation.py src/project_finalizer/commands/validate.py tests/unit/test_validator_registry.py
git commit -m "feat: add layered validator engine"
```

---

### Task 2: Add syntax, structure, reference, authority, and ownership validators

**Files:**
- Create: `src/project_finalizer/validators/syntax.py`
- Create: `src/project_finalizer/validators/structure.py`
- Create: `src/project_finalizer/validators/references.py`
- Create: `src/project_finalizer/validators/authority.py`
- Create: `src/project_finalizer/validators/ownership.py`
- Create: `src/project_finalizer/validators/work_packages.py`
- Create: `tests/unit/validators/test_syntax.py`
- Create: `tests/unit/validators/test_references.py`
- Create: `tests/unit/validators/test_authority_validator.py`
- Create: `tests/unit/validators/test_ownership_validator.py`
- Create: `tests/unit/validators/test_work_package_validator.py`

**Interfaces:**
- Consumes: `ValidationContext`, AuthorityMatrix, ModuleCatalog, schemas.
- Produces: issue codes `SYNTAX_*`, `REF_*`, `AUTH_*`, `OWN_*`.

- [ ] **Step 1: Write failing broken-reference test**

```python
# tests/unit/validators/test_references.py
from project_finalizer.validators.references import ReferenceValidator


def test_unknown_authority_ref_is_reported(context_factory):
    ctx = context_factory(authority_refs=["docs/missing.md"])
    report = ReferenceValidator().validate(ctx)
    assert [i.code for i in report.issues] == ["REF_MISSING_PATH"]
```

- [ ] **Step 2: Write failing historical-authority and duplicate-owner tests**

Use existing core fixtures; assert `AUTH_HISTORICAL_LEAKAGE`, `OWN_DUPLICATE_OWNER`, and `OWN_FOREIGN_WRITE` exactly.

- [ ] **Step 3: Run RED**

```bash
uv run pytest tests/unit/validators/test_syntax.py tests/unit/validators/test_references.py tests/unit/validators/test_authority_validator.py tests/unit/validators/test_ownership_validator.py -q
```

- [ ] **Step 4: Implement validators as pure readers**

They must not mutate project files. Reference validation checks file existence and known logical IDs. Authority validation checks typed-primary rules, advisory leakage, and generated provenance. Ownership validation delegates graph construction to core models and converts domain errors into issues. Work-package validation checks WP-000, DAG acyclicity, dependency readiness, authority refs, allowed/forbidden path contradictions, acceptance commands/evidence, activated invariants, and protected-surface stop conditions.

- [ ] **Step 5: Run GREEN and commit**

```bash
uv run pytest tests/unit/validators -q
git add src/project_finalizer/validators tests/unit/validators
git commit -m "feat: validate authority and ownership invariants"
```

---

### Task 3: Implement generic OpenAPI/API contract validator

**Files:**
- Create: `src/project_finalizer/validators/api.py`
- Create: `tests/unit/validators/test_api_validator.py`
- Create: `tests/fixtures/openapi/valid.yaml`
- Create: `tests/fixtures/openapi/duplicate-operation-id.yaml`
- Create: `tests/fixtures/openapi/unregistered-error.yaml`

**Interfaces:**
- Consumes: OpenAPI files declared by project authority, error catalog, optional project API metadata policy.
- Produces: issue codes `API_PARSE`, `API_DUPLICATE_OPERATION_ID`, `API_ERROR_CODE_UNKNOWN`, `API_AUTH_METADATA_MISSING`, `API_IDEMPOTENCY_METADATA_MISSING`.

- [ ] **Step 1: Write failing duplicate operation ID test**

```python
# tests/unit/validators/test_api_validator.py
from project_finalizer.validators.api import ApiValidator


def test_duplicate_operation_id_fails(context_factory, repo_root):
    ctx = context_factory(
        openapi_path=repo_root / "tests/fixtures/openapi/duplicate-operation-id.yaml"
    )
    report = ApiValidator().validate(ctx)
    assert "API_DUPLICATE_OPERATION_ID" in {i.code for i in report.issues}
```

- [ ] **Step 2: Add unknown error code/auth metadata tests**

Public operations require stable `operationId`; when the project policy marks auth/authorization metadata required, absence is an issue. Do not impose web-saas-only rules in the generic validator; consume policy flags from context.

- [ ] **Step 3: Run RED**

```bash
uv run pytest tests/unit/validators/test_api_validator.py -q
```

- [ ] **Step 4: Implement parsing and checks**

First call `openapi_spec_validator.validate_spec`. Then walk methods (`get`, `post`, `put`, `patch`, `delete`, `options`, `head`) in sorted path/method order and collect operation metadata. Resolve only local/reference behavior supported by the validator library; report unresolved refs as parse/contract errors rather than guessing.

- [ ] **Step 5: Run GREEN and commit**

```bash
uv run pytest tests/unit/validators/test_api_validator.py -q
git add src/project_finalizer/validators/api.py tests/fixtures/openapi tests/unit/validators/test_api_validator.py
git commit -m "feat: validate OpenAPI contract integrity"
```

---

### Task 4: Implement audit finding/disposition closure validator

**Files:**
- Create: `src/project_finalizer/audit.py`
- Create: `src/project_finalizer/validators/audit.py`
- Create: `core/audit/SENIOR-AUDIT-RUBRIC.md`
- Create: `core/audit/SEVERITY-MODEL.md`
- Create: `core/audit/CORRECTIVE-RELEASE.md`
- Create: `core/audit/AUDIT-CLOSURE-GATE.md`
- Create: `tests/unit/test_audit.py`
- Create: `tests/fixtures/audit/closed/findings.yaml`
- Create: `tests/fixtures/audit/closed/dispositions.yaml`
- Create: `tests/fixtures/audit/orphan-disposition/findings.yaml`
- Create: `tests/fixtures/audit/orphan-disposition/dispositions.yaml`

**Interfaces:**
- Consumes: finding/disposition schemas.
- Produces: `AuditLedger`, `closure_report`, issue codes `AUDIT_*`.

- [ ] **Step 1: Write failing orphan and unresolved blocker tests**

```python
# tests/unit/test_audit.py
from project_finalizer.audit import AuditLedger


def test_orphan_disposition_blocks_closure():
    ledger = AuditLedger.from_records(
        findings=[],
        dispositions=[{"finding_id": "CTR-001", "disposition": "REJECTED", "reason": "x"}],
    )
    report = ledger.closure_report()
    assert "AUDIT_ORPHAN_DISPOSITION" in {i.code for i in report.issues}
```

Also assert a Critical finding with no disposition produces `AUDIT_CRITICAL_OPEN`, High produces `AUDIT_HIGH_OPEN`.

- [ ] **Step 2: Run RED**

```bash
uv run pytest tests/unit/test_audit.py -q
```

- [ ] **Step 3: Implement terminal closure logic**

Enforce one finding ID, one disposition per finding, no unknown disposition IDs, and evidence requirements from schema. `DEFERRED` is terminal in the ledger but remains a blocker for Critical/High by default.

- [ ] **Step 4: Add the audit rubric and severity docs**

The rubric covers contradiction, technical correctness, security, data integrity, API/contracts, async consistency, operational feasibility, agent executability, testability, and release governance. It instructs auditors to attempt to falsify readiness and not edit source artifacts.

- [ ] **Step 5: Run GREEN and commit**

```bash
uv run pytest tests/unit/test_audit.py -q
git add src/project_finalizer/audit.py src/project_finalizer/validators/audit.py core/audit tests/fixtures/audit tests/unit/test_audit.py
git commit -m "feat: enforce terminal audit closure"
```

---

### Task 5: Implement build-readiness validator and report model

**Files:**
- Create: `src/project_finalizer/readiness.py`
- Create: `src/project_finalizer/validators/readiness.py`
- Create: `core/release/BUILD-READINESS.md`
- Create: `core/release/HANDOFF-CONTRACT.md`
- Create: `tests/unit/test_readiness.py`
- Replace CLI `readiness` stub with: `src/project_finalizer/commands/readiness.py`

**Interfaces:**
- Consumes: validation summaries, state, authority, staleness, WP graph, audit closure, pending protected decisions.
- Produces: `ReadinessReport`, `evaluate_build_readiness`, CLI `workflow readiness`.

- [ ] **Step 1: Write failing protected-decision readiness test**

```python
# tests/unit/test_readiness.py
from project_finalizer.readiness import ReadinessInputs, evaluate_build_readiness


def test_pending_protected_decision_fails_build_readiness():
    report = evaluate_build_readiness(ReadinessInputs(pending_protected_decisions=("DR-004",)))
    assert report.verdict == "FAIL"
    assert "READINESS_PROTECTED_DECISION" in report.blocker_codes
```

- [ ] **Step 2: Add stale artifact, no-WP-000, open-high, and all-green tests**

All-green expected verdict is exactly `PASS`; do not call it `PRODUCTION_READY`.

- [ ] **Step 3: Run RED**

```bash
uv run pytest tests/unit/test_readiness.py -q
```

- [ ] **Step 4: Implement readiness evaluation**

Required checks: authority consistent, machine contracts valid when applicable, WP graph valid with WP-000, no stale required artifacts, no pending protected decisions, zero unresolved Critical/High blockers, applicable profile validators green.

- [ ] **Step 5: Implement CLI report and state transition integration**

On PASS, write `.workflow/readiness-report.yaml`; transition to `BUILD_READY` is separate and still uses the state gate. On FAIL return exit `70`.

- [ ] **Step 6: Run GREEN and commit**

```bash
uv run pytest tests/unit/test_readiness.py -q
git add src/project_finalizer/readiness.py src/project_finalizer/validators/readiness.py src/project_finalizer/commands/readiness.py core/release tests/unit/test_readiness.py
git commit -m "feat: evaluate coding-agent build readiness"
```

---

### Task 6: Implement deterministic generators and source-hash registration

**Files:**
- Create: `src/project_finalizer/generators/__init__.py`
- Create: `src/project_finalizer/generators/manifest.py`
- Create: `src/project_finalizer/generators/module_index.py`
- Create: `src/project_finalizer/generators/ownership_matrix.py`
- Create: `src/project_finalizer/generators/work_package_graph.py`
- Create: `src/project_finalizer/generators/audit_summary.py`
- Create: `src/project_finalizer/generators/readiness_report.py`
- Create: `tests/unit/generators/test_generators.py`

**Interfaces:**
- Consumes: validated core records.
- Produces: deterministic YAML/JSON/Markdown indexes with artifact graph registration.

- [ ] **Step 1: Write failing deterministic-generation test**

Generate the same module index twice from identical input in different input ordering; assert output bytes are identical.

- [ ] **Step 2: Write failing provenance-registration test**

After generation, assert the generated artifact record stores exact SHA-256 hashes of every declared upstream source.

- [ ] **Step 3: Run RED**

```bash
uv run pytest tests/unit/generators/test_generators.py -q
```

- [ ] **Step 4: Implement generators with stable ordering**

YAML keys use declared semantic order for top-level human readability, while repeated collections are sorted by stable IDs. Markdown tables sort rows by stable ID.

- [ ] **Step 5: Run GREEN and commit**

```bash
uv run pytest tests/unit/generators/test_generators.py -q
git add src/project_finalizer/generators tests/unit/generators
git commit -m "feat: generate deterministic workflow indexes"
```

---

### Task 7: Implement checksum inventory, staging, deterministic ZIP, and re-extract verification

**Files:**
- Create: `src/project_finalizer/release.py`
- Create: `src/project_finalizer/generators/checksum.py`
- Create: `src/project_finalizer/generators/release_archive.py`
- Create: `core/release/CHECKSUM-POLICY.md`
- Create: `core/release/ARCHIVE-INTEGRITY.md`
- Create: `core/release/REEXTRACT-VERIFICATION.md`
- Create: `tests/release/test_release_archive.py`
- Create: `tests/release/test_release_security.py`

**Interfaces:**
- Consumes: validated source tree, release manifest, `ProjectFS`.
- Produces: `stage_release`, `write_sha256sums`, `build_zip`, `verify_zip`, `verify_reextract`, sidecar digest.

- [ ] **Step 1: Write failing archive integrity test**

Create a tiny release tree, stage it, archive it, re-extract it, and assert all staged regular files have identical SHA-256 after extraction.

- [ ] **Step 2: Write failing traversal/security test**

Attempt to stage a symlink to outside and assert `RELEASE_UNSAFE_SYMLINK`. Verify `verify_zip` rejects an injected ZIP member named `../escape.txt` or `/absolute.txt`.

- [ ] **Step 3: Run RED**

```bash
uv run pytest tests/release/test_release_archive.py tests/release/test_release_security.py -q
```

- [ ] **Step 4: Implement staging exclusion policy**

Exclude at minimum:

```text
.git/
.venv/
__pycache__/
.pytest_cache/
.mypy_cache/
.ruff_cache/
*.pyc
.workflow/runs/*/partial/
```

Do not exclude canonical `.workflow` metadata when packaging generated project specs if the handoff contract requires it; exclusion is context-aware and explicit.

- [ ] **Step 5: Implement normalized ZIP metadata**

Write entries in sorted POSIX path order with a fixed DOS-compatible timestamp `(1980,1,1,0,0,0)` and normalized permission bits for files/directories. Use DEFLATED compression with fixed settings. This makes repeated archives byte-stable within supported Python runtime.

- [ ] **Step 6: Implement checksum policy**

`SHA256SUMS.txt` contains every staged regular file except itself. The ZIP sidecar contains `<ziphash>  <filename>` and is intentionally outside the ZIP to avoid self-reference.

- [ ] **Step 7: Run GREEN, repeat release twice, compare hashes**

```bash
uv run pytest tests/release/test_release_archive.py tests/release/test_release_security.py -q
```

Add a test that builds two archives from unchanged staging and asserts identical ZIP SHA-256.

- [ ] **Step 8: Commit**

```bash
git add src/project_finalizer/release.py src/project_finalizer/generators core/release tests/release
git commit -m "feat: add reproducible release compiler"
```

---

### Task 8: Wire `workflow release` with preflight gates and truthful assurance report

**Files:**
- Create: `src/project_finalizer/commands/release.py`
- Create: `src/project_finalizer/validators/release.py`
- Create: `src/project_finalizer/qa.py`
- Create: `tests/integration/test_release_command.py`
- Create: `tests/release/test_assurance_disclosure.py`

**Interfaces:**
- Consumes: validator registry, readiness report, release compiler.
- Produces: CLI `workflow release`; generated QA summary text.

- [ ] **Step 1: Write failing preflight test**

A project with stale artifacts or readiness FAIL must not create a ZIP; assert exit code `50` or `70` as appropriate and output path absent.

- [ ] **Step 2: Write assurance-disclosure test**

Generated report must contain exact fields:

```text
Static specification validation: PASS
Autonomous coding-agent handoff: PASS
Runtime implementation validation: NOT PERFORMED
Production validation: NOT PERFORMED
Independent audit: PERFORMED|NOT PERFORMED
Self-review: PERFORMED|NOT PERFORMED
```

Mutual truth rule: it may not say both `Independent audit: PERFORMED` and only self-review evidence exists.

- [ ] **Step 3: Run RED**

```bash
uv run pytest tests/integration/test_release_command.py tests/release/test_assurance_disclosure.py -q
```

- [ ] **Step 4: Implement release preflight**

Order: validate source tree → staleness → audit closure → readiness → manifest generation → checksum/stage/archive/re-extract → release validator → state transition to `FINAL_RELEASE`. `ReleaseValidator` checks manifest completeness, package hygiene, generated-artifact currency, checksum inventory, archive traversal safety, and fresh re-extract evidence. State changes only after archive verification passes.

- [ ] **Step 5: Run GREEN and full Validation/Release verification gate**

```bash
task format:check
task lint
task typecheck
task test
task test:release
git diff --check
```

Expected: all pass.

- [ ] **Step 6: Commit**

```bash
git add src/project_finalizer/commands/release.py src/project_finalizer/qa.py tests
git commit -m "feat: gate and report final releases"
```

---

## Validation and Release completion evidence

Record:

```text
Layered validators deterministic: PASS
Authority/ownership validators: PASS
OpenAPI integrity checks: PASS
Audit closure math: PASS
Build-readiness semantics: PASS
Generators deterministic: PASS
Staging rejects unsafe symlinks: PASS
ZIP traversal verification: PASS
Re-extract SHA-256 comparison: PASS
Repeated unchanged archive hash: PASS
Assurance disclosure truthful: PASS
```
