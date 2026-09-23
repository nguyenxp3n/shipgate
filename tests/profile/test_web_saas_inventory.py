from pathlib import Path

ARCHITECTURE = {
    "architecture/WEB-APPLICATION-ARCHITECTURE.md",
    "architecture/FRONTEND-ARCHITECTURE.template.md",
    "architecture/BACKEND-ARCHITECTURE.template.md",
    "architecture/DATA-ARCHITECTURE.template.md",
    "architecture/INTEGRATION-ARCHITECTURE.template.md",
    "architecture/DEPLOYMENT-TOPOLOGY.template.md",
    "architecture/TRUST-BOUNDARIES.template.md",
}
CAPABILITIES = {
    "frontend",
    "api",
    "auth",
    "authorization",
    "users",
    "organizations",
    "database",
    "cache",
    "jobs",
    "events",
    "files",
    "email",
    "notifications",
    "admin",
    "search",
    "analytics",
    "payments",
    "audit-log",
    "observability",
    "operations",
}
CONTRACTS = {
    "contracts/http/HTTP-CONTRACT.md",
    "contracts/sessions/SESSION-CONTRACT.md",
    "contracts/permissions/PERMISSION-CATALOG.template.yaml",
    "contracts/pagination/PAGINATION-CONTRACT.md",
    "contracts/idempotency/IDEMPOTENCY-CONTRACT.md",
    "contracts/webhooks/WEBHOOK-CONTRACT.md",
    "contracts/jobs/JOB-CONTRACT.md",
    "contracts/events/EVENT-CONTRACT.md",
    "contracts/files/FILE-CONTRACT.md",
    "contracts/errors/ERROR-CATALOG.template.yaml",
    "contracts/configuration/CONFIGURATION-CONTRACT.md",
}
SECURITY = {
    "security/WEB-THREAT-MODEL.template.md",
    "security/SESSION-SECURITY.md",
    "security/API-SECURITY.md",
    "security/BROWSER-SECURITY.md",
    "security/DATA-PROTECTION.md",
    "security/SECRET-MANAGEMENT.md",
    "security/FILE-UPLOAD-SECURITY.md",
    "security/SSRF-POLICY.md",
    "security/WEBHOOK-SECURITY.md",
    "security/SECURITY-INVARIANTS.yaml",
}
DATABASE = {
    "database/DATABASE-CONTRACT.template.md",
    "database/MIGRATION-POLICY.md",
    "database/TRANSACTION-POLICY.md",
    "database/INDEX-POLICY.md",
    "database/RETENTION-POLICY.md",
    "database/OUTBOX-INBOX-PATTERN.md",
    "database/BACKUP-RESTORE.md",
}
OPERATIONS = {
    "operations/ENVIRONMENT-CONTRACT.template.yaml",
    "operations/CONFIGURATION-POLICY.md",
    "operations/HEALTH-READINESS.md",
    "operations/OBSERVABILITY-STANDARD.md",
    "operations/SLO.template.yaml",
    "operations/INCIDENT-RUNBOOK.template.md",
    "operations/DEPLOYMENT.template.md",
    "operations/DISASTER-RECOVERY.template.md",
}
TESTING = {
    "testing/WEB-SAAS-TEST-MATRIX.yaml",
    "testing/BROWSER-E2E-MATRIX.yaml",
    "testing/API-CONTRACT-MATRIX.yaml",
    "testing/AUTH-SECURITY-MATRIX.yaml",
    "testing/DATABASE-INTEGRATION-MATRIX.yaml",
    "testing/JOB-EVENT-MATRIX.yaml",
    "testing/DEPLOYMENT-SMOKE-MATRIX.yaml",
}
WORK_PACKAGES = {
    "work-packages/WEB-SAAS-WP-RULES.md",
    "work-packages/BOOTSTRAP-WP.template.md",
    "work-packages/MODULE-WP.template.md",
    "work-packages/SECURITY-WP.template.md",
    "work-packages/DATA-WP.template.md",
    "work-packages/UI-WP.template.md",
    "work-packages/RELEASE-WP.template.md",
}


def test_required_web_saas_files_exist(repo_root: Path) -> None:
    root = repo_root / "profiles/web-saas"
    required = ARCHITECTURE | CONTRACTS | SECURITY | DATABASE | OPERATIONS | TESTING | WORK_PACKAGES
    required |= {f"capabilities/{name}/CAPABILITY.md" for name in CAPABILITIES}
    required |= {f"capabilities/{name}/CAPABILITY.yaml" for name in CAPABILITIES}
    missing = sorted(path for path in required if not (root / path).is_file())
    assert missing == []
