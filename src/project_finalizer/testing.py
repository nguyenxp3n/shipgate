from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path
from types import SimpleNamespace
from typing import Any

import yaml
from jsonschema import Draft202012Validator

from project_finalizer.audit import AuditLedger
from project_finalizer.models import ValidationIssue
from project_finalizer.readiness import ReadinessInputs, evaluate_build_readiness
from project_finalizer.validation import build_default_registry
from project_finalizer.validators import ValidationContext, ValidatorRegistry
from project_finalizer.web_saas.validators import (
    AsyncContractsValidator,
    AuthValidator,
    DatabaseValidator,
    OperationsValidator,
    PermissionsValidator,
    SecurityValidator,
    TestMatrixValidator,
)


@dataclass(frozen=True)
class StaticProjectResult:
    issues: tuple[ValidationIssue, ...]
    build_readiness: str

    @property
    def ok(self) -> bool:
        return not self.issues and self.build_readiness == "PASS"

    @property
    def issue_codes(self) -> tuple[str, ...]:
        return tuple(issue.code for issue in self.issues)

    def format_issues(self) -> str:
        if not self.issues:
            return "no validation issues"
        return "\n".join(
            f"{issue.code}: {issue.message}"
            + (f" [{issue.path}]" if issue.path else "")
            + (f" ({issue.subject_id})" if issue.subject_id else "")
            for issue in self.issues
        )


def _load_yaml(path: Path) -> dict[str, Any]:
    raw = yaml.safe_load(path.read_text(encoding="utf-8"))
    return dict(raw) if isinstance(raw, dict) else {}


def _teamnotes_context(project_root: Path) -> tuple[ValidationContext, list[dict[str, Any]], dict[str, Any]]:
    module_dir = project_root / "expected-agent-spec/modules"
    modules = tuple(_load_yaml(path) for path in sorted(module_dir.glob("*.yaml")))
    graph = _load_yaml(project_root / "expected-work-packages/graph.yaml")
    work_packages = [dict(item) for item in graph.get("work_packages", []) if isinstance(item, dict)]
    errors = _load_yaml(project_root / "expected-contracts/error-catalog.yaml")
    error_catalog = frozenset(str(value) for value in errors.get("errors", []))
    ctx = ValidationContext(
        project_root=project_root,
        authority_matrix_path=project_root / "expected-agent-spec/AUTHORITY-MATRIX.yaml",
        modules=modules,
        work_packages=tuple(work_packages),
        openapi_path=project_root / "expected-contracts/openapi.yaml",
        error_catalog=error_catalog,
        api_policy={"require_auth_metadata": True, "require_idempotency_metadata": True},
    )
    profile = _load_yaml(project_root / "expected-final/validation-inputs.yaml")
    return ctx, work_packages, profile


def _validate_event_schemas(project_root: Path) -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []
    for path in sorted((project_root / "expected-contracts/events").glob("*.schema.json")):
        try:
            document = json.loads(path.read_text(encoding="utf-8"))
            Draft202012Validator.check_schema(document)
        except Exception as exc:
            issues.append(
                ValidationIssue(
                    "EVENT_SCHEMA_INVALID",
                    str(exc),
                    "ERROR",
                    path=path.relative_to(project_root).as_posix(),
                )
            )
    return issues


