from __future__ import annotations

from project_finalizer.artifacts import ArtifactGraph
from project_finalizer.generators import register_generated
from project_finalizer.io import ProjectFS
from project_finalizer.readiness import ReadinessReport


def generate_readiness_report(
    fs: ProjectFS,
    graph: ArtifactGraph,
    report: ReadinessReport,
    *,
    output: str,
    source_ids: tuple[str, ...],
) -> ArtifactGraph:
    fs.write_yaml_atomic(output, report.to_mapping())
    return register_generated(
        fs, graph, artifact_id="READINESS_REPORT", output=output, source_ids=source_ids
    )
