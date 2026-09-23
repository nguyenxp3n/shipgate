# AI Project Finalization Workflow V2 Web-SaaS and Agent Roles Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Implement the complete `web-saas@2.0.0` profile, capability/extension activation, profile-specific validation rules, agent-role contracts, orchestration metadata, and thin adapters for generic agents, Codex, Claude Code, and Gemini/Antigravity.

**Architecture:** Keep all web-specific obligations under `profiles/web-saas/`. The Generic Core sees the profile only through its manifest, capability set, schemas/templates, and validator registration. Agent roles are static role packages plus machine-readable registry metadata; V2 does not embed proprietary provider APIs. Adapters generate bootstrap files that point back to canonical workflow/project authority and are mechanically checked for drift.

**Tech Stack:** Python 3.12; existing manifest/profile/validator/generator APIs; YAML/Markdown static assets; pytest.

**Spec:** `docs/superpowers/specs/shipgate-architecture-spec.md`

## Global Constraints

- Profile ID/version are exactly `web-saas@2.0.0` and compatible with Core `>=2.0,<3.0`.
- Capabilities have only `required`, `optional_enabled`, or `disabled` states.
- Disabled extensions create no schema/test/WP obligations and coding agents must not add them speculatively.
- Enabled extensions activate their documentation, validators, test obligations, audit rules, and WP rules as a coherent unit.
- Frontend/UI authorization is never authoritative; backend authorization remains authoritative.
- Cache/search/analytics indexes are derived unless the project explicitly establishes another authority model.
- Cookie credentials require explicit CSRF disposition; cross-origin credentials require explicit CORS origin policy.
- Multi-tenant projects require explicit tenant boundary and tests.
- Async/event capabilities require retry/idempotency/dead-letter/ordering semantics appropriate to the interaction.
- AI extension is disabled by default and may not silently make AI authoritative over protected business/security state.
- Adapter files are bootstraps only and cannot carry unique product truth.
- Senior Auditor role is read-only with respect to canonical project artifacts.

## Review Focus

- Enabling an extension must activate all of its obligations atomically; partial activation must fail profile validation.
- Disabling an extension after artifacts already exist must mark those artifacts stale/out-of-scope rather than leave hidden obligations.
- Cookie/session combinations that omit CSRF or secure-cookie policy must fail with a stable security issue code.
- Adapter generation must not copy stale product text or create contradictory instructions across AGENTS/CLAUDE/GEMINI files.
- Role output with prose instead of the required machine contract must fail validation rather than be heuristically parsed.

---

### Task 1: Create the `web-saas` profile manifest and capability resolver

**Files:**
- Create: `profiles/web-saas/PROFILE-MANIFEST.yaml`
- Create: `profiles/web-saas/README.md`
- Create: `profiles/web-saas/PROFILE-REQUIREMENTS.md`
- Create: `profiles/web-saas/PROFILE-STATE-GATES.md`
- Create: `src/project_finalizer/web_saas/__init__.py`
- Create: `src/project_finalizer/web_saas/capabilities.py`
- Create: `tests/unit/web_saas/test_capabilities.py`

**Interfaces:**
- Consumes: `ProfileManifest`.
- Produces: `CapabilityState`, `CapabilitySet.resolve`, `enabled(name)`, `obligation_sets()`.

- [ ] **Step 1: Write failing state/activation tests**

```python
# tests/unit/web_saas/test_capabilities.py
import pytest

from project_finalizer.web_saas.capabilities import CapabilitySet


def test_disabled_extension_has_no_obligations():
    caps = CapabilitySet.from_mapping({"payments": "disabled"})
    assert caps.enabled("payments") is False
    assert "payments" not in caps.obligation_sets()


def test_unknown_capability_state_is_rejected():
    with pytest.raises(ValueError, match="capability state"):
        CapabilitySet.from_mapping({"payments": "maybe"})
```

