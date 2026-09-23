import pytest

from project_finalizer.artifacts import ArtifactGraph, ArtifactRecord
from project_finalizer.errors import WorkflowError


def test_changed_upstream_marks_dependent_stale():
    graph = ArtifactGraph(
        records=(
            ArtifactRecord("API_SEMANTICS", "docs/API.md", (), {}, False),
            ArtifactRecord(
                "OPENAPI",
                "contracts/openapi.yaml",
                ("API_SEMANTICS",),
                {"API_SEMANTICS": "oldhash"},
                True,
            ),
        )
    )
    assert graph.stale_artifacts({"API_SEMANTICS": "newhash"}) == ("OPENAPI",)


def test_missing_upstream_marks_artifact_and_transitive_downstream_stale():
    graph = ArtifactGraph(
        records=(
            ArtifactRecord("SOURCE", "source.md", (), {}, False),
            ArtifactRecord("A", "a.yaml", ("SOURCE",), {"SOURCE": "h1"}, True),
            ArtifactRecord("B", "b.yaml", ("A",), {"A": "h2"}, True),
        )
    )
    assert graph.stale_artifacts({}) == ("A", "B")


def test_artifact_cycle_is_rejected():
    with pytest.raises(WorkflowError, match="cycle"):
        ArtifactGraph(
            records=(
                ArtifactRecord("A", "a", ("B",), {"B": "x"}, True),
                ArtifactRecord("B", "b", ("A",), {"A": "y"}, True),
            )
        )
