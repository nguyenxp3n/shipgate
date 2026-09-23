from __future__ import annotations

from collections import Counter
from typing import Any

from project_finalizer.artifacts import ArtifactGraph
from project_finalizer.generators import register_generated
from project_finalizer.io import ProjectFS


def generate_audit_summary(
    fs: ProjectFS,
    graph: ArtifactGraph,
    findings: list[dict[str, Any]],
    *,
    output: str,
    source_ids: tuple[str, ...],
) -> ArtifactGraph:
    counts = Counter(str(item.get("severity", "UNKNOWN")) for item in findings)
    fs.write_yaml_atomic(
        output, {"total": len(findings), "by_severity": dict(sorted(counts.items()))}
    )
    return register_generated(
        fs, graph, artifact_id="AUDIT_SUMMARY", output=output, source_ids=source_ids
    )
