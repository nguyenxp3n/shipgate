from __future__ import annotations

from typing import Any

from project_finalizer.artifacts import ArtifactGraph
from project_finalizer.generators import register_generated
from project_finalizer.io import ProjectFS


def generate_ownership_matrix(fs: ProjectFS, graph: ArtifactGraph, modules: list[dict[str, Any]], *, output: str, source_ids: tuple[str, ...]) -> ArtifactGraph:
    owners = []
    for module in sorted(modules, key=lambda item: str(item.get("id", ""))):
        for data_name in sorted(str(value) for value in module.get("owned_data", [])):
            owners.append({"data": data_name, "owner": str(module.get("id", ""))})
    fs.write_yaml_atomic(output, {"ownership": owners})
    return register_generated(fs, graph, artifact_id="OWNERSHIP_MATRIX", output=output, source_ids=source_ids)