def validate_example_project(project_root: Path) -> StaticProjectResult:
    root = project_root.resolve()
    ctx, work_packages, profile = _teamnotes_context(root)
    issues = list(build_default_registry().run(ctx).issues)
    issues.extend(_validate_event_schemas(root))

    profile_ctx = SimpleNamespace(**profile, work_packages=tuple(work_packages))
    profile_registry = ValidatorRegistry(
        (
            AsyncContractsValidator(),
            AuthValidator(),
            DatabaseValidator(),
            OperationsValidator(),
            PermissionsValidator(),
            SecurityValidator(),
            TestMatrixValidator(),
        )
    )
    issues.extend(profile_registry.run(profile_ctx).issues)

    findings = _load_yaml(root / "expected-audit/findings.yaml").get("findings", [])
    dispositions = _load_yaml(root / "expected-corrective/dispositions.yaml").get("dispositions", [])
    audit_report = AuditLedger.from_records(
        findings=[dict(item) for item in findings if isinstance(item, dict)],
        dispositions=[dict(item) for item in dispositions if isinstance(item, dict)],
    ).closure_report()
    issues.extend(audit_report.issues)

    unresolved_critical = sum(1 for issue in audit_report.issues if issue.code == "AUDIT_CRITICAL_OPEN")
    unresolved_high = sum(1 for issue in audit_report.issues if issue.code == "AUDIT_HIGH_OPEN")
    pending = tuple(
        path.stem
        for path in sorted((root / "expected-core-spec/decisions").glob("*.yaml"))
        if str(_load_yaml(path).get("status", "")).lower() != "resolved"
    )
    readiness = evaluate_build_readiness(
        ReadinessInputs(
            documentation_complete=all(
                (root / relative).exists()
                for relative in (
                    "expected-core-spec/PRODUCT-SPEC.md",
                    "expected-core-spec/DOMAIN-MODEL.md",
                    "expected-core-spec/TECHNICAL-SPEC.md",
                    "expected-core-spec/DATA-MODEL.md",
                    "expected-core-spec/SECURITY.md",
                    "expected-core-spec/DEPLOYMENT.md",
                    "expected-agent-spec/AGENT-OPERATING-MANUAL.md",
                    "expected-final/SPEC-MANIFEST.yaml",
                )
            ),
            authority_resolved=not any(issue.code.startswith("AUTH_") for issue in issues),
            machine_contracts_valid=not any(
                issue.code.startswith(("API_", "EVENT_", "OWN_")) for issue in issues
            ),
            wp_entrypoint_exists=(root / "expected-work-packages/WP-000.md").is_file(),
            pending_protected_decisions=pending,
            critical_blockers=unresolved_critical,
            high_blockers=unresolved_high,
            profile_validators_green=not any(issue.code.startswith("WS_") for issue in issues),
        )
    )
    if readiness.verdict != "PASS":
        issues.extend(
            ValidationIssue(code, code.replace("_", " ").title(), "ERROR")
            for code in readiness.blocker_codes
        )
    return StaticProjectResult(tuple(issues), readiness.verdict)


