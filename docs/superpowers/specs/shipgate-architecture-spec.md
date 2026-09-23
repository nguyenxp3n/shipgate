# AI Project Finalization Workflow V2.0.0 — Architectural Design Specification

**Document status:** Approved design
**Design date:** 2026-09-20
**Target release:** `ai-project-finalization-workflow-v2.0.0`
**Initial profile:** `web-saas@2.0.0`
**Primary purpose:** Convert heterogeneous project source material into a coherent, auditable, coding-agent-ready specification package and reproducible final ZIP without requiring prior chat context.

---

## 1. Executive Summary

`ai-project-finalization-workflow-v2.0.0` is a reusable specification factory for software projects. It is not a documentation checklist and it is not an application scaffolder. Its job is to take incomplete, overlapping, contradictory, or differently structured project materials and compile them into a canonical implementation handoff that a coding agent can execute safely from `WP-000` onward.

The system combines six functions:

1. **Specification compiler** — normalizes raw project materials into canonical product, domain, architecture, data, security, operational, and machine-readable contracts.
2. **Agent governance system** — defines authority, controlled autonomy, protected decisions, stop conditions, file ownership, command gateways, and implementation protocol.
3. **Static analyzer** — validates schemas, authority graphs, references, module ownership, dependency graphs, contract coverage, audit closure, staleness, and release integrity.
4. **Audit framework** — runs an adversarial senior review against contradictions, technical correctness, security, data integrity, operational feasibility, agent executability, and testability.
5. **Corrective release system** — tracks every accepted or rejected finding to a terminal disposition and forces affected artifacts to be regenerated and revalidated.
6. **Reproducible release compiler** — produces the final specification ZIP, sidecar hash, manifest, QA evidence, and re-extract verification.

The design uses a **Generic Core + specialized profiles** model. The Generic Core is domain-agnostic. The first specialized profile, `web-saas`, provides production-grade constraints and completeness gates for modern web applications and SaaS systems while allowing optional capability packs such as multi-tenancy, background processing, file storage, payments, AI integration, realtime, and search.

The workflow must distinguish these states precisely:

- `SPEC_COMPLETE`
- `AGENT_SPEC_READY`
- `BUILD_READY`
- `RUNTIME_VERIFIED`
- `PRODUCTION_READY`

`BUILD_READY` means a coding agent can begin implementation without inventing protected product, API, data, security, or deployment decisions. It does **not** mean an application has been implemented or validated in production.

---

## 2. Goals

### 2.1 Primary goals

The workflow shall:

- accept 10–100+ heterogeneous source files and project notes;
- preserve provenance from raw inputs to normalized requirements and canonical specifications;
- detect conflicting claims instead of silently choosing one;
- establish authority by subject type rather than by one global precedence list;
- separate normative prose from machine-readable wire/data contracts;
- define a complete coding-agent operating model;
- create module ownership and dependency boundaries that are mechanically checkable;
- compile implementation work into a dependency-aware DAG of READY work packages;
- enforce a clear distinction between free, constrained, and protected decisions;
- run senior audit passes and require terminal disposition for every finding;
- detect stale derived artifacts after source changes;
- validate build readiness with deterministic checks where possible;
- create a reproducible final release archive with integrity evidence;
- work with Codex, Claude Code, Gemini/Antigravity, and generic coding agents through thin adapters;
- operate without relying on prior chat history as hidden authority.

### 2.2 Secondary goals

The workflow should:

- make project ambiguity visible early;
- reduce architecture drift between documentation and implementation;
- reduce agent context pollution through progressive disclosure;
- support partial automation while preserving explicit human approval for load-bearing decisions;
- make assurance claims precise and evidence-backed;
- remain extensible to future profiles such as mobile, backend API, desktop, and data platforms.

---

## 3. Non-Goals

V2.0.0 shall not:

- generate or implement the target product application itself;
- claim runtime correctness for software not yet implemented;
- replace penetration testing, load testing, production monitoring, or compliance certification;
- automatically decide unresolved protected product/security/data decisions;
- require every project to use the same application stack;
- require microservices, Kubernetes, event-driven architecture, or any other topology unless project requirements demand them;
- enable every optional capability by default;
- use LLM judgment for checks that can be deterministic;
- treat historical audit documents as active implementation authority;
- claim independent audit when only a same-context or self-review was performed.

---

## 4. Design Principles

### 4.1 Authority is typed, not flat

Different artifact types own different truths. Examples:

- product behavior → canonical product/domain prose;
- HTTP wire shape → OpenAPI;
- event/config/document shape → JSON Schema;
- database physical shape → migrations/schema contract;
- security invariants → security normative specification;
- implementation sequence → READY work packages;
- historical audits → advisory evidence only.

A single global precedence ladder is insufficient and creates ambiguity. The workflow therefore uses an **Authority Matrix** keyed by subject type.

### 4.2 Unknown does not mean permission to invent

The workflow follows the hard rule:

> `UNKNOWN != PERMISSION TO INVENT`

Protected ambiguity becomes a Decision Request or release blocker.

### 4.3 Deterministic verification beats LLM assertion

If a condition can be checked mechanically, the workflow shall use a validator or generator rather than a prompt asking an LLM to “verify” it.

Examples include:

- duplicate identifiers;
- broken references;
- JSON Schema validity;
- OpenAPI validity;
- graph cycles;
- missing terminal dispositions;
- stale artifact hashes;
- manifest completeness;
- archive integrity;
- checksum verification.

### 4.4 Derived artifacts must be traceable

Generated or compiled artifacts must identify canonical upstream sources and source hashes so staleness can be detected automatically.

### 4.5 Progressive disclosure for coding agents

A coding agent shall not need to read the entire corpus before starting. Root adapters direct the agent to the canonical manual, authority model, manifest, and the first eligible work package. Each work package references only the relevant modules and contracts.

### 4.6 Review roles shall be separated from author roles where possible

A final auditor should use fresh context when the execution environment supports it. If not, reports must explicitly identify self-review or same-model review as degraded assurance.

---

## 5. Product Shape: Generic Core + Profiles + Adapters

The workflow has four major layers:

```text
ai-project-finalization-workflow-v2.0.0/
├── core/                  # Generic lifecycle, authority, governance, audit, readiness, release
├── profiles/              # Domain/platform-specific completeness rules
├── adapters/              # Thin bootstrap surfaces for coding-agent ecosystems
└── reference/ or examples/# Executable examples and regression lessons
```

### 5.1 Generic Core

The Generic Core contains only project-agnostic concepts:

- lifecycle/state machine;
- source ingestion and normalization;
- requirement provenance;
- authority model;
- decision governance;
- module decomposition rules;
- cross-component interaction model;
- testing/invariant model;
- work-package model;
- audit/disposition model;
- staleness graph;
- readiness gates;
- release compiler.

The Core must not contain web-specific assumptions such as cookies, CORS, REST, browsers, or SQL databases.

### 5.2 Profiles

Profiles define additional requirements for a project class. V2.0.0 ships with:

- `web-saas@2.0.0`

Future profiles may include:

- `mobile`
- `backend-api`
- `desktop`
- `data-platform`

Profiles add capability definitions, validators, templates, testing matrices, and profile-specific work-package compilation rules.

### 5.3 Adapters

Adapters provide environment-specific bootstraps for:

- generic agent;
- Codex;
- Claude Code;
- Gemini/Antigravity.

Adapters may reference canonical authority but must not become product authority.

---

## 6. Project Lifecycle and State Machine

Every project processed by the workflow moves through explicit states:

```text
RAW_INPUT
  ↓
INTAKE_COMPLETE
  ↓
SOURCE_NORMALIZED
  ↓
CORE_SPEC_FROZEN
  ↓
MACHINE_CONTRACTS_READY
  ↓
AGENT_SPEC_READY
  ↓
WORK_PACKAGES_READY
  ↓
SENIOR_AUDITED
  ↓
CORRECTIVE_COMPLETE
  ↓
BUILD_READY
  ↓
FINAL_RELEASE
```

### 6.1 State transitions

A state transition may occur only after the transition validator proves the required gates. Agents cannot directly edit `current_state` to bypass checks.

Example project-state representation:

