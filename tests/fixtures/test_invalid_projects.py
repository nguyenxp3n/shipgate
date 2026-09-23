from pathlib import Path

import pytest

from project_finalizer.testing import validate_invalid_fixture


@pytest.mark.parametrize(
    ("fixture", "expected_code"),
    [
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
    ],
)
def test_invalid_fixture_fails_for_expected_reason(
    repo_root: Path, fixture: str, expected_code: str
) -> None:
    result = validate_invalid_fixture(repo_root / "fixtures/invalid" / fixture)
    assert result.ok is False
    assert expected_code in result.issue_codes, result.format_issues()
