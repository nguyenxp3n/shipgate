from pathlib import Path

from project_finalizer.testing import validate_self_hosting


def test_workflow_repo_passes_applicable_generic_core_rules(repo_root: Path) -> None:
    result = validate_self_hosting(repo_root)
    assert result.ok, result.format_issues()