- [ ] **Step 2: Run RED**

```bash
uv run pytest tests/unit/web_saas/test_capabilities.py -q
```

- [ ] **Step 3: Implement three-state resolver**

`required` and `optional_enabled` count as enabled; `disabled` does not. Required profile capabilities are `frontend`, `api`, `auth`, `authorization`, `database`, `observability`. Optional inventory includes organizations, cache, jobs, events, files, email, notifications, admin, search, analytics, payments, ai_integration, realtime, pwa, webhooks.

- [ ] **Step 4: Create `PROFILE-MANIFEST.yaml`**

Declare core compatibility `>=2.0,<3.0`, required/optional capabilities, extension directory names, and profile validator names.

- [ ] **Step 5: Run GREEN and commit**

```bash
uv run pytest tests/unit/web_saas/test_capabilities.py -q
git add profiles/web-saas src/project_finalizer/web_saas tests/unit/web_saas
git commit -m "feat: add web-saas capability resolution"
```

---

### Task 2: Add full web-saas architecture, security, database, operations, testing, and WP asset inventory

**Files:**
- Create architecture files:
  - `profiles/web-saas/architecture/WEB-APPLICATION-ARCHITECTURE.md`
  - `profiles/web-saas/architecture/FRONTEND-ARCHITECTURE.template.md`
  - `profiles/web-saas/architecture/BACKEND-ARCHITECTURE.template.md`
  - `profiles/web-saas/architecture/DATA-ARCHITECTURE.template.md`
  - `profiles/web-saas/architecture/INTEGRATION-ARCHITECTURE.template.md`
  - `profiles/web-saas/architecture/DEPLOYMENT-TOPOLOGY.template.md`
  - `profiles/web-saas/architecture/TRUST-BOUNDARIES.template.md`
- Create `CAPABILITY.md` and `CAPABILITY.yaml` in each exact capability directory:
  - `profiles/web-saas/capabilities/frontend/`
  - `profiles/web-saas/capabilities/api/`
  - `profiles/web-saas/capabilities/auth/`
  - `profiles/web-saas/capabilities/authorization/`
  - `profiles/web-saas/capabilities/users/`
  - `profiles/web-saas/capabilities/organizations/`
  - `profiles/web-saas/capabilities/database/`
  - `profiles/web-saas/capabilities/cache/`
  - `profiles/web-saas/capabilities/jobs/`
  - `profiles/web-saas/capabilities/events/`
  - `profiles/web-saas/capabilities/files/`
  - `profiles/web-saas/capabilities/email/`
  - `profiles/web-saas/capabilities/notifications/`
  - `profiles/web-saas/capabilities/admin/`
  - `profiles/web-saas/capabilities/search/`
  - `profiles/web-saas/capabilities/analytics/`
  - `profiles/web-saas/capabilities/payments/`
  - `profiles/web-saas/capabilities/audit-log/`
  - `profiles/web-saas/capabilities/observability/`
  - `profiles/web-saas/capabilities/operations/`
- Create contract files:
  - `profiles/web-saas/contracts/http/HTTP-CONTRACT.md`
  - `profiles/web-saas/contracts/sessions/SESSION-CONTRACT.md`
  - `profiles/web-saas/contracts/permissions/PERMISSION-CATALOG.template.yaml`
  - `profiles/web-saas/contracts/pagination/PAGINATION-CONTRACT.md`
  - `profiles/web-saas/contracts/idempotency/IDEMPOTENCY-CONTRACT.md`
  - `profiles/web-saas/contracts/webhooks/WEBHOOK-CONTRACT.md`
  - `profiles/web-saas/contracts/jobs/JOB-CONTRACT.md`
  - `profiles/web-saas/contracts/events/EVENT-CONTRACT.md`
  - `profiles/web-saas/contracts/files/FILE-CONTRACT.md`
  - `profiles/web-saas/contracts/errors/ERROR-CATALOG.template.yaml`
  - `profiles/web-saas/contracts/configuration/CONFIGURATION-CONTRACT.md`
