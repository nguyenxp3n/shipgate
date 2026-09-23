from __future__ import annotations

from project_finalizer.artifacts import ArtifactGraph
from project_finalizer.io import ProjectFS


def register_generated(
    fs: ProjectFS,
    graph: ArtifactGraph,
    *,
    artifact_id: str,
    output: str,
    source_ids: tuple[str, ...],
) -> ArtifactGraph:
    return graph.record_build(
        fs=fs,
        artifact_id=artifact_id,
        path=output,
        depends_on=source_ids,
        generated=True,
    )