```yaml
project_state:
  current: SENIOR_AUDITED
  previous: WORK_PACKAGES_READY
  allowed_next:
    - CORRECTIVE_COMPLETE

gates:
  source_of_truth_complete: true
  core_spec_frozen: true
  machine_contracts_valid: true
  wp_graph_valid: true
  audit_complete: true
  unresolved_critical: 3
  unresolved_high: 7
```

This state cannot transition to `BUILD_READY` while Critical/High blockers remain unresolved.

### 6.2 Logical locking

When a state freezes an artifact class, those files become logically locked. Later changes require a **Change Transaction** that records:

- reason;
- finding or decision that caused the change;
- affected authorities;
- downstream artifacts;
- version impact;
- verification evidence.

---

## 7. Source Intake and Normalization

### 7.1 Accepted input classes

The workflow shall support source materials such as:

- product notes;
- design documents;
- architecture notes;
- existing README files;
- API notes or OpenAPI files;
- database schemas and migrations;
- diagrams exported to supported text metadata or referenced as source evidence;
- ADRs;
- agent instructions;
- previous audits;
- legacy specifications;
- operational runbooks;
- implementation plans.

### 7.2 Discovery outputs

Discovery creates:

```text
workspace/intake/
├── INPUT-INVENTORY.yaml
├── REQUIREMENTS-EXTRACTED.yaml
├── CONFLICTS.yaml
├── UNKNOWNS.yaml
├── ASSUMPTIONS.yaml
├── LEGACY-DOC-CLASSIFICATION.yaml
└── DISCOVERY-REPORT.md
```

A requirement must preserve provenance:

```yaml
id: REQ-0042
source:
  file: product-notes.md
  location: section-7
statement: Users may preview public courses without authentication.
classification: product_behavior
confidence: explicit
status: unresolved_authority
```

### 7.3 Conflict behavior

When two sources disagree, Discovery records both claims. It must not choose a winner merely because one file is newer, longer, or more detailed.

### 7.4 Intermediate Representation (IR)

Normalization creates a project IR containing:

- actors;
- capabilities;
- entities;
- workflows;
- external systems;
- requirements;
- conflicts;
- decisions;
- provenance edges.

The IR is a normalized index, not the final semantic authority.

---

## 8. Authority Model

### 8.1 Authority Matrix

Each project produces a machine-readable authority matrix. Example:

```yaml
authority:
  product_behavior:
    primary: docs/core/PRODUCT-SPEC.md
    secondary:
      - docs/core/DOMAIN-MODEL.md

  http_wire_format:
    primary: contracts/openapi/openapi.yaml
    prose_reference: docs/core/API-SEMANTICS.md

  event_wire_format:
    primary: contracts/events/*.schema.json

  database_physical_schema:
    primary: database/migrations/**

  database_semantics:
    primary: docs/core/DATA-MODEL.md

  security_invariants:
    primary: docs/core/SECURITY.md

  implementation_order:
    primary: docs/agent-spec/work-packages/**

  historical_audits:
    authority: advisory_only
```

### 8.2 Authority validator requirements

The authority validator shall detect:

- missing primary authority for mandatory subject types;
- multiple primary authorities for one subject without an explicit composition rule;
- historical or advisory documents referenced as normative implementation sources;
- adapters overriding canonical truth;
- derived artifacts missing provenance;
- machine/prose contradictions for subject types where comparison is defined;
- stale derived artifacts.

---

## 9. Canonical Core Specification

The Core Specification separates “what” from “how.”

### 9.1 Required canonical documents

For a typical software project, applicable files include:

- `PRODUCT-SPEC.md`
- `DOMAIN-MODEL.md`
- `TECHNICAL-SPEC.md`
- `DATA-MODEL.md`
- `API-SEMANTICS.md`
- `SECURITY.md`
- `DEPLOYMENT.md`
- `OPERATIONS.md`
- `OBSERVABILITY.md`
- `FAILURE-MODES.md`
- `NON-FUNCTIONAL-REQUIREMENTS.md`

Profiles may add or disable specific documents when evidence justifies applicability.

### 9.2 Scope separation

- `PRODUCT-SPEC.md` owns externally visible behavior and scope.
- `DOMAIN-MODEL.md` owns business terminology, state machines, invariants, and relationships.
- `TECHNICAL-SPEC.md` owns architecture and runtime decomposition.
- `API-SEMANTICS.md` owns HTTP/API semantics but not exact wire shape.
- `DATA-MODEL.md` owns data meaning, ownership, lifecycle, and retention semantics.
- machine contracts own exact structured shape.

---

## 10. Controlled Autonomy and Decision Governance

### 10.1 Three decision levels

#### Level 1 — Free

Examples:

- local variable names;
- private helper functions;
- small internal refactors;
- test helper layout;
- non-public comments.

#### Level 2 — Constrained

Examples:

- internal package layout;
- query implementation strategy;
- cache internals;
- non-public algorithm choice;
- approved dependency choice within policy.

#### Level 3 — Protected

Examples:

- public API contracts;
- database schema or migrations;
- authorization/security/privacy/retention;
- business rules and state machines;
- cross-module events;
- external providers;
- deployment topology;
- irreversible data operations;
- public product behavior.

A Level-3 ambiguity requires a Decision Request, approved ADR, or explicit corrective decision.

### 10.2 Decision Requests

Decision Requests are machine-readable and human-reviewable. The CLI shall support listing, showing, and resolving decisions. Resolutions preserve the original user decision and become immutable project evidence.

---

## 11. Module Decomposition and Ownership

### 11.1 Module contract

Each implementation module shall define:

- identifier and status;
- responsibilities;
- owned data;
- data it must not mutate;
- public commands/queries;
- consumed events;
- emitted events;
- dependencies;
- transaction ownership;
- critical invariants;
- test obligations.

Example:

```yaml
module:
  id: billing
  status: active
responsibilities:
  - manage_subscription
  - produce_invoice_state
owned_data:
  - subscriptions
  - invoices
must_not_write:
  - users
  - organizations
public_interfaces:
  commands:
    - ChangePlan
  queries:
    - GetSubscription
consumes_events:
  - payment.succeeded.v1
emits_events:
  - subscription.changed.v1
dependencies:
  allowed:
    - users
    - payments
  forbidden:
    - analytics
transactions:
  owns:
    - subscription_change
critical_invariants:
  - only_one_active_subscription_per_org
```

### 11.2 Ownership validator

The workflow shall detect:

- duplicate data ownership;
- direct foreign-module table mutation;
- forbidden dependency edges;
- cycles where the selected architecture forbids them;
- missing producer/consumer definitions;
- cross-module writes without contract.

---

## 12. Cross-Module Interaction Model

Every meaningful cross-component interaction shall be classified as exactly one of:

- synchronous query;
- synchronous command;
- same-request orchestration;
- domain event;
- background job;
- transactional outbox event;
- external webhook.

Each interaction must define, when applicable:

- owner;
- producer;
- consumer;
- request or event schema;
- transaction boundary;
- commit point;
- retry semantics;
- idempotency semantics;
- timeout behavior;
- failure behavior;
- response authority.

This requirement prevents contradictory contracts such as an API promising immediately authoritative foreign-module state while the foreign state is only eventually updated asynchronously.

---

## 13. Machine Contracts

The workflow supports machine-readable authorities including:

- OpenAPI;
- JSON Schema;
- event catalogs;
- configuration schemas;
- error catalogs;
- permission catalogs;
- module manifests;
- ownership matrices.

### 13.1 Contract provenance

Where supported, machine contracts should preserve requirement and semantic references, for example:

```yaml
x-requirement-refs:
  - REQ-041
  - APISEM-008
```

### 13.2 Error catalog

A project shall use a canonical error catalog rather than module-specific ad hoc formats when the selected profile requires common API errors.

---

## 14. Testing Architecture

### 14.1 Phase-aware gates

Testing requirements activate when the relevant implementation surface becomes present. The workflow must not require impossible coverage before code exists, but once an invariant becomes active, required tests become mandatory.

Example:

```yaml
invariant:
  id: AUTH-004
  owner: auth
  active_from_wp: WP-006
  required_tests:
    - integration
    - security
```

### 14.2 Test classes

Supported test classes include:

