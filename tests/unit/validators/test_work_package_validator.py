from pathlib import Path

from project_finalizer.validators import ValidationContext
from project_finalizer.validators.work_packages import WorkPackageValidator


def _wp(wp_id: str, **overrides):
    data = {
        "id": wp_id,
        "title": wp_id,
        "state": "READY",
        "purpose": "purpose",
        "depends_on": [],
        "authority_refs": ["AUTH"],
        "allowed_paths": [f"src/{wp_id}/**"],
        "forbidden_paths": [],
        "acceptance_commands": ["task test"],
        "stop_conditions": ["protected decision required"],
        "protected_surface": True,
        "completion_evidence": ["tests pass"],
        "activated_invariants": [],
    }
    data.update(overrides)
    return data


def test_wp_graph_requires_wp000(tmp_path: Path) -> None:
    ctx = ValidationContext(tmp_path, work_packages=(_wp("WP-001"),), known_authority_ids=frozenset({"AUTH"}))
    report = WorkPackageValidator().validate(ctx)
    assert "WP_ENTRYPOINT_MISSING" in [issue.code for issue in report.issues]


def test_wp_scope_contradiction_is_reported(tmp_path: Path) -> None:
    ctx = ValidationContext(
        tmp_path,
        work_packages=(
            _wp("WP-000", allowed_paths=["src/**"], forbidden_paths=["src/**"]),
        ),
        known_authority_ids=frozenset({"AUTH"}),
    )
    report = WorkPackageValidator().validate(ctx)
    assert "WP_PATH_SCOPE_CONTRADICTION" in [issue.code for issue in report.issues]
