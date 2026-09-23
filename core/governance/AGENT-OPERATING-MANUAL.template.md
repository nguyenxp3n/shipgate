# Agent Operating Manual

This manual governs coding agents implementing a finalized project package. Canonical product, security, data, API, and deployment authority lives in the Authority Matrix and referenced specifications/contracts; this manual governs how an agent works with that authority.

## Bootstrap order

1. Read this Agent Operating Manual.
2. Read the Authority Matrix.
3. Read SPEC-MANIFEST.
4. Read `work-packages/README.md`.
5. Select the dependency-eligible READY Work Package; `WP-000` is the initial entry point.
6. Read only that Work Package plus its referenced module/contracts/global constraints.

## Controlled autonomy

### Level 1 — FREE

Local names, private helper layout, comments, test helper arrangement, and small internal refactors are free decisions when they do not change public behavior or protected contracts.

### Level 2 — CONSTRAINED

Internal package layout, query implementation, internal algorithms, derived caches, and dependencies already allowed by policy may be selected within the frozen architecture and Work Package scope. Record material implementation rulings in the execution ledger.

### Level 3 — PROTECTED

Public interfaces, persistent schema/migrations, security/authorization/privacy/retention, business rules/state machines, cross-module events, external providers, deployment topology, irreversible data operations, and other authority-bearing decisions are protected. Unknown protected requirements are not permission to invent.

A protected ambiguity requires a **Decision Request** or an approved change/ADR. Stop the affected Work Package until authority is resolved.

## Authority discipline

Machine-readable contracts own the wire/structured shape assigned by the Authority Matrix; normative prose owns the business/security/transaction meaning assigned to it. Generated artifacts remain derived and carry source/hash provenance. A **historical audit** is advisory evidence only. Never implement directly from historical findings when canonical authority does not contain the accepted resolution.

## Work Package protocol

Execute READY work only after all declared **dependency** IDs are complete. Respect allowed/forbidden paths, interfaces consumed/produced, schema/security impact, activated invariants, acceptance commands, required evidence, and stop conditions. A Work Package does not authorize unrelated refactoring or future optional capabilities.

Use the project **command gateway** (normally `Taskfile.yml`) instead of inventing parallel ad-hoc command paths. Run each Work Package acceptance command and preserve evidence before marking it complete.

## Assurance states

- `SPEC_COMPLETE`: canonical specification exists but may not yet be executable by an autonomous coding agent.
- `AGENT_SPEC_READY`: agent governance/contracts exist.
- `BUILD_READY`: a fresh coding agent can start at WP-000 without protected guesses.
- `RUNTIME_VERIFIED`: the implemented runtime has passed its required build/integration/runtime checks.
- `PRODUCTION_READY`: deployment, operations, security, recovery, and production gates have passed.

`BUILD_READY` never implies `RUNTIME_VERIFIED` or `PRODUCTION_READY`.

## Stop conditions

Stop before destructive/irreversible operations, protected authority changes, security-sensitive actions outside approved contracts, shared-branch/publish side effects that require human approval, or any plan so incomplete that continuing would be a guess. When a Work Package discovers a protected change, create/consume the approved Decision Request or change transaction before resuming.
