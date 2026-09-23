from pathlib import Path


def _text(repo_root: Path, relative: str) -> str:
    return (repo_root / "profiles/web-saas" / relative).read_text(encoding="utf-8").casefold()


def test_browser_security_covers_required_surfaces(repo_root: Path) -> None:
    text = _text(repo_root, "security/BROWSER-SECURITY.md")
    for marker in (
        "csp",
        "cors",
        "csrf",
        "xss",
        "clickjacking",
        "referrer policy",
        "permissions policy",
        "open redirect",
        "service worker",
        "private",
    ):
        assert marker in text


def test_database_and_health_policies_pin_critical_semantics(repo_root: Path) -> None:
    migration = _text(repo_root, "database/MIGRATION-POLICY.md")
    for marker in ("expand", "migrate", "contract", "forward-fix"):
        assert marker in migration
    outbox = _text(repo_root, "database/OUTBOX-INBOX-PATTERN.md")
    assert "idempotent" in outbox
    assert "docker socket" in outbox
    health = _text(repo_root, "operations/HEALTH-READINESS.md")
    assert "liveness" in health and "readiness" in health


def test_work_package_rules_pin_bootstrap_and_stop_conditions(repo_root: Path) -> None:
    text = _text(repo_root, "work-packages/WEB-SAAS-WP-RULES.md")
    assert "wp-000" in text
    assert "protected" in text
    assert "stop condition" in text