- Create security files:
  - `profiles/web-saas/security/WEB-THREAT-MODEL.template.md`
  - `profiles/web-saas/security/SESSION-SECURITY.md`
  - `profiles/web-saas/security/API-SECURITY.md`
  - `profiles/web-saas/security/BROWSER-SECURITY.md`
  - `profiles/web-saas/security/DATA-PROTECTION.md`
  - `profiles/web-saas/security/SECRET-MANAGEMENT.md`
  - `profiles/web-saas/security/FILE-UPLOAD-SECURITY.md`
  - `profiles/web-saas/security/SSRF-POLICY.md`
  - `profiles/web-saas/security/WEBHOOK-SECURITY.md`
  - `profiles/web-saas/security/SECURITY-INVARIANTS.yaml`
- Create database files:
  - `profiles/web-saas/database/DATABASE-CONTRACT.template.md`
  - `profiles/web-saas/database/MIGRATION-POLICY.md`
  - `profiles/web-saas/database/TRANSACTION-POLICY.md`
  - `profiles/web-saas/database/INDEX-POLICY.md`
  - `profiles/web-saas/database/RETENTION-POLICY.md`
  - `profiles/web-saas/database/OUTBOX-INBOX-PATTERN.md`
  - `profiles/web-saas/database/BACKUP-RESTORE.md`
- Create operations files:
  - `profiles/web-saas/operations/ENVIRONMENT-CONTRACT.template.yaml`
  - `profiles/web-saas/operations/CONFIGURATION-POLICY.md`
  - `profiles/web-saas/operations/HEALTH-READINESS.md`
  - `profiles/web-saas/operations/OBSERVABILITY-STANDARD.md`
  - `profiles/web-saas/operations/SLO.template.yaml`
  - `profiles/web-saas/operations/INCIDENT-RUNBOOK.template.md`
  - `profiles/web-saas/operations/DEPLOYMENT.template.md`
  - `profiles/web-saas/operations/DISASTER-RECOVERY.template.md`
- Create testing files:
  - `profiles/web-saas/testing/WEB-SAAS-TEST-MATRIX.yaml`
  - `profiles/web-saas/testing/BROWSER-E2E-MATRIX.yaml`
  - `profiles/web-saas/testing/API-CONTRACT-MATRIX.yaml`
  - `profiles/web-saas/testing/AUTH-SECURITY-MATRIX.yaml`
  - `profiles/web-saas/testing/DATABASE-INTEGRATION-MATRIX.yaml`
  - `profiles/web-saas/testing/JOB-EVENT-MATRIX.yaml`
  - `profiles/web-saas/testing/DEPLOYMENT-SMOKE-MATRIX.yaml`
- Create work-package files:
  - `profiles/web-saas/work-packages/WEB-SAAS-WP-RULES.md`
  - `profiles/web-saas/work-packages/BOOTSTRAP-WP.template.md`
  - `profiles/web-saas/work-packages/MODULE-WP.template.md`
  - `profiles/web-saas/work-packages/SECURITY-WP.template.md`
  - `profiles/web-saas/work-packages/DATA-WP.template.md`
  - `profiles/web-saas/work-packages/UI-WP.template.md`
  - `profiles/web-saas/work-packages/RELEASE-WP.template.md`
- Create: `tests/profile/test_web_saas_inventory.py`
- Create: `tests/profile/test_web_saas_static_content.py`

**Interfaces:**
- Consumes: approved design Section 23/53.
- Produces: normative/templates assets referenced by the profile manifest.

- [ ] **Step 1: Write failing required-inventory test**

