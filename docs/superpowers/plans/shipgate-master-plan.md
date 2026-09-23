# AI Project Finalization Workflow V2.0.0 Master Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build and release `ai-project-finalization-workflow-v2.0.0`, a reusable specification compiler, governance system, static analyzer, audit/corrective framework, and reproducible release compiler with a production-grade `web-saas` profile.

**Architecture:** Implement the approved design as five sequential, independently reviewable plans. The repository uses a small Python 3.12 package (`project_finalizer`) for deterministic orchestration and validation, static normative/template assets under `core/`, `profiles/`, `prompts/`, and `adapters/`, and a file-based project workspace model. LLM/provider execution is intentionally outside the deterministic core: the workflow prepares and validates role artifacts but does not require proprietary network APIs in V2.0.0.

**Tech Stack:** Python `>=3.12,<3.13`; standard-library `argparse`, `dataclasses`, `pathlib`, `hashlib`, `zipfile`; PyYAML; jsonschema; packaging; openapi-spec-validator; pytest; pytest-cov; Ruff; mypy; uv; Taskfile.

**Spec:** `docs/superpowers/specs/shipgate-architecture-spec.md`

## Global Constraints

- The target release name is exactly `ai-project-finalization-workflow-v2.0.0`.
- The initial complete profile is exactly `web-saas@2.0.0`.
- Runtime compatibility is `Python >=3.12,<3.13`.
- Generic Core must not depend on web-specific concepts.
- `UNKNOWN != PERMISSION TO INVENT`; protected ambiguity must create a Decision Request or block progress.
- Deterministic checks must not be delegated to an LLM.
- Authority is typed by subject; no single flat precedence ladder may replace the Authority Matrix.
- Generated/derived artifacts must retain source references and source hashes so staleness is detectable.
- Historical audits are advisory evidence only and must not become implementation authority.
- Adapters may reference canonical authority but must not become product authority.
- Optional `web-saas` extensions are disabled unless explicitly enabled.
- `BUILD_READY` means coding-agent specification handoff is complete; it does not imply runtime or production validation.
- Independent review must never be claimed when only self-review or same-context review occurred.
- The contributor command gateway is `Taskfile.yml` with `setup`, `format`, `format:check`, `lint`, `typecheck`, `test`, `test:unit`, `test:integration`, `test:fixtures`, `test:release`, `qa`, and `release` tasks.
- Stable CLI exit codes are fixed at `0,10,20,30,40,50,60,70,80,90` with meanings defined in the approved spec.
- Public CLI command names from the spec must remain stable; new helper subcommands may be private/internal only unless a design change is approved.
- V2.0.0 must not make outbound provider API calls as part of deterministic validation or release assembly.
- The repository `LICENSE` content is a protected human/legal decision. Do not invent a license; final release must stop until that decision is resolved.

## Review Focus

- Corrupted or partially-written YAML/JSON project state: commands must fail without mutating the last valid state.
- Path traversal/symlink inputs that escape a project root: readers, generators, and release assembly must reject them.
- Interrupted corrective/release runs: partial outputs must remain untrusted and must not silently become authority.
- Case-insensitive/Unicode-normalized identifier collisions: validators must reject duplicate logical IDs even when raw bytes differ.
- Deterministic archive reproducibility: two releases from an unchanged source tree must produce the same staged tree and checksum inventory; ZIP byte identity is required where the implementation normalizes metadata, otherwise the report must distinguish tree reproducibility from archive-byte reproducibility.

---

## Scope decomposition

The approved design spans multiple independently testable subsystems, so implementation is split into five plans rather than one monolithic task list. Execute them in order; each plan ends with a green repository and a commit boundary that a reviewer can accept or reject independently.

1. `shipgate-foundation-plan.md`
   - package/toolchain bootstrap;
   - CLI shell and exit-code contract;
   - schema registry and base schema inventory;
   - manifest/profile loading;
   - safe file IO and atomic writes.
2. `shipgate-core-plan.md`
   - intake/provenance/conflicts;
   - lifecycle/state transitions;
   - Decision Requests and change transactions;
   - typed authority and artifact staleness;
   - module/ownership/interaction models;
   - work-package graph/compiler;
   - run ledger/failure recovery.
3. `shipgate-validation-plan.md`
   - layered validator registry;
   - authority/ownership/API/audit/readiness checks;
   - deterministic generators;
   - checksum/staging/archive/re-extract release compiler.
4. `shipgate-saas-plan.md`
   - full `web-saas` profile and extensions;
   - profile-specific security/data/async validators;
   - agent-role prompt library and role registry;
   - Codex/Claude/Gemini/generic adapters.
