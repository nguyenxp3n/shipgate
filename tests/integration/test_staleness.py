from pathlib import Path

from project_finalizer.artifacts import ArtifactGraph, ArtifactRecord
from project_finalizer.io import ProjectFS


def test_artifact_graph_persists_atomically(tmp_path: Path):
    root = tmp_path / "project"
    root.mkdir()
    fs = ProjectFS(root)
    graph = ArtifactGraph(records=(ArtifactRecord("SOURCE", "source.md", (), {}, False),))
    graph.save(fs)
    loaded = ArtifactGraph.load(fs)
    assert loaded.records == graph.records