- unit;
- schema;
- contract;
- integration;
- security;
- browser E2E;
- deployment smoke;
- release reproducibility.

### 14.3 Coverage policy

Coverage thresholds are guardrails, not substitutes for critical-invariant tests. Profiles may define path/package classifications and empirical re-evaluation rules.

---

## 15. Work-Package Compiler

### 15.1 Work package model

Every work package shall contain:

- ID;
- title;
- state;
- purpose;
- dependencies;
- inputs;
- authority references;
- allowed paths;
- forbidden paths;
- interfaces consumed;
- interfaces produced;
- schema/migration impact;
- security impact;
- acceptance tests;
- critical invariants activated;
- commands to run;
- expected evidence;
- stop conditions;
- completion evidence.

A work package that only says “Implement authentication” is invalid.

### 15.2 Graph rules

The Work-Package Graph must:

- have unique IDs;
- have a valid entrypoint;
- be acyclic;
- use valid dependency references;
- prevent READY packages from depending on unresolved blockers;
- respect capability dependencies;
- reference existing commands and authority artifacts.

### 15.3 WP-000

Every project begins with an applicable bootstrap package that creates the foundations required for all later packages, including repository structure, toolchain pins, command gateway, formatting, linting, tests, contract validation, environment bootstrap, generated-code locations, and migration locations as applicable.

---

## 16. Audit Framework

### 16.1 Senior audit behavior

The final Senior Auditor should begin from an adversarial neutral prompt:

> Assume the package may contain structural defects. Attempt to falsify implementation readiness.

Audit passes include:

- contradiction;
- technical correctness;
- security;
- data integrity;
- API/contracts;
- asynchronous consistency;
- operational feasibility;
- agent executability;
- testability;
- release governance.

### 16.2 Finding model

A finding is structured data, not only prose:

```json
{
  "id": "CTR-014",
  "category": "CONTRADICTION",
  "severity": "HIGH",
  "status": "OPEN",
  "affected": [
    "docs/core/API-SEMANTICS.md",
    "contracts/openapi/openapi.yaml"
  ],
  "summary": "OpenAPI response promises synchronous foreign-module state that is only produced asynchronously.",
  "evidence": ["API semantics require immediate `newBalance`; event contract defines balance update as post-commit asynchronous."],
  "implementation_risk": "Clients may observe or depend on state the server cannot authoritatively return at commit time.",
  "recommended_resolution": "Make the response local-state authoritative or move the required foreign update into the same approved transaction/orchestration boundary."
}
```

### 16.3 Severity model

- **Critical:** can cause severe security failure, cross-tenant exposure, data loss, impossible transaction behavior, credential compromise, or unsafe destructive operations.
- **High:** material implementation ambiguity or correctness risk, such as contradictory public API, undefined ownership, missing idempotency for retryable money mutation, or unrecoverable worker behavior.
- **Medium:** meaningful but non-blocking defect when explicitly accepted.
- **Low:** minor quality or maintenance issue.

The system must not inflate every inconsistency to Critical.

---

## 17. Corrective Release Loop

Every finding receives one terminal disposition:

- `FIXED`
- `ALREADY_FIXED`
- `DEFERRED`
- `NOT_APPLICABLE`
- `REJECTED`

### 17.1 Disposition requirements

A `FIXED` disposition requires:

- resolution references;
- verification references.

A `REJECTED` or `NOT_APPLICABLE` disposition requires a reason and evidence.

Default release policy:

- Critical deferred → blocker;
- High deferred → blocker;
- Medium deferred → allowed only with explicit rationale;
- Low deferred → allowed.

### 17.2 Corrective cycle

```text
AUDIT
  ↓
TRIAGE
  ↓
PATCH CANONICAL SOURCE
  ↓
REGENERATE DERIVED CONTRACTS
  ↓
VALIDATE
  ↓
RE-AUDIT AFFECTED SURFACE
```

Generated artifacts must not be patched as substitutes for fixing canonical sources.

---

## 18. Artifact Dependency and Staleness Engine

### 18.1 Dependency graph

Artifacts record upstream dependencies and source hashes.

Example:

```yaml
artifact:
  id: OPENAPI
  path: contracts/openapi/openapi.yaml
  depends_on:
    - API_SEMANTICS
    - ERROR_CATALOG
  built_from_hashes:
    API_SEMANTICS: "sha256:34af0e6d-example"
    ERROR_CATALOG: "sha256:11bc92d1-example"
```

If an upstream source changes and the downstream artifact has not been regenerated, the downstream artifact becomes `STALE_ARTIFACT` and blocks `BUILD_READY` and release.

### 18.2 Impact propagation

A changed artifact marks dependent artifacts stale transitively where required. Example:

```text
PRODUCT-SPEC
  ↓
DOMAIN-MODEL
  ↓
API-SEMANTICS
  ↓
OPENAPI
  ↓
GENERATED CLIENT
  ↓
WORK PACKAGES
```

---

## 19. AI Agent Role System

### 19.1 Controller/Orchestrator

The Controller:

- owns state transitions;
- selects the role appropriate to the current phase;
- enforces write ownership;
- runs validators;
- tracks runs and evidence;
- pauses for human decisions;
- resumes safely;
- does not independently invent protected architecture.

### 19.2 Agent registry

Roles and write boundaries are machine-readable. A role attempting to write outside its allowed paths is denied.

### 19.3 Required V2 roles

1. Discovery Agent
2. Normalization Agent
3. Product & Domain Architect
4. Technical Architect
5. Contract Compiler
6. Security & Data Integrity Reviewer
7. Agent-Spec Compiler
8. Work-Package Compiler
9. Senior Auditor
10. Corrective Agent
11. Build-Readiness Reviewer
12. Release Compiler

### 19.4 Role isolation

#### Discovery Agent

Reads all source materials and records requirements, conflicts, unknowns, assumptions, and legacy classification. It does not resolve contradictions.

#### Normalization Agent

Builds the project IR and preserves provenance. It does not become semantic authority.

#### Product & Domain Architect

Owns product behavior, actors, workflows, business rules, terminology, state machines, and business invariants. It must escalate unresolved protected product decisions.

#### Technical Architect

Owns architecture, module decomposition, data ownership, runtime components, dependency directions, deployment topology, and failure boundaries. It cannot change product behavior merely to simplify implementation.

#### Contract Compiler

Compiles approved semantics into machine-readable contracts. It cannot invent unsupported public behavior.

#### Security & Data Integrity Reviewer

Performs an early design review for authentication, authorization, privacy, tenancy, transactions, migrations, idempotency, outbox/inbox, backup/restore, and sensitive-data handling.

#### Agent-Spec Compiler

Builds the coding-agent governance layer: operating manual, autonomy rules, command specs, change control, repository ownership, testing rules, and decision protocol.

#### Work-Package Compiler

Produces the implementation DAG and package-level acceptance evidence.

#### Senior Auditor

Read-only against canonical project sources. Writes only audit artifacts.

#### Corrective Agent

Applies accepted corrections through explicit change transactions and regenerates affected derived artifacts.

#### Build-Readiness Reviewer

Simulates a new coding agent and attempts to prove that implementation can begin without guessing protected decisions.

#### Release Compiler

Runs deterministic release assembly, integrity verification, hashes, and final packaging.

---

## 20. Review Independence and Anti-Bias

Where the platform supports a fresh reviewer, the Senior Auditor should receive fresh context and should not be the same context that authored the artifacts.

If fresh review is unavailable, the final QA report must state:

```text
Independent audit: NOT PERFORMED
Final review mode: SELF-REVIEW
```

A self-review must never be described as independent.

---

## 21. Human Approval Gates

The workflow shall minimize unnecessary approvals but pause at load-bearing decision points.

Default human gates:

- Project Intent Freeze;
- Protected Decision Resolution;
- Core Product/Domain Freeze;
- Architecture Freeze;
- Major Corrective Architecture Change;
- Final Release Approval.

Mechanical validation phases run without human confirmation unless they surface a blocker.

---

## 22. Run Ledger and Failure Recovery

Every agent run records:

- run ID;
- role;
- start/end metadata;
- input artifact identifiers and hashes;
- output artifact identifiers and hashes;
- validator results;
- decisions created;
- rulings needed for downstream operation.

The ledger does not need private chain-of-thought.

