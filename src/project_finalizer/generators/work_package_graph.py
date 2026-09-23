from __future__ import annotations

from typing import Any

from project_finalizer.artifacts import ArtifactGraph
from project_finalizer.generators import register_generated
from project_finalizer.io import ProjectFS


def generate_work_package_graph(fs: ProjectFS, graph: ArtifactGraph, packages: list[dict[str, Any]], *, output: str, source_ids: tuple[str, ...]) -> ArtifactGraph:
    rows = [
        {"id": str(item.get("id", "")), "depends_on": sorted(str(value) for value in item.get("depends_on", []))}
        for item in sorted(packages, key=lambda item: str(item.get("id", "")))
    ]
    fs.write_yaml_atomic(output, {"work_packages": rows})
    return register_generated(fs, graph, artifact_id="WP_GRAPH", output=output, source_ids=source_ids)