def validate_invalid_fixture(fixture_root: Path) -> StaticProjectResult:
    """Run the production validator primitives that apply to one adversarial fixture.

    Fixtures are intentionally minimal, so this helper constructs only the validation
    context needed to reach the advertised defect instead of requiring a full project.
    """
    from tempfile import TemporaryDirectory

    from project_finalizer.artifacts import ArtifactGraph, ArtifactRecord
    from project_finalizer.errors import WorkflowError
    from project_finalizer.release import stage_release
    from project_finalizer.validators.adapters import AdapterValidator
    from project_finalizer.validators.api import ApiValidator
    from project_finalizer.validators.ownership import OwnershipValidator
    from project_finalizer.validators.release import ReleaseValidator
    from project_finalizer.validators.work_packages import WorkPackageValidator

    root = fixture_root.resolve()
    issues: list[ValidationIssue] = []

    claims_path = root / "authority-claims.yaml"
    if claims_path.is_file():
        raw_claims = _load_yaml(claims_path).get("claims", [])
        by_subject: dict[str, set[str]] = {}
        for claim in raw_claims:
            if isinstance(claim, dict):
                by_subject.setdefault(str(claim.get("subject", "")), set()).add(
                    str(claim.get("primary", ""))
                )
        for subject, primaries in sorted(by_subject.items()):
            if len({value for value in primaries if value}) > 1:
                issues.append(
                    ValidationIssue(
                        "AUTH_DUPLICATE_PRIMARY",
                        f"subject {subject} declares multiple primary authorities",
                        "ERROR",
                        subject_id=subject,
                    )
                )

    wp_path = root / "work-packages.yaml"
    if wp_path.is_file():
        packages = _load_yaml(wp_path).get("work_packages", [])
        report = WorkPackageValidator().validate(
            ValidationContext(
                project_root=root,
                work_packages=tuple(dict(item) for item in packages if isinstance(item, dict)),
            )
        )
        issues.extend(report.issues)
        if any(issue.code == "WP_DEPENDENCY_CYCLE" for issue in report.issues):
            issues.append(ValidationIssue("WP_CYCLE", "work-package graph contains a cycle", "ERROR"))

    modules_path = root / "modules.yaml"
    if modules_path.is_file():
        modules = _load_yaml(modules_path).get("modules", [])
        issues.extend(
            OwnershipValidator()
            .validate(
                ValidationContext(
                    project_root=root,
                    modules=tuple(dict(item) for item in modules if isinstance(item, dict)),
                )
            )
            .issues
        )

    audit_path = root / "audit.yaml"
    if audit_path.is_file():
        audit = _load_yaml(audit_path)
        issues.extend(
            AuditLedger.from_records(
                findings=[dict(item) for item in audit.get("findings", []) if isinstance(item, dict)],
                dispositions=[dict(item) for item in audit.get("dispositions", []) if isinstance(item, dict)],
            ).closure_report().issues
        )

    artifacts_path = root / "artifacts.yaml"
    if artifacts_path.is_file():
        raw = _load_yaml(artifacts_path)
        records = tuple(
            ArtifactRecord.from_mapping(dict(item))
            for item in raw.get("artifacts", [])
            if isinstance(item, dict)
        )
        current_hashes = {str(k): str(v) for k, v in raw.get("current_hashes", {}).items()}
        for artifact_id in ArtifactGraph(records).stale_artifacts(current_hashes):
            issues.append(
                ValidationIssue(
                    "ARTIFACT_STALE",
                    f"generated artifact is stale: {artifact_id}",
                    "ERROR",
                    subject_id=artifact_id,
                )
            )

    openapi_path = root / "openapi.yaml"
    if openapi_path.is_file():
        issues.extend(
            ApiValidator(validate_spec_func=lambda document: None)
            .validate(
                ValidationContext(
                    project_root=root,
                    openapi_path=openapi_path,
                    api_policy={"require_auth_metadata": True},
                )
            )
            .issues
        )

    profile_path = root / "profile.yaml"
    if profile_path.is_file():
        profile = _load_yaml(profile_path)
        profile_ctx = SimpleNamespace(**profile, work_packages=())
        issues.extend(AuthValidator().validate(profile_ctx).issues)
        db_report = DatabaseValidator().validate(profile_ctx)
        issues.extend(db_report.issues)
        database = profile.get("database", {})
        if isinstance(database, dict):
            for entity in database.get("entities", []):
                if isinstance(entity, dict) and entity.get("tenant_owned") and not entity.get("tenant_key"):
                    issues.append(
                        ValidationIssue(
                            "WS_DB_TENANT_KEY_REQUIRED",
                            "tenant-owned entity requires tenant key",
                            "ERROR",
                            subject_id=str(entity.get("id", "unknown")),
                        )
                    )

    event_path = root / "events.yaml"
    if event_path.is_file():
        raw = _load_yaml(event_path)
        schemas = {str(value) for value in raw.get("schemas", [])}
        for consumer in raw.get("consumers", []):
            if isinstance(consumer, dict) and str(consumer.get("event", "")) not in schemas:
                issues.append(
                    ValidationIssue(
                        "OWN_EVENT_SCHEMA_MISSING",
                        "event consumer references an event without a declared schema",
                        "ERROR",
                        subject_id=str(consumer.get("event", "")),
                    )
                )

    if (root / ".workflow/adapter-manifest.yaml").is_file():
        issues.extend(AdapterValidator().validate(ValidationContext(project_root=root)).issues)

    if (root / "SHA256SUMS.txt").is_file():
        release_issues = ReleaseValidator().validate(ValidationContext(project_root=root)).issues
        issues.extend(release_issues)
        if any(issue.code == "RELEASE_CHECKSUM_MISMATCH" for issue in release_issues):
            issues.append(ValidationIssue("RELEASE_HASH_MISMATCH", "release hash mismatch", "ERROR"))

    def record_stage_issue(source: Path) -> None:
        if not source.is_dir():
            return
        with TemporaryDirectory(prefix="workflow-fixture-stage-") as tmp:
            try:
                stage_release(source, Path(tmp) / "stage")
            except WorkflowError as exc:
                issues.append(ValidationIssue(exc.code, str(exc), "ERROR"))

    source_fixture = root / "source-fixture.yaml"
    if source_fixture.is_file():
        layout = _load_yaml(source_fixture)
        with TemporaryDirectory(prefix="workflow-fixture-source-") as tmp:
            source = Path(tmp) / "source"
            source.mkdir()
            for relative, content in layout.get("files", {}).items():
                target = source / str(relative)
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_text(str(content), encoding="utf-8")
            for relative, link_target in layout.get("symlinks", {}).items():
                target = source / str(relative)
                target.parent.mkdir(parents=True, exist_ok=True)
                target.symlink_to(str(link_target))
            record_stage_issue(source)
    else:
        record_stage_issue(root / "source")

    return StaticProjectResult(tuple(issues), "FAIL" if issues else "PASS")


