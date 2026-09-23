from pathlib import Path

from project_finalizer.validators import ValidationContext
from project_finalizer.validators.references import ReferenceValidator


def test_unknown_authority_ref_is_reported(tmp_path: Path) -> None:
    ctx = ValidationContext(tmp_path, authority_refs=("docs/missing.md",))
    report = ReferenceValidator().validate(ctx)
    assert [issue.code for issue in report.issues] == ["REF_MISSING_PATH"]
