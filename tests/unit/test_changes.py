from pathlib import Path

import pytest

from project_finalizer.artifacts import ArtifactGraph, ArtifactRecord
from project_finalizer.changes import ChangeStore
from project_finalizer.errors import ExitCode, WorkflowError
from project_finalizer.io import ProjectFS


def test_change_close_rejects_stale_affected_artifact(tmp_path: Path):
    root = tmp_path / "project"
    root.mkdir()
    fs = ProjectFS(root)
    graph = ArtifactGraph(
        records=(
            ArtifactRecord("SOURCE", "source.md", (), {}, False),
            ArtifactRecord("OPENAPI", "openapi.yaml", ("SOURCE",), {"SOURCE": "old"}, True),
        )
    )
    store = ChangeStore(fs)
    store.begin(
        "CHG-0017",
        reason="fix contract",
        finding="CTR-017",
        affected_authorities=("api",),
        downstream_artifacts=("OPENAPI",),
        version_impact="patch",
    )
    store.validate("CHG-0017", validators_green=True)
    with pytest.raises(WorkflowError) as exc:
        store.close("CHG-0017", artifact_graph=graph, current_hashes={"SOURCE": "new"})
    assert exc.value.exit_code == ExitCode.STALE_ARTIFACTS
