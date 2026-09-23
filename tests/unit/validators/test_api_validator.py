from pathlib import Path

from project_finalizer.validators import ValidationContext
from project_finalizer.validators.api import ApiValidator


def _no_op_validate_spec(document):
    assert isinstance(document, dict)


def test_duplicate_operation_id_fails(repo_root: Path) -> None:
    ctx = ValidationContext(
        repo_root,
        openapi_path=repo_root / "tests/fixtures/openapi/duplicate-operation-id.yaml",
    )
    report = ApiValidator(validate_spec_func=_no_op_validate_spec).validate(ctx)
    assert "API_DUPLICATE_OPERATION_ID" in {issue.code for issue in report.issues}


def test_unknown_error_code_fails(repo_root: Path) -> None:
    ctx = ValidationContext(
        repo_root,
        openapi_path=repo_root / "tests/fixtures/openapi/unregistered-error.yaml",
        error_catalog=frozenset({"RESOURCE_NOT_FOUND"}),
    )
    report = ApiValidator(validate_spec_func=_no_op_validate_spec).validate(ctx)
    assert "API_ERROR_CODE_UNKNOWN" in {issue.code for issue in report.issues}


def test_required_auth_and_idempotency_metadata_are_reported(repo_root: Path) -> None:
    ctx = ValidationContext(
        repo_root,
        openapi_path=repo_root / "tests/fixtures/openapi/duplicate-operation-id.yaml",
        api_policy={"require_auth_metadata": True, "require_idempotency_metadata": True},
    )
    report = ApiValidator(validate_spec_func=_no_op_validate_spec).validate(ctx)
    codes = {issue.code for issue in report.issues}
    assert "API_AUTH_METADATA_MISSING" in codes
    assert "API_IDEMPOTENCY_METADATA_MISSING" in codes


def test_valid_openapi_with_registered_error_is_clean(repo_root: Path) -> None:
    ctx = ValidationContext(
        repo_root,
        openapi_path=repo_root / "tests/fixtures/openapi/valid.yaml",
        error_catalog=frozenset({"RESOURCE_NOT_FOUND"}),
        api_policy={"require_auth_metadata": True, "require_idempotency_metadata": True},
    )
    report = ApiValidator(validate_spec_func=_no_op_validate_spec).validate(ctx)
    assert report.ok