def validate_regression_fixture(fixture_root: Path) -> StaticProjectResult:
    from project_finalizer.authority import AuthorityMatrix
    from project_finalizer.errors import WorkflowError
    from project_finalizer.validators.feasibility import FeasibilityValidator
    from project_finalizer.validators.ownership import OwnershipValidator

    root = fixture_root.resolve()
    metadata = _load_yaml(root / "fixture.yaml")
    kind = str(metadata.get("kind", ""))
    issues: list[ValidationIssue] = []

    if kind == "flat-precedence":
        claims = metadata.get("claims", [])
        by_subject: dict[str, set[str]] = {}
        for claim in claims:
            if isinstance(claim, dict):
                by_subject.setdefault(str(claim.get("subject", "")), set()).add(str(claim.get("primary", "")))
        for subject, primaries in by_subject.items():
            if len({value for value in primaries if value}) > 1:
                issues.append(ValidationIssue("AUTH_DUPLICATE_PRIMARY", "multiple authorities claim one wire subject", "ERROR", subject_id=subject))

    elif kind == "async-response-contradiction":
        operation = metadata.get("operation", {})
        if isinstance(operation, dict) and operation.get("response_claims_authoritative_fields") and operation.get("update_mode") == "asynchronous_event" and not operation.get("synchronous_readback"):
            issues.append(ValidationIssue("ASYNC_RESPONSE_AUTHORITY_CONTRADICTION", "synchronous response promises foreign authoritative state that is updated only asynchronously", "ERROR"))

    elif kind == "foreign-owner-write":
        modules = metadata.get("modules", [])
        issues.extend(OwnershipValidator().validate(ValidationContext(project_root=root, modules=tuple(dict(item) for item in modules if isinstance(item, dict)))).issues)

    elif kind == "async-durability":
        async_contract = metadata.get("async", {})
        if isinstance(async_contract, dict) and async_contract.get("durable_cross_module_effect") and (not async_contract.get("producer_outbox") or not async_contract.get("consumer_idempotency")):
            issues.append(ValidationIssue("ASYNC_DURABILITY_CONTRACT_MISSING", "durable cross-module async effects require producer durability and idempotent consumption", "ERROR"))

    elif kind == "event-schema-drift":
        event = metadata.get("event", {})
        if isinstance(event, dict) and set(map(str, event.get("catalog_fields", []))) != set(map(str, event.get("schema_fields", []))):
            issues.append(ValidationIssue("EVENT_SCHEMA_DRIFT", "event catalog and machine schema fields differ", "ERROR"))

    elif kind == "timeout-budget":
        issues.extend(FeasibilityValidator().validate(SimpleNamespace(resource_budget=metadata.get("resource_budget", {}))).issues)

    elif kind == "wp-gate-timing":
        invariant = metadata.get("invariant", {})
        if isinstance(invariant, dict):
            required = str(invariant.get("required_from_wp", "WP-999"))
            activated = str(invariant.get("activated_from_wp", "WP-999"))
            try:
                required_n = int(required.split("-")[1])
                activated_n = int(activated.split("-")[1])
            except (IndexError, ValueError):
                required_n = activated_n = 0
            if activated_n > required_n:
                issues.append(ValidationIssue("WP_INVARIANT_ACTIVATION_LATE", "critical invariant activates after the package that first needs it", "ERROR", subject_id=str(invariant.get("id", ""))))

    elif kind == "historical-authority":
        authority = metadata.get("authority", {})
        try:
            AuthorityMatrix.from_mapping(dict(authority) if isinstance(authority, dict) else {})
        except WorkflowError as exc:
            code = "AUTH_HISTORICAL_LEAKAGE" if exc.code == "HISTORICAL_AUTHORITY_FORBIDDEN" else exc.code
            issues.append(ValidationIssue(code, str(exc), "ERROR"))

    return StaticProjectResult(tuple(issues), "FAIL" if issues else "PASS")


