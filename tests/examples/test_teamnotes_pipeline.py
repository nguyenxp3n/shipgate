from pathlib import Path

from project_finalizer.testing import validate_example_project


def test_teamnotes_positive_static_pipeline(repo_root: Path) -> None:
    result = validate_example_project(repo_root / "examples/teamnotes")
    assert result.ok, result.format_issues()
    assert result.build_readiness == "PASS"