If a run fails mid-phase, incomplete outputs are marked `UNTRUSTED_PARTIAL`. The controller may resume only where safety is established, otherwise it discards and regenerates partial outputs.

---

## 23. `web-saas` Profile

### 23.1 Purpose

The first specialized profile shall support production-grade documentation for:

- SaaS applications;
- LMS/CRM-like web platforms;
- B2B and B2C web applications;
- admin portals;
- internal tools with protected business data;
- lightweight marketplaces;
- subscription applications;
- dashboards;
- modular web platforms.

It is stack-neutral but completeness-strict.

### 23.2 Capability resolution

Every capability is classified as:

- `required`
- `optional_enabled`
- `disabled`

Disabled capability means it is outside the current release and coding agents must not add it “for future flexibility.”

Initial capability catalog:

- frontend;
- API;
- authentication;
- authorization;
- users;
- organizations/multi-tenancy;
- database;
- cache;
- jobs;
- events;
- file/object storage;
- email;
- notifications;
- admin;
- search;
- analytics;
- payments;
- audit log;
- observability;
- operations;
- AI integration;
- realtime;
- PWA.

### 23.3 Frontend requirements

Applicable projects must explicitly define:

- routing model;
- rendering model;
- auth bootstrap;
- authorization visibility behavior;
- API client boundary;
- server state;
- local UI state;
- forms and validation;
- error/loading/empty/offline states;
- accessibility target;
- responsive behavior;
- browser support;
- service-worker/PWA cache rules;
- generated API types if enabled.

Private authenticated data must not be cached by a service worker unless the project explicitly defines and reviews a secure policy.

### 23.4 API requirements

Every public operation must define, as applicable:

- stable operation ID;
- auth requirement;
- authorization requirement;
- validation;
- request/response schema;
- error behavior;
- rate-limit behavior;
- idempotency;
- transaction semantics;
- pagination;
- retry behavior.

A canonical error envelope and error catalog shall be used when the project exposes a common API surface.

### 23.5 Authentication

The profile requires explicit decisions for:

- identity source;
- credential ownership;
- password/SSO model;
- email verification;
- login/logout;
- session creation/rotation/revocation;
- account recovery;
- multi-device sessions;
- multi-tab race behavior where relevant;
- CSRF;
- CORS;
- token storage and expiration;
- refresh behavior;
- brute-force/rate-limit controls;
- audit events.

The profile does not force JWT or server-side sessions; it forces one coherent model.

### 23.6 Authorization

Authorization must define:

- roles;
- permissions;
- resource scope;
- tenant scope;
- ownership checks;
- system roles;
- object-level access;
- admin override rules;
- service identities.

Frontend visibility is not authoritative authorization.

### 23.7 Multi-tenancy extension

If enabled, the project must choose one tenant model and define tenant boundaries for every tenant-owned entity. Missing tenant boundaries on tenant-owned data are release blockers.

### 23.8 Database

Database contracts must define:

- engine/version;
- identifiers/timestamps;
- ownership;
- PK/FK/UNIQUE/CHECK/NOT NULL rules;
- delete semantics;
- retention;
- indexes for declared hot paths;
- migration strategy;
- transaction boundaries;
- backup/restore requirements.

Production migration policy shall use safe expand/migrate/contract reasoning where required by availability and compatibility constraints.

### 23.9 Transaction boundaries

Every user-visible mutation must identify:

- authoritative write;
- same-transaction writes;
- post-commit events;
- eventual effects;
- response data authority.

### 23.10 Jobs/events/outbox

If asynchronous processing is enabled, the profile requires:

- outbox where cross-component durable publication requires it;
- consumer idempotency/inbox where needed;
- retry policy;
- dead-letter handling;
- ordering assumptions;
- event versioning;
- retention;
- worker concurrency;
- poison-message handling;
- observability.

### 23.11 Cache

Each cache must define owner, source of truth, key format, TTL, invalidation, outage behavior, stale tolerance, and privacy classification. Cache is not authoritative business state unless explicitly designed and audited as such.

### 23.12 File/object storage

If enabled, the project must define actual content validation, limits, authorization, private/public visibility, signed URL behavior, malware policy, metadata stripping where relevant, retention, deletion, and orphan cleanup.

### 23.13 Email/notifications

Business transaction success must be separated from notification delivery unless the product explicitly requires atomic coupling. Security-sensitive flows such as password reset require token entropy, expiration, single-use semantics, enumeration protection, and rate limits.

### 23.14 Payments extension

Payments remain disabled by default. When enabled, the project must separate provider state from application entitlement state and define webhook signature verification, replay protection, deduplication, out-of-order behavior, reconciliation, and idempotency.

### 23.15 Admin

Admin contracts must address authentication, authorization, privileged mutations, impersonation, destructive operations, bulk actions, data export, audit logging, and step-up/re-authentication requirements where risk requires them.

### 23.16 Audit log

Security audit logs must record who did what to which resource, when, from where, with result and correlation data, while excluding passwords, tokens, secrets, and other forbidden data.

### 23.17 Observability

The profile requires decisions for structured logging, request/correlation IDs, metrics, tracing strategy, health/readiness, alerting, error reporting, and PII redaction. Thresholds remain project decisions.

### 23.18 Environment/configuration

Every environment variable must have a schema defining type, requirement level, allowed environments, defaults where safe, and secret classification.

### 23.19 Secrets

The project must define secret storage, runtime injection, rotation, local-development handling, CI handling, logging redaction, and incident revocation.

### 23.20 Browser security

Applicable projects must explicitly address:

- CSP;
- CORS;
- CSRF;
- XSS;
- clickjacking;
- secure cookies;
- mixed content;
- referrer policy;
- permissions policy;
- open redirects;
- DOM injection;
- third-party scripts;
- service-worker caching.

### 23.21 SSRF

If the backend can fetch user-controlled or integration-controlled URLs, SSRF controls become mandatory. If no such surface exists, the project records `NOT_APPLICABLE` with evidence.

### 23.22 Rate limiting

Rate-limit policy is surface-specific, not globally uniform. It may define separate policies for login, registration, password reset, general API, expensive operations, AI, uploads, webhooks, and admin actions.

### 23.23 Privacy and retention

Data classification must distinguish at least public, internal, confidential, personal, and secret information. Personal-data rules must define purpose, retention, deletion, export, backup implications, logging implications, and analytics implications.

### 23.24 Backup, restore, and DR

The profile requires backup target/frequency/retention/encryption, restore procedure, restore verification, RPO/RTO, object storage recovery where applicable, secret recovery, rollback, and migration recovery.

### 23.25 Deployment

The profile supports single-VM, Compose, container platforms, Kubernetes, serverless, and managed PaaS, but every selected topology must define artifacts, configuration injection, migration ordering, health/readiness gates, rollback behavior, worker deployment, static assets, CDN if applicable, and TLS termination.

### 23.26 Dependency policy

Projects shall pin dependencies and define license/security policy. New dependencies are constrained decisions unless explicitly preapproved by policy.

### 23.27 Testing matrices

The profile shall produce machine-readable matrices covering:

- browser E2E;
- API contracts;
- auth/security;
- database integration;
- job/event behavior;
- deployment smoke tests.

A surface that does not apply must be explicitly `NOT_APPLICABLE` with evidence rather than silently omitted.

### 23.28 Failure-mode catalog

Every enabled capability must define relevant failure behavior as one of:

- fail open;
- fail closed;
- retry;
- degrade;
- queue;
- return error.

Security-sensitive behavior should default toward fail closed unless the approved design specifies otherwise.

### 23.29 AI integration extension

Disabled by default. When enabled, the project must define provider, model role, prompt ownership, tool permissions, external data sharing, PII rules, retention, moderation, timeouts, retries, cost/rate limits, fallback, streaming, validation, and AI authority boundaries.

Default rule:

> AI output is not authoritative business state unless the project explicitly defines and audits that authority.

### 23.30 Realtime extension

If enabled, define connection authentication, authorization, reconnect, replay, ordering, heartbeat, backpressure, and horizontal-scaling assumptions.

### 23.31 Search extension

If enabled, the default model treats search as derived state from authoritative storage and requires indexing, reindex, eventual consistency, delete propagation, recovery, and schema-versioning rules.

