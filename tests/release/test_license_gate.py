from pathlib import Path

import pytest
import yaml

from project_finalizer.commands.release import _preflight
from project_finalizer.errors import ExitCode, WorkflowError
from project_finalizer.models import ValidationReport
from project_finalizer.readiness import ReadinessInputs


class _PassingRegistry:
    def run(self, _ctx: object) -> ValidationReport:
        return ValidationReport()


def _mock_other_preflight_gates(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        "project_finalizer.commands.release.build_default_registry",
        lambda: _PassingRegistry(),
    )
    monkeypatch.setattr(
        "project_finalizer.commands.release.collect_readiness_inputs",
        lambda _root: ReadinessInputs(),
    )


def _mark_as_workflow_source(root: Path) -> None:
    (root / "WORKFLOW-MANIFEST.yaml").write_text(
        yaml.safe_dump(
            {
                "workflow": {
                    "name": "ai-project-finalization-workflow",
                    "version": "2.0.0",
                    "status": "active",
                }
            },
            sort_keys=False,
        ),
        encoding="utf-8",
    )


def test_workflow_release_preflight_requires_resolved_license_decision(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _mock_other_preflight_gates(monkeypatch)
    _mark_as_workflow_source(tmp_path)

    with pytest.raises(WorkflowError) as exc:
        _preflight(tmp_path)

    assert exc.value.exit_code == ExitCode.HUMAN_DECISION_REQUIRED
    assert exc.value.code == "RELEASE_LICENSE_DECISION_REQUIRED"


def test_target_project_release_does_not_require_workflow_repository_license(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _mock_other_preflight_gates(monkeypatch)

    _preflight(tmp_path)


def test_workflow_release_accepts_resolved_proprietary_license(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _mock_other_preflight_gates(monkeypatch)
    _mark_as_workflow_source(tmp_path)
    decision_dir = tmp_path / "docs/decisions"
    decision_dir.mkdir(parents=True)
    (decision_dir / "DR-WF-001-license.yaml").write_text(
        yaml.safe_dump(
            {
                "id": "DR-WF-001",
                "subject": "repository_license",
                "status": "RESOLVED",
                "resolution": {
                    "choice": "C",
                    "original_text": "C. Proprietary / All Rights Reserved",
                },
            },
            sort_keys=False,
        ),
        encoding="utf-8",
    )
    (tmp_path / "LICENSE").write_text(
        "Copyright (c) 2026. All Rights Reserved.\n",
        encoding="utf-8",
    )

    _preflight(tmp_path)