```python
# tests/profile/test_web_saas_inventory.py
REQUIRED_FILES = {
    "architecture/WEB-APPLICATION-ARCHITECTURE.md",
    "architecture/FRONTEND-ARCHITECTURE.template.md",
    "architecture/BACKEND-ARCHITECTURE.template.md",
    "security/WEB-THREAT-MODEL.template.md",
    "security/SESSION-SECURITY.md",
    "security/API-SECURITY.md",
    "security/BROWSER-SECURITY.md",
    "security/SECURITY-INVARIANTS.yaml",
    "database/DATABASE-CONTRACT.template.md",
    "database/MIGRATION-POLICY.md",
    "database/OUTBOX-INBOX-PATTERN.md",
    "operations/ENVIRONMENT-CONTRACT.template.yaml",
    "operations/HEALTH-READINESS.md",
    "operations/DISASTER-RECOVERY.template.md",
    "testing/WEB-SAAS-TEST-MATRIX.yaml",
    "testing/AUTH-SECURITY-MATRIX.yaml",
    "work-packages/WEB-SAAS-WP-RULES.md",
    "work-packages/BOOTSTRAP-WP.template.md",
}


def test_required_web_saas_files_exist(repo_root):
    root = repo_root / "profiles/web-saas"
    missing = sorted(path for path in REQUIRED_FILES if not (root / path).exists())
    assert missing == []
```

- [ ] **Step 2: Write failing semantic-marker tests**

Static content tests assert:

- `BROWSER-SECURITY.md` contains explicit sections for CSP, CORS, CSRF, XSS, clickjacking, referrer policy, permissions policy, open redirects, service worker/private caching;
- `MIGRATION-POLICY.md` contains expand/migrate/contract and forward-fix semantics;
- `OUTBOX-INBOX-PATTERN.md` requires idempotent consumers and no application Docker-socket assumptions;
- `HEALTH-READINESS.md` distinguishes liveness from readiness;
- `WEB-SAAS-WP-RULES.md` requires WP-000 and protected-surface stop conditions.

- [ ] **Step 3: Run RED**

```bash
uv run pytest tests/profile/test_web_saas_inventory.py tests/profile/test_web_saas_static_content.py -q
```

- [ ] **Step 4: Author architecture and contracts templates**

Keep fields project-resolvable rather than embedding a stack choice. Templates must ask for exact rendering model, routing/auth bootstrap, API base/versioning/error/idempotency semantics, database ownership/tenancy/retention, deployment topology/trust boundaries, and failure modes.

- [ ] **Step 5: Author security/database/operations/test assets**

Do not insert project-specific numeric limits as generic defaults when the approved design says the project must decide them. Where an exact disposition is required, provide a closed-choice field plus a rationale/evidence field.

- [ ] **Step 6: Run GREEN and commit**

```bash
uv run pytest tests/profile/test_web_saas_inventory.py tests/profile/test_web_saas_static_content.py -q
git add profiles/web-saas tests/profile
git commit -m "docs: add complete web-saas profile assets"
```

---

### Task 3: Implement web-saas auth, browser-security, permission, database, async, operations, and test-matrix validators

**Files:**
- Create: `src/project_finalizer/web_saas/validators/__init__.py`
- Create: `src/project_finalizer/web_saas/validators/auth.py`
- Create: `src/project_finalizer/web_saas/validators/security.py`
- Create: `src/project_finalizer/web_saas/validators/permissions.py`
- Create: `src/project_finalizer/web_saas/validators/database.py`
- Create: `src/project_finalizer/web_saas/validators/async_contracts.py`
- Create: `src/project_finalizer/web_saas/validators/operations.py`
- Create: `src/project_finalizer/web_saas/validators/test_matrix.py`
- Create: `tests/unit/web_saas/validators/test_auth.py`
- Create: `tests/unit/web_saas/validators/test_security.py`
- Create: `tests/unit/web_saas/validators/test_database.py`
- Create: `tests/unit/web_saas/validators/test_async.py`
- Create: `tests/unit/web_saas/validators/test_test_matrix.py`