---

## 24. `web-saas` Work-Package Compilation

The profile may commonly generate packages resembling:

```text
WP-000 Repository Bootstrap
  ↓
WP-001 Toolchain & Command Gateway
  ↓
WP-002 Configuration
  ↓
WP-003 Database Foundation
  ↓
WP-004 HTTP/API Foundation
  ↓
WP-005 Authentication
  ↓
WP-006 User/Authorization Foundation
  ↓
WP-007 First Business Module
  ↓
Additional dependency-eligible business/capability packages
  ↓
Observability
Security Hardening
E2E
Deployment
Production Readiness
```

This is not a fixed graph. Disabled capabilities do not generate work packages. Enabled capabilities are ordered according to actual dependencies.

---

## 25. Build-Readiness Semantics

Build-readiness review asks:

> Can a new coding agent, with no hidden context outside this package, begin at WP-000 and proceed without making protected product, architecture, API, data, security, or deployment decisions?

The validator checks at least:

- authority consistency;
- module ownership;
- database ownership;
- machine contracts;
- error catalog;
- authentication model;
- authorization model;
- transaction boundaries;
- idempotency;
- event contracts;
- config/environment contract;
- toolchain versions;
- dependency policy;
- migration policy;
- security invariants;
- test commands;
- work-package graph;
- acceptance criteria;
- audit closure;
- release integrity prerequisites.

If an enabled capability lacks mandatory authority, `BUILD_READY=false`.

---

## 26. Final Package Shape for Generated Projects

A typical final project package shall resemble:

```text
<project>-final-spec/
├── START-HERE.md
├── AGENTS.md
├── CLAUDE.md
├── GEMINI.md
├── PACKAGE-README.md
├── Taskfile.yml
├── SHA256SUMS.txt
│
├── docs/
│   ├── core/
│   ├── agent-spec/
│   │   ├── commands/
│   │   ├── contracts/
│   │   ├── decisions/
│   │   ├── governance/
│   │   ├── modules/
│   │   ├── testing/
│   │   ├── workflows/
│   │   └── work-packages/
│   ├── audits/
│   └── design-history/
│
├── contracts/
├── schemas/
├── scripts/
│   ├── validators/
│   ├── generators/
│   └── release/
│
├── QA-AUDIT-*.md
├── QA-BUILD-READINESS-*.md
├── QA-AUDIT-DISPOSITION.md
└── SPEC-MANIFEST.*
```

The coding-agent bootstrap is:

```text
START-HERE.md
→ AGENTS.md / equivalent adapter
→ Agent Operating Manual
→ Authority Matrix
→ SPEC-MANIFEST
→ work-packages/README.md
→ WP-000
```

---

## 27. Workflow Package Blueprint

The V2.0.0 workflow release itself shall contain:

```text
ai-project-finalization-workflow-v2.0.0/
├── START-HERE.md
├── README.md
├── CHANGELOG.md
├── LICENSE
├── VERSION
├── AGENTS.md
├── CLAUDE.md
├── GEMINI.md
├── Taskfile.yml
├── pyproject.toml
├── uv.lock
├── WORKFLOW-MANIFEST.yaml
├── SHA256SUMS.txt
├── core/
├── profiles/
├── adapters/
├── schemas/
├── prompts/
├── validators/
├── generators/
├── cli/
├── tests/
├── examples/
├── docs/
├── fixtures/
└── release/
```

---

## 28. Prompt Library Design

Each AI role receives a role package containing:

- `SYSTEM-ROLE.md`
- `INPUT-CONTRACT.md`
- `OUTPUT-CONTRACT.md`
- `STOP-CONDITIONS.md`
- `QUALITY-RUBRIC.md`

Prompt roles are stored under:

```text
prompts/
├── controller/
├── discovery/
├── normalization/
├── product-architect/
├── technical-architect/
├── contract-compiler/
├── security-reviewer/
├── agent-spec-compiler/
├── wp-compiler/
├── senior-auditor/
├── corrective-agent/
├── readiness-reviewer/
└── release-reviewer/
```

Prompts must define exact output schemas and forbidden behavior. Free-form prose is insufficient when downstream automation must parse outputs.

---

## 29. Schema Inventory

V2.0.0 shall provide machine schemas for at least:

- workflow manifest;
- project;
- project state;
- profile;
- requirement;
- conflict;
- decision request;
- authority matrix;
- artifact metadata;
- module;
- ownership;
- interaction;
- command;
- test invariant;
- work package;
- work-package graph;
- audit finding;
- audit disposition;
- run record;
- change transaction;
- readiness report;
- release manifest.

All examples and fixtures must validate against the real schemas; no illustrative-only schema variants are allowed.

---

## 30. Validator Architecture

Validators are layered:

1. syntax;
2. structure;
3. references;
4. semantics;
5. authority;
6. contracts;
7. security;
8. work packages;
9. audit;
10. readiness;
11. release.

`workflow validate` runs all applicable validators.

### 30.1 Stable exit codes

The CLI shall use stable exit codes:

```text
0   PASS
10  VALIDATION_FAILED
20  HUMAN_DECISION_REQUIRED
30  INVALID_PROJECT_STATE
40  PROFILE_ERROR
50  STALE_ARTIFACTS
60  AUDIT_BLOCKERS_REMAIN
70  BUILD_READINESS_FAILED
80  RELEASE_INTEGRITY_FAILED
90  INTERNAL_WORKFLOW_ERROR
```

---

## 31. Key Validators

### 31.1 Authority validator

Checks:

- one primary authority per required subject or valid composition rule;
- correct machine authority by contract type;
- no historical authority leakage;
- adapter consistency;
- source references for generated artifacts;
- staleness.

### 31.2 Ownership/dependency validator

Builds graphs across modules, tables, commands, queries, events, jobs, and external services. Detects foreign writes, duplicate ownership, cycles, missing schemas, orphan consumers, and invalid cross-module mutations.

### 31.3 API validator

For OpenAPI projects, checks:

- parse validity;
- unique stable `operationId`;
- canonical error code references;
- explicit auth/authorization metadata;
- rate-limit semantics where required;
- idempotency metadata;
- request/response schema references;
- no public semantic operation missing its wire contract;
- no undocumented public operation.

### 31.4 Database validator

Checks semantic/physical consistency for ownership, keys, constraints, tenancy, delete behavior, migrations, declared hot paths, and outbox/inbox requirements when enabled.

### 31.5 Security validator

Checks profile-dependent completeness, for example:

- auth enabled but session/token storage undefined → fail;
- cookie credentials but CSRF disposition absent → fail;
- cross-origin credentials but origin policy absent → fail;
- multi-tenancy but tenant isolation tests absent → fail;
- file upload but content validation absent → fail;
- webhook but signature/replay policy absent → fail.

### 31.6 Work-package validator

Checks graph validity, scope constraints, authority references, acceptance commands, activated invariants, completion evidence, and protected-surface stop conditions.

### 31.7 Audit-closure validator

Checks:

```text
N findings
N unique IDs
N terminal dispositions
0 orphan dispositions
0 dispositions without findings
0 unresolved Critical blockers
0 unresolved High blockers
```

### 31.8 Release validator

Checks manifest completeness, hashes, generated staleness, archive integrity, re-extract integrity, and expected release evidence.

---

## 32. Generator Architecture

Deterministic generators include:

- manifest generator;
- adapter generator;
- module index generator;
- ownership matrix generator;
- work-package graph generator;
- audit summary generator;
- readiness report generator;
- checksum generator;
- release archive generator.

LLM-authored canonical text is produced through explicit AI roles, not hidden inside deterministic generators.

---

## 33. CLI Contract

Primary executable:

```text
workflow
```

Command tree:

```text
workflow init
workflow inspect
workflow discover
workflow normalize
workflow resolve
workflow spec
workflow architecture
workflow contracts
workflow agent-spec
workflow wp
workflow audit
workflow correct
workflow readiness
workflow validate
workflow status
workflow transition
workflow release
workflow resume
workflow decisions <list|show|resolve>
workflow change <begin|validate|close>
```

Shorthands:

```text
workflow audit-input --dry-run
workflow finalize
```

`finalize` only orchestrates normal phases. It may not bypass validators or state transitions.

