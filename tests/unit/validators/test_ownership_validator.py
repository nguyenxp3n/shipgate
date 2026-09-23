from pathlib import Path

from project_finalizer.validators import ValidationContext
from project_finalizer.validators.ownership import OwnershipValidator


def test_duplicate_owner_is_reported(tmp_path: Path) -> None:
    ctx = ValidationContext(
        tmp_path,
        modules=(
            {"id": "a", "owned_data": ["users"], "must_not_write": []},
            {"id": "b", "owned_data": ["users"], "must_not_write": []},
        ),
    )
    report = OwnershipValidator().validate(ctx)
    assert [issue.code for issue in report.issues] == ["OWN_DUPLICATE_OWNER"]


def test_foreign_write_is_reported(tmp_path: Path) -> None:
    ctx = ValidationContext(
        tmp_path,
        modules=(
            {"id": "a", "owned_data": ["users"], "must_not_write": []},
            {"id": "b", "owned_data": [], "must_not_write": [], "writes": ["users"]},
        ),
    )
    report = OwnershipValidator().validate(ctx)
    assert [issue.code for issue in report.issues] == ["OWN_FOREIGN_WRITE"]