**Interfaces:**
- Consumes: `ValidationContext`, capability set, project profile records.
- Produces: profile issue codes prefixed `WS_AUTH_`, `WS_SEC_`, `WS_DB_`, `WS_ASYNC_`, `WS_TEST_`, `WS_OPS_`.

- [ ] **Step 1: Write failing cookie/CSRF test**

```python
# tests/unit/web_saas/validators/test_auth.py
from project_finalizer.web_saas.validators.auth import AuthValidator


def test_cookie_credentials_require_csrf_disposition(web_context_factory):
    ctx = web_context_factory(
        auth={"credential_transport": "cookie", "csrf": None},
    )
    report = AuthValidator().validate(ctx)
    assert "WS_AUTH_CSRF_REQUIRED" in {i.code for i in report.issues}
```

- [ ] **Step 2: Write failing multi-tenant isolation test**

When `multi_tenant` is enabled and a tenant-owned entity lacks tenant key/enforcement plus a tenant-isolation test, report both semantic and test obligations.

- [ ] **Step 3: Write failing async obligation test**

When events/jobs are enabled, missing idempotency/retry/failure/dead-letter dispositions produces stable `WS_ASYNC_*` findings.

- [ ] **Step 4: Write failing file/webhook/SSRF applicability tests**

Enabled surface requires corresponding policy; disabled surface creates no obligation. `NOT_APPLICABLE` must include evidence when a security surface is explicitly evaluated as absent.

- [ ] **Step 5: Run RED**

```bash
uv run pytest tests/unit/web_saas/validators -q
```

- [ ] **Step 6: Implement validators by capability**

Each validator first checks applicability from `CapabilitySet`; it must not emit errors for disabled capabilities. Reuse Generic Core issue/report types and registry.

- [ ] **Step 7: Implement phase-aware test-matrix validation**

Critical invariant entries declare `active_from_wp`; once a WP at/after that point is READY/complete, required test classes must exist. Do not require all future tests at repository bootstrap.

- [ ] **Step 8: Run GREEN and commit**

```bash
uv run pytest tests/unit/web_saas/validators -q
git add src/project_finalizer/web_saas/validators tests/unit/web_saas/validators
git commit -m "feat: validate web-saas security and data obligations"
```

---

### Task 4: Implement optional extension activation as all-or-nothing obligation packs

**Files:**
- For each exact extension directory below, create `EXTENSION-MANIFEST.yaml`, `REQUIREMENTS.md`, `TESTING.yaml`, `AUDIT-RULES.yaml`, and `WORK-PACKAGE-RULES.md`:
  - `profiles/web-saas/extensions/multi-tenant/`
  - `profiles/web-saas/extensions/payments/`
  - `profiles/web-saas/extensions/file-storage/`
  - `profiles/web-saas/extensions/email/`
  - `profiles/web-saas/extensions/realtime/`
  - `profiles/web-saas/extensions/search/`
  - `profiles/web-saas/extensions/ai-integration/`
  - `profiles/web-saas/extensions/background-processing/`
  - `profiles/web-saas/extensions/webhook-provider/`
  - `profiles/web-saas/extensions/analytics/`
  - `profiles/web-saas/extensions/pwa/`
- Create: `src/project_finalizer/web_saas/extensions.py`
- Create: `tests/unit/web_saas/test_extensions.py`
- Create: `tests/profile/test_extension_inventory.py`

**Interfaces:**
- Consumes: capability resolver and profile manifest.
- Produces: `ExtensionManifest`, `ExtensionRegistry.active_obligations(capabilities)`.

- [ ] **Step 1: Write failing partial-extension test**

```python
# tests/unit/web_saas/test_extensions.py
import pytest

from project_finalizer.web_saas.extensions import ExtensionRegistry


def test_enabled_extension_missing_validator_is_rejected(tmp_path):
    # fixture manifest declares docs/schema/tests but omits validator
    registry = ExtensionRegistry(tmp_path)
    with pytest.raises(ValueError, match="incomplete extension obligation pack"):
        registry.load_enabled({"payments": "optional_enabled"})
```

