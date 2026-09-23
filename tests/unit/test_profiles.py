from pathlib import Path

import pytest

from project_finalizer.errors import ExitCode, WorkflowError
from project_finalizer.profiles import load_profile_manifest


def test_incompatible_profile_returns_profile_error(repo_root: Path):
    with pytest.raises(WorkflowError) as exc:
        load_profile_manifest(
            repo_root / "tests/fixtures/profiles/incompatible/PROFILE-MANIFEST.yaml",
            core_version="2.0.0",
        )
    assert exc.value.exit_code == ExitCode.PROFILE_ERROR
    assert exc.value.code == "PROFILE_CORE_INCOMPATIBLE"