---

## 34. Profile Loading and Compatibility

Each profile provides `PROFILE-MANIFEST.yaml` with:

- profile ID;
- profile version;
- core compatibility range;
- required capabilities;
- optional capabilities;
- active validators;
- schemas/templates added by the profile.

The loader fails when core/profile versions are incompatible.

---

## 35. Adapter Rules

Adapter tree:

```text
adapters/
├── generic/
├── codex/
├── claude-code/
└── gemini-antigravity/
```

Root agent files stay short. They point to canonical manuals rather than duplicating business rules.

Hard rule:

> `ADAPTER MAY REFERENCE AUTHORITY; ADAPTER MUST NOT BECOME AUTHORITY.`

---

## 36. Example Project

V2.0.0 shall ship an executable documentation project called **TeamNotes**, a small but realistic SaaS with:

- users;
- organizations;
- notes;
- sharing;
- auth;
- RBAC;
- PostgreSQL;
- email invitations;
- background notification job;
- admin;
- audit log;
- deployment;
- backup/restore.

Payments and AI are intentionally disabled to keep the baseline focused.

Example tree:

```text
examples/teamnotes/
├── raw-input/
├── expected-normalized/
├── expected-core-spec/
├── expected-contracts/
├── expected-agent-spec/
├── expected-work-packages/
├── expected-audit/
├── expected-corrective/
└── expected-final/
```

The example is executable documentation, not a toy readme.

---

## 37. Negative Fixtures

The workflow shall include invalid fixtures such as:

- duplicate authority;
- cyclic work packages;
- foreign table write;
- unresolved audit finding;
- stale OpenAPI;
- missing authorization;
- tenant table without tenant key/boundary;
- orphan event consumer;
- adapter overriding core;
- bad release hash.

Each fixture must fail for the expected error class.

---

## 38. Regression Lessons from Prior Project Work

Without embedding project-specific domain content, V2.0.0 shall encode regression cases for failure classes previously observed in complex specification work:

- flat precedence ambiguity;
- synchronous API vs asynchronous side-effect contradiction;
- cross-module ownership violation;
- missing transactional outbox/inbox infrastructure;
- event schema drift;
- internally inconsistent timeout/limit arithmetic;
- work-package gate timing errors;
- historical audit documents leaking into active authority.

These become reusable correctness fixtures.

---

## 39. Testing the Workflow Itself

The workflow test suite shall include:

- unit tests;
- schema tests;
- validator tests;
- generator tests;
- CLI tests;
- integration tests;
- golden-project tests;
- negative-fixture tests;
- release reproducibility tests.

### 39.1 LLM role evaluations

LLM roles are evaluated for:

- output-schema adherence;
- required sections;
- forbidden behavior;
- provenance retention;
- escalation of protected decisions;
- write-path boundaries.

Example evaluation:

- input: two sources conflict on account deletion;
- expected Discovery behavior: create a conflict and do not choose a winner;
- choosing a winner silently is `ROLE_EVAL_FAIL`.

---

## 40. Cross-Provider Compatibility

The workflow targets a generic agent runtime with capabilities such as:

```yaml
agent_runtime:
  capabilities:
    read_files: true
    write_files: true
    run_commands: true
    fresh_context: optional
    parallel_agents: optional
```

When fresh/parallel agents are unavailable, assurance degrades explicitly rather than being simulated.

---

## 41. Toolchain and Command Gateway

The initial implementation should use a small dependency set, targeting Python 3.12.x and a reproducible Python environment. Exact dependency versions are implementation-plan decisions within the approved dependency policy, but V2 should avoid heavy frameworks without need.

The workflow repository uses `Taskfile.yml` as its contributor command gateway with commands equivalent to:

```text
task setup
task format
task format:check
task lint
task typecheck
task test
task test:unit
task test:integration
task test:fixtures
task test:release
task qa
task release
```

The exact underlying tools are chosen in the implementation plan and pinned in the repository.

---

## 42. CI Contract

CI for the workflow must run at least:

- format check;
- lint;
- typecheck;
- unit tests;
- schema tests;
- negative fixtures;
- golden integration;
- release dry-run.

Automatic publishing is not required for V2.0.0.

---

## 43. Workflow Manifest

The release contains `WORKFLOW-MANIFEST.yaml`, conceptually:

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
  codex: 2.0.0
  claude-code: 2.0.0
  gemini-antigravity: 2.0.0
runtime:
  python: ">=3.12,<3.13"
schemas_version: 2.0.0
release:
  reproducible: true