- [ ] **Step 2: Write disabled-extension no-obligation test**

Assert disabled payments produces no payment validator, test matrix, WP template, or audit rule activation.

- [ ] **Step 3: Run RED**

```bash
uv run pytest tests/unit/web_saas/test_extensions.py tests/profile/test_extension_inventory.py -q
```

- [ ] **Step 4: Implement manifest format and registry**

Each extension manifest lists `documents`, `schemas`, `validators`, `testing`, `audit_rules`, and `work_package_rules`. All lists must resolve when enabled.

- [ ] **Step 5: Author minimum normative extension assets**

Specific frozen rules:

- payments: provider state and application entitlement state are distinct; webhook signature/replay/dedup/out-of-order/reconciliation required;
- AI: provider/model role, external data/PII, cost/rate/fallback/output validation and authority boundary required; AI is non-authoritative by default;
- realtime: connection auth/authorization/reconnect/order/backpressure required;
- search: authoritative source, indexing/reindex/delete/recovery/versioning required;
- PWA: private data cache policy required.

- [ ] **Step 6: Run GREEN and commit**

```bash
uv run pytest tests/unit/web_saas/test_extensions.py tests/profile/test_extension_inventory.py -q
git add profiles/web-saas/extensions src/project_finalizer/web_saas/extensions.py tests
git commit -m "feat: add web-saas extension obligation packs"
```

---

### Task 5: Implement agent-role registry and machine-checkable role packages

**Files:**
- Create: `prompts/ROLE-REGISTRY.yaml`
- Create role directories for:
  - `controller`
  - `discovery`
  - `normalization`
  - `product-architect`
  - `technical-architect`
  - `contract-compiler`
  - `security-reviewer`
  - `agent-spec-compiler`
  - `wp-compiler`
  - `senior-auditor`
  - `corrective-agent`
  - `readiness-reviewer`
  - `release-reviewer`
- In each role directory create:
  - `SYSTEM-ROLE.md`
  - `INPUT-CONTRACT.md`
  - `OUTPUT-CONTRACT.md`
  - `STOP-CONDITIONS.md`
  - `QUALITY-RUBRIC.md`
- Create: `src/project_finalizer/agents/__init__.py`
- Create: `src/project_finalizer/agents/registry.py`
- Create: `src/project_finalizer/agents/packets.py`
- Create: `src/project_finalizer/agents/runtime.py`
- Create: `tests/unit/agents/test_registry.py`
- Create: `tests/unit/agents/test_runtime.py`
- Create: `tests/unit/agents/test_packets.py`

**Interfaces:**
- Consumes: role registry YAML, authority/ownership paths.
- Produces: `AgentRole`, `RoleRegistry`, `RolePacket`, `build_role_packet(project_root, role_id)`.

- [ ] **Step 1: Write failing write-boundary test**

```python
# tests/unit/agents/test_registry.py
from project_finalizer.agents.registry import RoleRegistry


def test_senior_auditor_is_read_only_for_canonical_sources(repo_root):
    registry = RoleRegistry.load(repo_root / "prompts/ROLE-REGISTRY.yaml")
    role = registry.get("senior-auditor")
    assert role.can_write("docs/audits/QA.md") is True
    assert role.can_write("contracts/openapi/openapi.yaml") is False
```

- [ ] **Step 2: Write failing packet minimal-context test**

A WP compiler packet must include its role contract, approved canonical inputs, and expected output paths, but must not automatically include `docs/audits/historical/**` unless the role explicitly requests historical evidence.

- [ ] **Step 3: Run RED**

```bash
uv run pytest tests/unit/agents -q
```

- [ ] **Step 4: Implement registry model**

