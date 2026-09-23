from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass
from typing import Any

from project_finalizer.errors import ExitCode, WorkflowError
from project_finalizer.ids import assert_unique_ids
from project_finalizer.io import ProjectFS


@dataclass(frozen=True)
class ArtifactRecord:
    artifact_id: str
    path: str
    depends_on: tuple[str, ...]
    built_from_hashes: dict[str, str]
    generated: bool = True

    @classmethod
    def from_mapping(cls, raw: dict[str, Any]) -> ArtifactRecord:
        return cls(
            artifact_id=str(raw["artifact_id"]),
            path=str(raw["path"]),
            depends_on=tuple(str(v) for v in raw.get("depends_on", [])),
            built_from_hashes={str(k): str(v) for k, v in raw.get("built_from_hashes", {}).items()},
            generated=bool(raw.get("generated", True)),
        )

    def to_mapping(self) -> dict[str, Any]:
        return {
            "artifact_id": self.artifact_id,
            "path": self.path,
            "depends_on": list(self.depends_on),
            "built_from_hashes": dict(sorted(self.built_from_hashes.items())),
            "generated": self.generated,
        }


class ArtifactGraph:
    PATH = ".workflow/artifacts.yaml"

    def __init__(self, records: tuple[ArtifactRecord, ...] = ()) -> None:
        try:
            assert_unique_ids(record.artifact_id for record in records)
        except ValueError as exc:
            raise WorkflowError(
                str(exc),
                exit_code=ExitCode.VALIDATION_FAILED,
                code="ARTIFACT_ID_DUPLICATE",
            ) from exc
        self.records = tuple(sorted(records, key=lambda record: record.artifact_id))
        self._by_id = {record.artifact_id: record for record in self.records}
        self._assert_acyclic()

    def _assert_acyclic(self) -> None:
        visiting: set[str] = set()
        visited: set[str] = set()

        def visit(node: str) -> None:
            if node in visited:
                return
            if node in visiting:
                raise WorkflowError(
                    f"artifact dependency cycle detected at {node}",
                    exit_code=ExitCode.VALIDATION_FAILED,
                    code="ARTIFACT_DEPENDENCY_CYCLE",
                )
            visiting.add(node)
            record = self._by_id.get(node)
            if record is not None:
                for dependency in record.depends_on:
                    if dependency in self._by_id:
                        visit(dependency)
            visiting.remove(node)
            visited.add(node)

        for artifact_id in sorted(self._by_id):
            visit(artifact_id)

    def mark_downstream(self, changed: Iterable[str]) -> tuple[str, ...]:
        marked = set(changed)
        descendants: set[str] = set()
        progressed = True
        while progressed:
            progressed = False
            for record in self.records:
                if record.artifact_id in marked:
                    continue
                if any(dependency in marked for dependency in record.depends_on):
                    marked.add(record.artifact_id)
                    descendants.add(record.artifact_id)
                    progressed = True
        return tuple(sorted(descendants))

    def stale_artifacts(self, current_hashes: dict[str, str]) -> tuple[str, ...]:
        stale: set[str] = set()
        for record in self.records:
            if not record.generated:
                continue
            for dependency in record.depends_on:
                expected = record.built_from_hashes.get(dependency)
                actual = current_hashes.get(dependency)
                if expected is None or actual is None or expected != actual:
                    stale.add(record.artifact_id)
                    break
        if stale:
            stale.update(self.mark_downstream(stale))
        return tuple(sorted(stale))

    def missing_sources(self, current_hashes: dict[str, str]) -> tuple[str, ...]:
        missing: set[str] = set()
        for record in self.records:
            if not record.generated:
                continue
            for dependency in record.depends_on:
                if dependency not in current_hashes:
                    missing.add(dependency)
        return tuple(sorted(missing))

    def record_build(
        self,
        *,
        fs: ProjectFS,
        artifact_id: str,
        path: str,
        depends_on: tuple[str, ...],
        generated: bool = True,
    ) -> ArtifactGraph:
        if not fs.resolve(path).is_file():
            raise WorkflowError(
                f"generated artifact output does not exist: {path}",
                exit_code=ExitCode.VALIDATION_FAILED,
                code="ARTIFACT_OUTPUT_MISSING",
            )
        hashes: dict[str, str] = {}
        for dependency in depends_on:
            source = self._by_id.get(dependency)
            if source is None:
                raise WorkflowError(
                    f"artifact source missing: {dependency}",
                    exit_code=ExitCode.STALE_ARTIFACTS,
                    code="ARTIFACT_SOURCE_MISSING",
                )
            if not fs.resolve(source.path).is_file():
                raise WorkflowError(
                    f"artifact source missing: {dependency}",
                    exit_code=ExitCode.STALE_ARTIFACTS,
                    code="ARTIFACT_SOURCE_MISSING",
                )
            hashes[dependency] = fs.sha256(source.path)
        replacement = ArtifactRecord(artifact_id, path, depends_on, hashes, generated)
        records = [record for record in self.records if record.artifact_id != artifact_id]
        records.append(replacement)
        return ArtifactGraph(tuple(records))

    def save(self, fs: ProjectFS) -> None:
        fs.write_yaml_atomic(
            self.PATH,
            {"artifacts": [record.to_mapping() for record in self.records]},
        )

    @classmethod
    def load(cls, fs: ProjectFS) -> ArtifactGraph:
        path = fs.resolve(cls.PATH)
        if not path.is_file():
            return cls(())
        raw = fs.read_yaml(cls.PATH)
        if not isinstance(raw, dict) or not isinstance(raw.get("artifacts"), list):
            raise WorkflowError(
                "artifact graph is invalid",
                exit_code=ExitCode.VALIDATION_FAILED,
                code="ARTIFACT_GRAPH_INVALID",
            )
        records = tuple(ArtifactRecord.from_mapping(item) for item in raw["artifacts"])
        return cls(records)