def validate_self_hosting(repo_root: Path) -> StaticProjectResult:
    """Validate this workflow repository with applicable Generic Core rules only."""
    root = repo_root.resolve()
    module_dir = root / "self-hosting/modules"
    modules = tuple(_load_yaml(path) for path in sorted(module_dir.glob("*.yaml")))
    graph = _load_yaml(root / "self-hosting/work-packages/graph.yaml")
    work_packages = tuple(
        dict(item) for item in graph.get("work_packages", []) if isinstance(item, dict)
    )
    ctx = ValidationContext(
        project_root=root,
        authority_matrix_path=root / "self-hosting/AUTHORITY-MATRIX.yaml",
        modules=modules,
        work_packages=work_packages,
    )
    # Self-hosting uses the same generic layers but intentionally has no web-saas context.
    issues = list(build_default_registry().run(ctx).issues)
    audit_findings = _load_yaml(root / "self-hosting/audit/findings.yaml").get("findings", [])
    audit_dispositions = _load_yaml(root / "self-hosting/audit/dispositions.yaml").get("dispositions", [])
    issues.extend(
        AuditLedger.from_records(
            findings=[dict(item) for item in audit_findings if isinstance(item, dict)],
            dispositions=[dict(item) for item in audit_dispositions if isinstance(item, dict)],
        ).closure_report().issues
    )
    readiness = evaluate_build_readiness(
        ReadinessInputs(
            documentation_complete=(
                (root / "docs/superpowers/specs/shipgate-architecture-spec.md").is_file()
                or (root / "docs/superpowers/specs/2026-09-20-ai-project-finalization-workflow-v2-design.md").is_file()
            ),
            authority_resolved=not any(issue.code.startswith("AUTH_") for issue in issues),
            machine_contracts_valid=not any(issue.code.startswith(("OWN_", "REF_", "SYNTAX_")) for issue in issues),
            wp_entrypoint_exists=any(wp.get("id") == "WP-000" for wp in work_packages),
            critical_blockers=sum(1 for issue in issues if issue.code == "AUDIT_CRITICAL_OPEN"),
            high_blockers=sum(1 for issue in issues if issue.code == "AUDIT_HIGH_OPEN"),
        )
    )
    if readiness.verdict != "PASS":
        issues.extend(ValidationIssue(code, code.replace("_", " ").title(), "ERROR") for code in readiness.blocker_codes)
    return StaticProjectResult(tuple(issues), readiness.verdict)