Role metadata includes read globs, write globs, forbidden globs, required inputs, output contract path, fresh-context preference, and whether canonical project writes are allowed.

- [ ] **Step 5: Author role contracts**

Critical behaviors:

- Discovery records conflicts and does not choose authority;
- Product Architect cannot choose infrastructure stack;
- Technical Architect cannot alter product behavior to simplify architecture;
- Contract Compiler cannot invent unsupported public endpoints;
- Senior Auditor assumes structural defects may exist and is source-read-only;
- Corrective Agent triages recommendations rather than blindly applying them;
- Readiness Reviewer simulates a fresh coding agent and fails on protected guesses;
- Release Reviewer verifies evidence and assurance wording.

- [ ] **Step 6: Implement provider-capability runtime metadata**

Define:

```python
@dataclass(frozen=True)
class AgentRuntimeCapabilities:
    read_files: bool
    write_files: bool
    run_commands: bool
    fresh_context: bool
    parallel_agents: bool
```

V2 ships a provider-neutral `ExternalAgentRuntime` that prepares role packets and validates imported outputs; it performs no network/API call. A runtime reporting `fresh_context=False` must force assurance metadata to `independent_review=false`; the system may not simulate independence.

- [ ] **Step 7: Run GREEN and commit**

```bash
uv run pytest tests/unit/agents -q
git add prompts src/project_finalizer/agents tests/unit/agents
git commit -m "feat: define isolated AI agent role contracts"
```

---

### Task 6: Implement generic, Codex, Claude Code, and Gemini/Antigravity adapters

**Files:**
- Create: `adapters/generic/AGENT.template.md`
- Create: `adapters/codex/AGENTS.template.md`
- Create: `adapters/codex/bootstrap-prompt.md`
- Create: `adapters/codex/wp-start-prompt.md`
- Create: `adapters/codex/wp-review-prompt.md`
- Create: `adapters/codex/codex-config.md`
- Create: `adapters/claude-code/CLAUDE.template.md`
- Create: `adapters/claude-code/bootstrap-prompt.md`
- Create: `adapters/claude-code/wp-start-prompt.md`
- Create: `adapters/claude-code/wp-review-prompt.md`
- Create: `adapters/gemini-antigravity/GEMINI.template.md`
- Create: `adapters/gemini-antigravity/bootstrap-prompt.md`
- Create: `adapters/gemini-antigravity/wp-start-prompt.md`
- Create: `adapters/gemini-antigravity/wp-review-prompt.md`
- Create: `src/project_finalizer/generators/adapters.py`
- Create: `src/project_finalizer/validators/adapters.py`
- Create: `tests/unit/generators/test_adapters.py`
- Create: `tests/unit/validators/test_adapters.py`

**Interfaces:**
- Consumes: project manifest, canonical Agent Operating Manual path, Authority Matrix path, SPEC-MANIFEST, WP README.
- Produces: generated root bootstrap files; adapter consistency validator.

- [ ] **Step 1: Write failing canonical-reference test**

Generate all adapters for a fixture and assert each contains the exact bootstrap order:

```text
Agent Operating Manual
Authority Matrix
SPEC-MANIFEST
work-packages/README.md
WP-000
```

- [ ] **Step 2: Write failing unique-product-truth test**

Create a corrupted adapter fixture containing a business rule string not referenced from canonical paths; validator must emit `ADAPTER_NONCANONICAL_TRUTH`.

- [ ] **Step 3: Run RED**

```bash
uv run pytest tests/unit/generators/test_adapters.py tests/unit/validators/test_adapters.py -q
```

- [ ] **Step 4: Implement adapter rendering with a tiny explicit substitution map**

Do not introduce a template engine dependency. Use fixed marker replacement for project name, canonical paths, command gateway, and version. Reject unknown/unfilled markers.

- [ ] **Step 5: Implement adapter consistency validator**

