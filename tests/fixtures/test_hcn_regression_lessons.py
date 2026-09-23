from pathlib import Path

import yaml

from project_finalizer.testing import validate_regression_fixture


def test_hcn_regression_lessons_preserve_expected_defect_classes(repo_root: Path) -> None:
    root = repo_root / "fixtures/regression/hcn-learning-lessons"
    for fixture in sorted(path for path in root.iterdir() if path.is_dir()):
        metadata = yaml.safe_load((fixture / "fixture.yaml").read_text(encoding="utf-8"))
        result = validate_regression_fixture(fixture)
        assert result.ok is False, fixture.name
        for expected in metadata["expected_codes"]:
            assert expected in result.issue_codes, f"{fixture.name}: {result.format_issues()}"