```

The final manifest indexes normative artifacts and release metadata.

---

## 44. Release Compiler

Release assembly is deterministic wherever possible:

```text
validate source tree
→ check placeholders
→ check authority graph
→ validate schemas
→ validate machine contracts
→ validate work-package DAG
→ validate audit dispositions
→ validate build readiness
→ generate manifest
→ hash canonical artifacts
→ build staging directory
→ create ZIP
→ ZIP integrity test
→ fresh re-extract
→ verify all hashes
→ compare staged and extracted trees
→ calculate ZIP SHA-256
```

Final artifacts:

```text
ai-project-finalization-workflow-v2.0.0.zip
ai-project-finalization-workflow-v2.0.0.zip.sha256
```

---

## 45. QA Evidence for the Workflow Release

The final workflow package shall include reports equivalent to:

- `QA-CORE-ARCHITECTURE.md`
- `QA-WEB-SAAS-PROFILE.md`
- `QA-VALIDATORS.md`
- `QA-AGENT-ROLE-CONTRACTS.md`
- `QA-EXAMPLE-PROJECT.md`
- `QA-RELEASE-INTEGRITY.md`
- `QA-BUILD-READINESS.md`

If a fresh senior review is performed, include:

- `QA-SENIOR-AUDIT.md`
- `QA-SENIOR-AUDIT-DISPOSITION.md`

The reports must state whether AI-provider integration and independent review were actually performed.

---

## 46. Self-Hosting Test

The workflow shall be able to audit its own repository using applicable Generic Core rules, including:

- authority validation;
- module ownership;
- schema validity;
- command definitions;
- testing policy;
- audit closure;
- release validation.

The `web-saas` profile does not apply to the workflow repository itself because the workflow is a CLI/tooling project, not a SaaS application.

---

## 47. Definition of Done for V2.0.0

The workflow release is complete only when all applicable conditions pass:

### 47.1 Functional package scope

- Generic Core complete;
- `web-saas` profile complete;
- generic adapter complete;
- Codex adapter complete;
- Claude Code adapter complete;
- Gemini/Antigravity adapter complete;
- required schemas implemented;
- required validators implemented;
- required generators implemented;
- CLI implemented;
- TeamNotes example implemented;
- invalid fixtures implemented;
- regression fixtures implemented.

### 47.2 Mechanical gates

- all schemas validate;
- all validator tests pass;
- all positive fixtures pass;
- all negative fixtures fail for the expected reason;
- work-package compiler produces a valid acyclic graph;
- audit-closure validator is proven against positive and negative cases;
- staleness detection is proven;
- release compiler is proven;
- no unresolved Critical findings;
- no unresolved High findings;
- no unresolved protected decisions;
- ZIP integrity passes;
- fresh re-extract passes;
- checksums pass;
- staged vs extracted tree comparison passes.

### 47.3 Assurance disclosure

QA must explicitly report:

```text
AI-provider execution integration: PERFORMED / NOT PERFORMED
Independent senior review: PERFORMED / NOT PERFORMED
Runtime implementation validation of generated target app: NOT APPLICABLE TO WORKFLOW RELEASE
```

No stronger claim may be made than the evidence supports.

---

## 48. User Experience of a Future Project

A future project may begin with only:

- an idea;
- notes;
- old README files;
- draft API notes;
- a preliminary database design;
- diagrams;
- legacy documents.

The intended operator flow is:

```text
workflow init ./raw-project --profile web-saas
workflow audit-input --dry-run
workflow finalize
```

The workflow may halt at protected decisions. The user resolves those decisions and resumes:

```text
workflow decisions list
workflow decisions show DR-004
workflow decisions resolve DR-004 --choice B
workflow resume
```

The final result is a project specification release such as:

```text
my-project-final-spec-v1.0.0.zip
```

A coding agent then follows:

```text
START-HERE
→ agent adapter
→ Agent Operating Manual
→ Authority Matrix
→ SPEC-MANIFEST
→ Work Package README
→ WP-000
→ dependency-eligible READY work packages
```

The project package, not chat history, is the handoff authority.

---

## 49. Key Architectural Decisions Frozen by This Design

The following decisions are approved by the design and must not be reopened casually during implementation:

1. V2 uses **Generic Core + specialized profiles**.
2. `web-saas` is the first complete specialized profile.
3. Authority is **subject-typed**, not one flat global precedence ladder.
4. Machine-readable contracts own exact wire/shape where designated; prose owns semantics where designated.
5. Protected ambiguity becomes a Decision Request rather than an agent invention.
6. Every cross-module interaction has an explicit interaction type and transaction/failure semantics.
7. Work packages form a validated DAG and constrain implementation scope.
8. Audit findings are structured records with terminal dispositions.
9. Derived artifacts carry provenance and staleness metadata.
10. Deterministic checks are implemented as validators, not LLM opinions.
11. Final audit is separated from authoring where fresh review is possible; otherwise degraded assurance is disclosed.
12. Adapters remain thin and non-authoritative.
13. Optional `web-saas` capabilities are disabled unless enabled explicitly.
14. `BUILD_READY` is distinct from `RUNTIME_VERIFIED` and `PRODUCTION_READY`.
15. Release packaging is reproducible and includes fresh re-extract verification.
16. The workflow ships with a realistic TeamNotes example and negative/regression fixtures.
17. The workflow must be able to audit itself under applicable Generic Core rules.

---

## 50. Implementation Planning Boundary

This design intentionally freezes architecture and behavioral requirements but does not yet freeze every implementation detail. The implementation plan must define, without changing the decisions above:

- exact Python package/module layout;
- exact pinned library versions;
- CLI framework selection;
- schema implementation order;
- validator implementation order;
- test implementation sequence;
- file-by-file task breakdown;
- exact TeamNotes source corpus;
- CI provider syntax;
- release script details;
- version-control execution strategy.

Any implementation-plan choice that would alter a frozen decision in Section 49 requires returning to design review rather than silently changing the architecture.

---

## 51. Acceptance of This Design

Approval of this document authorizes creation of a detailed implementation plan for `ai-project-finalization-workflow-v2.0.0`. It does **not** yet authorize implementation before that plan is reviewed and an execution method is selected.

---

## 52. Detailed Generic Core Source Blueprint

The implementation plan shall preserve the following conceptual Core decomposition. It may split Python packages differently for maintainability, but the normative document/template responsibilities must remain recognizable and traceable.

```text
core/
├── README.md
├── CORE-MANIFEST.yaml
│
├── lifecycle/
│   ├── PROJECT-STATE-MACHINE.md
│   ├── PHASE-CONTRACTS.md
│   ├── TRANSITION-GATES.md
│   ├── FAILURE-RECOVERY.md
│   └── COMPLETION-DEFINITION.md
│
├── authority/
│   ├── SOURCE-OF-TRUTH.md
│   ├── AUTHORITY-MATRIX.yaml
│   ├── PRECEDENCE-RULES.md
│   ├── HISTORICAL-DOC-POLICY.md
│   ├── GENERATED-ARTIFACT-POLICY.md
│   └── CONFLICT-RESOLUTION.md
│
├── intake/
│   ├── INPUT-INVENTORY.md
│   ├── REQUIREMENT-EXTRACTION.md
│   ├── CONFLICT-DETECTION.md
│   ├── ASSUMPTION-REGISTER.md
│   ├── UNKNOWN-DECISIONS.md
│   └── LEGACY-CLASSIFICATION.md
│
├── core-spec/
│   ├── PRODUCT-SPEC.template.md
│   ├── TECHNICAL-SPEC.template.md
│   ├── DOMAIN-MODEL.template.md
│   ├── DATA-MODEL.template.md
│   ├── API-SEMANTICS.template.md
│   ├── SECURITY.template.md
│   ├── DEPLOYMENT.template.md
│   ├── OPERATIONS.template.md
│   ├── OBSERVABILITY.template.md
│   ├── FAILURE-MODES.template.md
│   └── NON-FUNCTIONAL-REQUIREMENTS.template.md
│
├── agent-governance/
│   ├── AGENT-OPERATING-MANUAL.template.md
│   ├── CONTROLLED-AUTONOMY.md
│   ├── STOP-CONDITIONS.md
│   ├── DECISION-REQUEST.template.md
│   ├── ADR.template.md
│   ├── CHANGE-CONTROL.md
│   ├── VERSIONING.md
│   └── GENERATED-CODE-BOUNDARIES.md
│
├── decomposition/
│   ├── MODULE-CLASSIFICATION.md
│   ├── MODULE-CONTRACT.template.md
│   ├── OWNERSHIP-MATRIX.schema.json
│   ├── DEPENDENCY-RULES.md
│   └── BOUNDARY-VALIDATION.md
│
├── contracts/
│   ├── api/
│   ├── events/
│   ├── config/
│   ├── errors/
│   ├── idempotency/
│   ├── authorization/
│   ├── transactions/
│   └── cross-module/
│
├── testing/
│   ├── TESTING-STANDARD.md
│   ├── COVERAGE-POLICY.md
│   ├── CRITICAL-INVARIANTS.template.yaml
│   ├── CONTRACT-TEST-MATRIX.template.yaml
│   ├── SECURITY-TEST-MATRIX.template.yaml
│   ├── E2E-JOURNEYS.template.yaml
│   └── PHASE-AWARE-GATES.md
│
├── work-packages/
│   ├── WORK-PACKAGE.template.md
│   ├── WP-GRAPH.schema.json
│   ├── WP-STATE-MACHINE.md
│   ├── WP-COMPILER-RULES.md
│   ├── WP-ACCEPTANCE-CONTRACT.md
│   └── WP-STOP-CONDITIONS.md
│
├── audit/
│   ├── SENIOR-AUDIT-RUBRIC.md
│   ├── FINDING.schema.json
│   ├── DISPOSITION.schema.json
│   ├── SEVERITY-MODEL.md
│   ├── CORRECTIVE-RELEASE.md
│   └── AUDIT-CLOSURE-GATE.md
│
└── release/
    ├── BUILD-READINESS.md
    ├── RELEASE-MANIFEST.schema.json
    ├── RELEASE-COMPILER.md
    ├── CHECKSUM-POLICY.md
    ├── ARCHIVE-INTEGRITY.md
    ├── REEXTRACT-VERIFICATION.md
    └── HANDOFF-CONTRACT.md