Adapters may contain environment-specific operating instructions but no unique product/API/database/security claims. Enforce known required references and forbid copied historical audit text.

- [ ] **Step 6: Run GREEN and commit**

```bash
uv run pytest tests/unit/generators/test_adapters.py tests/unit/validators/test_adapters.py -q
git add adapters src/project_finalizer/generators/adapters.py src/project_finalizer/validators/adapters.py tests
git commit -m "feat: generate consistent coding-agent adapters"
```

---

### Task 7: Create Generic Core Agent Operating Manual and generated-project bootstrap templates

**Files:**
- Create: `core/governance/AGENT-OPERATING-MANUAL.template.md`
- Create: `core/specification/PRODUCT-SPEC.template.md`
- Create: `core/specification/TECHNICAL-SPEC.template.md`
- Create: `core/specification/DOMAIN-MODEL.template.md`
- Create: `core/specification/DATA-MODEL.template.md`
- Create: `core/specification/API-SEMANTICS.template.md`
- Create: `core/specification/SECURITY.template.md`
- Create: `core/specification/DEPLOYMENT.template.md`
- Create: `core/specification/OPERATIONS.template.md`
- Create: `core/specification/OBSERVABILITY.template.md`
- Create: `core/specification/FAILURE-MODES.template.md`
- Create: `core/specification/NON-FUNCTIONAL-REQUIREMENTS.template.md`
- Create: `core/testing/TESTING-STANDARD.md`
- Create: `core/testing/COVERAGE-POLICY.md`
- Create: `core/testing/CRITICAL-INVARIANTS.template.yaml`
- Create: `core/testing/CONTRACT-TEST-MATRIX.template.yaml`
- Create: `core/testing/SECURITY-TEST-MATRIX.template.yaml`
- Create: `core/testing/E2E-JOURNEYS.template.yaml`
- Create: `core/testing/PHASE-AWARE-GATES.md`
- Create: `tests/core/test_core_asset_inventory.py`

**Interfaces:**
- Consumes: approved design Sections 9, 10, 14, 25, 26.
- Produces: canonical generated-project templates referenced by role/adapters.

- [ ] **Step 1: Write failing core inventory test**

List every file above and assert it exists.

- [ ] **Step 2: Write semantic-marker tests**

Assert the manual contains controlled-autonomy levels, protected-decision stop rule, historical-audit warning, command-gateway rule, WP dependency rule, and assurance-state definitions.

- [ ] **Step 3: Run RED**

```bash
uv run pytest tests/core/test_core_asset_inventory.py -q
```

- [ ] **Step 4: Author templates without web assumptions**

Do not mention cookie/CORS/PostgreSQL/React in Generic Core templates except as non-normative examples explicitly labeled examples.

- [ ] **Step 5: Run GREEN and profile isolation test**

Add a test that greps generic core normative assets for forbidden web-specific authority terms in normative statements; allow examples only in fenced/example-labeled sections.

- [ ] **Step 6: Run full Web-SaaS/Agent verification gate**

```bash
task format:check
task lint
task typecheck
task test
uv run pytest tests/profile tests/core -q
git diff --check
```

- [ ] **Step 7: Commit**

```bash
git add core/specification core/governance/AGENT-OPERATING-MANUAL.template.md core/testing tests/core
git commit -m "docs: complete core agent handoff templates"
```

---

## Web-SaaS and Agent Roles completion evidence

Record:

```text
web-saas profile manifest compatible: PASS
Required profile assets present: PASS
Disabled extension obligations: 0
Enabled extension obligation pack completeness: PASS
Cookie/CSRF and CORS security rules: PASS
Tenant isolation gate: PASS
Async idempotency/retry/failure rules: PASS
All 13 role packages complete: PASS
Senior Auditor canonical writes: DENIED
Adapters reference same canonical bootstrap order: PASS
Adapter unique product truth: 0
Generic Core web-specific normative dependency: 0
```
