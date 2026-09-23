from pathlib import Path

from project_finalizer.validators import ValidationContext
from project_finalizer.validators.syntax import SyntaxValidator


def test_invalid_yaml_is_reported(tmp_path: Path) -> None:
    (tmp_path / "broken.yaml").write_text("a: [\n", encoding="utf-8")
    report = SyntaxValidator().validate(ValidationContext(tmp_path))
    assert [issue.code for issue in report.issues] == ["SYNTAX_YAML_INVALID"]
