from pathlib import Path

from project_finalizer.validators import ValidationContext
from project_finalizer.validators.authority import AuthorityValidator


def test_historical_authority_is_rejected(tmp_path: Path) -> None:
    historical = tmp_path / "docs/audits/historical/old.md"
    historical.parent.mkdir(parents=True)
    historical.write_text("old", encoding="utf-8")
    matrix = tmp_path / "AUTHORITY-MATRIX.yaml"
    matrix.write_text(
        "subjects:\n  product_behavior:\n    composition: single\n    primary:\n      - docs/audits/historical/old.md\n",
        encoding="utf-8",
    )
    ctx = ValidationContext(tmp_path, authority_matrix_path=matrix)
    report = AuthorityValidator().validate(ctx)
    assert [issue.code for issue in report.issues] == ["AUTH_HISTORICAL_LEAKAGE"]
