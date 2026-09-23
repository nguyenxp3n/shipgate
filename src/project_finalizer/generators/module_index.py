from __future__ import annotations

from typing import Any

from project_finalizer.artifacts import ArtifactGraph
from project_finalizer.generators import register_generated
from project_finalizer.io import ProjectFS


def generate_module_index(
    fs: ProjectFS,
    graph: ArtifactGraph,
    modules: list[dict[str, Any]],
    *,
    output: str,
    source_ids: tuple[str, ...],
) -> ArtifactGraph:
    rows = []
    for module in sorted(modules, key=lambda item: str(item.get("id", ""))):
        module_id = str(module.get("id", ""))
        owned = ", ".join(sorted(str(value) for value in module.get("owned_data", []))) or "-"
        rows.append(f"| {module_id} | {owned} |")
    content = "# Module Index\n\n| Module | Owned data |\n| --- | --- |\n" + "\n".join(rows) + "\n"
    fs.write_text_atomic(output, content)
    return register_generated(
        fs, graph, artifact_id="MODULE_INDEX", output=output, source_ids=source_ids
    )