5. `shipgate-release-plan.md`
   - TeamNotes positive example;
   - invalid and HCN-regression fixtures;
   - role evaluations;
   - self-hosting validation;
   - CI, QA evidence, final package, sidecar SHA-256.

## Spec coverage map

- Design Sections 1–5 (purpose, goals, principles, product shape): Master + Foundation plans.
- Sections 6–8 (lifecycle, intake, authority): Core Engine Tasks 2–5 and 10–11.
- Sections 9–14 (core specification, autonomy, module/interaction contracts, machine contracts, testing): Core Engine Tasks 4, 7–8; Web-SaaS/Agents Task 7; Validation Tasks 2–3.
- Sections 15–18 (WP compiler, audit, corrective loop, staleness): Core Engine Tasks 6, 8–9; Validation Tasks 4–6.
- Sections 19–22 (agent roles, review independence, human gates, run ledger): Web-SaaS/Agents Tasks 5–6; Core Engine Tasks 4, 9, 11.
- Sections 23–24 (`web-saas` profile and WP compilation): Web-SaaS/Agents Tasks 1–4 and 7.
- Sections 25–26 (build readiness and generated-project package): Validation Task 5; Web-SaaS/Agents Tasks 6–7; Evidence Task 2.
- Sections 27–35 (workflow package, prompts, schemas, validators, generators, CLI, profiles, adapters): Foundation Tasks 1–6; Core Engine Task 1; Validation Tasks 1–8; Web-SaaS/Agents Tasks 1, 5–6; Evidence Task 8.
- Sections 36–39 (TeamNotes, invalid/regression fixtures, workflow testing): Evidence Tasks 1–5.
- Section 40 (cross-provider compatibility): Web-SaaS/Agents Task 5 runtime capability model and Task 6 adapters.
- Sections 41–45 (toolchain, CI, manifest, release compiler, QA): Foundation Tasks 1 and 5; Validation Tasks 6–8; Evidence Tasks 7, 10–11.
- Sections 46–47 (self-hosting and Definition of Done): Evidence Tasks 6 and 11.
- Sections 48–56 (future user flow, frozen decisions, detailed inventories, command semantics, acceptance matrix): Core Engine Tasks 10–11; Web-SaaS/Agents Tasks 2–7; Evidence Tasks 8–11; final traceability file in Evidence Task 10.

## Cross-plan interfaces frozen here

All plans use these exact import/public names unless a design change is approved:

```python
from project_finalizer.errors import ExitCode, WorkflowError
from project_finalizer.io import ProjectFS
from project_finalizer.schemas import SchemaRegistry
from project_finalizer.models import ValidationIssue, ValidationReport
from project_finalizer.state import ProjectState, StateStore
from project_finalizer.validators import Validator, ValidatorRegistry
```

Core protocol shapes:

```python
@dataclass(frozen=True)
class ValidationIssue:
    code: str
    message: str
    severity: str
    path: str | None = None
    subject_id: str | None = None


@dataclass(frozen=True)
class ValidationReport:
    issues: tuple[ValidationIssue, ...]

    @property
    def ok(self) -> bool: ...


class Validator(Protocol):
    name: str

    def validate(self, ctx: "ValidationContext") -> ValidationReport: ...
```

State-store mutation must be atomic: validate complete new content in memory, write to a same-directory temporary file, `fsync`, then `os.replace`.

The deterministic workflow never stores chain-of-thought. A run ledger stores only inputs, output paths/hashes, rulings, validation results, and timestamps.

## Execution order and review gates

- [ ] Complete Foundation Plan; run its full verification gate; commit.
- [ ] Complete Core Engine Plan; run full repository QA; commit.
- [ ] Complete Validation & Release Plan; prove release compiler on minimal fixtures; commit.
- [ ] Complete Web-SaaS & Agents Plan; prove capability activation and adapter consistency; commit.
- [ ] Resolve the repository license Decision Request before final release assembly.
- [ ] Complete Evidence & Release Plan; run all positive/negative/self-hosting/release tests; commit.
- [ ] Run whole-branch review against the approved design and Final Acceptance Matrix.
- [ ] Only after fresh final verification create `ai-project-finalization-workflow-v2.0.0.zip` and `.zip.sha256`.

## Whole-program acceptance commands

At final handoff the repository must pass, from a clean checkout with dependencies already locked:

```bash
task format:check
task lint
task typecheck
task test
task test:fixtures
task test:release
task qa
task release
```

Expected final evidence:

```text
Static workflow validation: PASS
Generic Core validation: PASS
web-saas profile validation: PASS
Positive example pipeline: PASS
Negative fixtures: PASS (each fails for expected class)
Self-hosting validation: PASS
Critical blockers: 0
High blockers: 0
Release integrity: PASS
Runtime target-project validation: NOT PERFORMED
Production target-project validation: NOT PERFORMED
```