```

This structure is a minimum semantic inventory. The implementation plan may co-locate small documents only when that does not reduce independent authority, machine validation, or progressive disclosure.

---

## 53. Detailed `web-saas` Profile Blueprint

The first complete profile shall include the following conceptual structure:

```text
profiles/web-saas/
├── PROFILE-MANIFEST.yaml
├── README.md
├── PROFILE-REQUIREMENTS.md
├── PROFILE-STATE-GATES.md
│
├── architecture/
│   ├── WEB-APPLICATION-ARCHITECTURE.md
│   ├── FRONTEND-ARCHITECTURE.template.md
│   ├── BACKEND-ARCHITECTURE.template.md
│   ├── DATA-ARCHITECTURE.template.md
│   ├── INTEGRATION-ARCHITECTURE.template.md
│   ├── DEPLOYMENT-TOPOLOGY.template.md
│   └── TRUST-BOUNDARIES.template.md
│
├── capabilities/
│   ├── frontend/
│   ├── api/
│   ├── auth/
│   ├── authorization/
│   ├── users/
│   ├── organizations/
│   ├── database/
│   ├── cache/
│   ├── jobs/
│   ├── events/
│   ├── files/
│   ├── email/
│   ├── notifications/
│   ├── admin/
│   ├── search/
│   ├── analytics/
│   ├── payments/
│   ├── audit-log/
│   ├── observability/
│   └── operations/
│
├── contracts/
│   ├── http/
│   ├── sessions/
│   ├── permissions/
│   ├── pagination/
│   ├── idempotency/
│   ├── webhooks/
│   ├── jobs/
│   ├── events/
│   ├── files/
│   ├── errors/
│   └── configuration/
│
├── security/
│   ├── WEB-THREAT-MODEL.template.md
│   ├── SESSION-SECURITY.md
│   ├── API-SECURITY.md
│   ├── BROWSER-SECURITY.md
│   ├── DATA-PROTECTION.md
│   ├── SECRET-MANAGEMENT.md
│   ├── FILE-UPLOAD-SECURITY.md
│   ├── SSRF-POLICY.md
│   ├── WEBHOOK-SECURITY.md
│   └── SECURITY-INVARIANTS.yaml
│
├── database/
│   ├── DATABASE-CONTRACT.template.md
│   ├── MIGRATION-POLICY.md
│   ├── TRANSACTION-POLICY.md
│   ├── INDEX-POLICY.md
│   ├── RETENTION-POLICY.md
│   ├── OUTBOX-INBOX-PATTERN.md
│   └── BACKUP-RESTORE.md
│
├── operations/
│   ├── ENVIRONMENT-CONTRACT.template.yaml
│   ├── CONFIGURATION-POLICY.md
│   ├── HEALTH-READINESS.md
│   ├── OBSERVABILITY-STANDARD.md
│   ├── SLO.template.yaml
│   ├── INCIDENT-RUNBOOK.template.md
│   ├── DEPLOYMENT.template.md
│   └── DISASTER-RECOVERY.template.md
│
├── testing/
│   ├── WEB-SAAS-TEST-MATRIX.yaml
│   ├── BROWSER-E2E-MATRIX.yaml
│   ├── API-CONTRACT-MATRIX.yaml
│   ├── AUTH-SECURITY-MATRIX.yaml
│   ├── DATABASE-INTEGRATION-MATRIX.yaml
│   ├── JOB-EVENT-MATRIX.yaml
│   └── DEPLOYMENT-SMOKE-MATRIX.yaml
│
├── work-packages/
│   ├── WEB-SAAS-WP-RULES.md
│   ├── BOOTSTRAP-WP.template.md
│   ├── MODULE-WP.template.md
│   ├── SECURITY-WP.template.md
│   ├── DATA-WP.template.md
│   ├── UI-WP.template.md
│   └── RELEASE-WP.template.md
│
├── extensions/
│   ├── multi-tenant/
│   ├── payments/
│   ├── file-storage/
│   ├── email/
│   ├── realtime/
│   ├── search/
│   ├── ai-integration/
│   ├── background-processing/
│   ├── webhook-provider/
│   ├── analytics/
│   └── pwa/
│
└── validators/
    ├── validate_profile.py
    ├── validate_auth.py
    ├── validate_database.py
    ├── validate_openapi.py
    ├── validate_permissions.py
    ├── validate_async_contracts.py
    ├── validate_security.py
    ├── validate_operations.py
    └── validate_test_matrix.py
```

Every extension is disabled unless enabled by project capability resolution. Enabling an extension activates its documents, schemas, validators, audit rules, test requirements, and work-package compilation rules as one coherent unit.

---

## 54. Detailed Workflow Repository Inventories

### 54.1 Root schema inventory

The workflow repository shall provide, at minimum:

```text
schemas/
├── workflow-manifest.schema.json
├── project.schema.json
├── project-state.schema.json
├── profile.schema.json
├── requirement.schema.json
├── conflict.schema.json
├── decision-request.schema.json
├── authority-matrix.schema.json
├── artifact.schema.json
├── module.schema.json
├── ownership.schema.json
├── interaction.schema.json
├── command.schema.json
├── test-invariant.schema.json
├── work-package.schema.json
├── work-package-graph.schema.json
├── audit-finding.schema.json
├── audit-disposition.schema.json
├── run-record.schema.json
├── change-transaction.schema.json
├── readiness-report.schema.json
└── release-manifest.schema.json
```

### 54.2 Validator organization

```text
validators/
├── syntax/
├── structure/
├── references/
├── semantics/
├── authority/
├── contracts/
├── security/
├── work_packages/
├── audit/
├── readiness/
└── release/
```

### 54.3 Deterministic generator inventory

```text
generators/
├── manifest.py
├── adapters.py
├── module_index.py
├── ownership_matrix.py
├── work_package_graph.py
├── audit_summary.py
├── readiness_report.py
├── checksum.py
└── release_archive.py
```

### 54.4 Adapter inventory

```text
adapters/
├── generic/
├── codex/
│   ├── AGENTS.template.md
│   ├── bootstrap-prompt.md
│   ├── wp-start-prompt.md
│   ├── wp-review-prompt.md
│   └── codex-config.md
├── claude-code/
│   ├── CLAUDE.template.md
│   ├── bootstrap-prompt.md
│   ├── wp-start-prompt.md
│   └── wp-review-prompt.md
└── gemini-antigravity/
    ├── GEMINI.template.md
    ├── bootstrap-prompt.md
    ├── wp-start-prompt.md
    └── wp-review-prompt.md
```

The exact configuration filename for a provider-specific runtime may vary according to the runtime's current supported format, but its content remains non-authoritative and generated from canonical workflow configuration.

---

## 55. Command and Decision Semantics

### 55.1 Status output contract

`workflow status` must expose the current state and the next legal action without requiring an LLM to infer it. A typical output contains:

```text
Project: Acme SaaS
Profile: web-saas@2.0.0
State: CORRECTIVE_COMPLETE

Core specification       PASS
Authority graph          PASS
Machine contracts        PASS
Security review          PASS
Work-package DAG         PASS
Audit findings           41/41 terminal
Critical blockers        0
High blockers            0
Build readiness          NOT RUN

Next:
  workflow readiness
```

### 55.2 Decision commands

The CLI shall support the semantics of:

```text
workflow decisions list
workflow decisions show DR-004
workflow decisions resolve DR-004 --choice B
workflow decisions resolve DR-004 --text "user-provided resolution"
```

The exact option syntax may be refined in implementation, but the distinction between enumerated and free-text resolution must remain.

### 55.3 Change transaction commands

The CLI shall support the semantics of:

```text
workflow change begin --finding CTR-017
workflow change validate CHG-0017
workflow change close CHG-0017
```

A change cannot close while affected downstream artifacts remain stale or validators fail.

### 55.4 Dry-run

`workflow audit-input --dry-run` performs intake inspection and returns:

- missing artifact classes;
- conflicts;
- estimated phases;
- protected decisions likely required;
- profile capability proposal;

without mutating canonical project sources.

---

## 56. Final Acceptance Matrix

The implementation plan and final QA shall trace each major design obligation to evidence. At minimum, the final release must demonstrate all rows below.

| Area | Required evidence |
|---|---|
| Lifecycle | Illegal state transitions fail; legal gated transitions pass |
| Authority | Duplicate/missing/forbidden authority cases fail predictably |
| Provenance | Requirements and derived artifacts retain source references |
| Controlled autonomy | Protected ambiguity creates a Decision Request rather than an invented decision |
| Module ownership | Foreign-write and duplicate-owner fixtures fail |
| Cross-module contracts | Interaction type, transaction, idempotency, and failure semantics are representable and validated |
| Machine contracts | Positive schemas/OpenAPI pass; malformed or contradictory fixtures fail where mechanically detectable |
| Testing | Critical invariants activate by phase/work package and missing required tests are detectable |
| Work packages | DAG is acyclic, entrypoint exists, scope and dependencies validate |
| Audit | Every finding has exactly one valid terminal disposition before closure |
| Staleness | Upstream mutation marks dependent derived artifacts stale until regeneration |
| Security profile | Enabled surfaces require corresponding security dispositions/tests |
| `web-saas` extensions | Disabled extensions create no obligations; enabled extensions activate all associated obligations |
| Adapters | Root agent files remain consistent and non-authoritative |
| Review assurance | Independent vs self-review mode is reported truthfully |
| Release | Manifest, checksum, ZIP test, re-extract, and staged-tree comparison pass |
| Example | TeamNotes passes the intended positive static pipeline |
| Negative fixtures | Each invalid fixture fails for its expected error class |
| Self-hosting | Workflow repository passes applicable Generic Core validation |

This matrix is the minimum acceptance contract for V2.0.0; implementation planning may add finer-grained tests but may not weaken these obligations.
