from __future__ import annotations

from typing import Any

from project_finalizer.artifacts import ArtifactGraph
from project_finalizer.generators import register_generated
from project_finalizer.io import ProjectFS


def generate_manifest(
    fs: ProjectFS,
    graph: ArtifactGraph,
    data: dict[str, Any],
    *,
    output: str,
    source_ids: tuple[str, ...],
) -> ArtifactGraph:
    fs.write_yaml_atomic(output, data)
    return register_generated(
        fs, graph, artifact_id="SPEC_MANIFEST", output=output, source_ids=source_ids
    )
