from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from project_finalizer.errors import ExitCode, WorkflowError
from project_finalizer.ids import assert_unique_ids


@dataclass(frozen=True)
class ModuleRecord:
    module_id: str
    owned_data: tuple[str, ...]
    must_not_write: tuple[str, ...]
    writes: tuple[str, ...]
    dependencies: tuple[str, ...]


@dataclass(frozen=True)
class OwnershipIndex:
    owners: dict[str, str]

    def owner_for(self, data_name: str) -> str | None:
        return self.owners.get(data_name)


class ModuleCatalog:
    def __init__(self, modules: tuple[ModuleRecord, ...]) -> None:
        self.modules = tuple(sorted(modules, key=lambda module: module.module_id))
        self.by_id = {module.module_id: module for module in self.modules}
        owners: dict[str, str] = {}
        for module in self.modules:
            for item in module.owned_data:
                if item in owners:
                    raise WorkflowError(
                        f"duplicate owner for {item}: {owners[item]} and {module.module_id}",
                        exit_code=ExitCode.VALIDATION_FAILED,
                        code="DUPLICATE_DATA_OWNER",
                    )
                owners[item] = module.module_id
        self.ownership = OwnershipIndex(owners)
        for module in self.modules:
            for item in module.writes:
                owner = owners.get(item)
                if owner is not None and owner != module.module_id:
                    raise WorkflowError(
                        f"foreign write from {module.module_id} to {item} owned by {owner}",
                        exit_code=ExitCode.VALIDATION_FAILED,
                        code="FOREIGN_DATA_WRITE",
                    )
                if item in module.must_not_write:
                    raise WorkflowError(
                        f"module {module.module_id} writes forbidden data {item}",
                        exit_code=ExitCode.VALIDATION_FAILED,
                        code="FORBIDDEN_DATA_WRITE",
                    )
        self._assert_acyclic()

    @classmethod
    def from_mappings(cls, mappings: list[dict[str, Any]]) -> "ModuleCatalog":
        ids = [str(raw.get("id", "")) for raw in mappings]
        try:
            assert_unique_ids(ids)
        except ValueError as exc:
            raise WorkflowError(
                str(exc),
                exit_code=ExitCode.VALIDATION_FAILED,
                code="MODULE_ID_DUPLICATE",
            ) from exc
        modules = tuple(
            ModuleRecord(
                module_id=str(raw["id"]),
                owned_data=tuple(str(v) for v in raw.get("owned_data", [])),
                must_not_write=tuple(str(v) for v in raw.get("must_not_write", [])),
                writes=tuple(str(v) for v in raw.get("writes", [])),
                dependencies=tuple(str(v) for v in raw.get("dependencies", [])),
            )
            for raw in mappings
        )
        return cls(modules)

    def _assert_acyclic(self) -> None:
        visiting: set[str] = set()
        visited: set[str] = set()

        def visit(module_id: str) -> None:
            if module_id in visited:
                return
            if module_id in visiting:
                raise WorkflowError(
                    f"module dependency cycle detected at {module_id}",
                    exit_code=ExitCode.VALIDATION_FAILED,
                    code="MODULE_DEPENDENCY_CYCLE",
                )
            visiting.add(module_id)
            record = self.by_id.get(module_id)
            if record is not None:
                for dependency in record.dependencies:
                    if dependency in self.by_id:
                        visit(dependency)
            visiting.remove(module_id)
            visited.add(module_id)

        for module_id in sorted(self.by_id):
            visit(module_id)


INTERACTION_TYPES = {
    "SYNC_QUERY",
    "SYNC_COMMAND",
    "SAME_REQUEST_ORCHESTRATION",
    "DOMAIN_EVENT",
    "BACKGROUND_JOB",
    "OUTBOX_EVENT",
    "EXTERNAL_WEBHOOK",
}


@dataclass(frozen=True)
class InteractionRecord:
    interaction_id: str
    interaction_type: str
    producer: str
    consumer: str
    transaction_boundary: str
    idempotency: str
    timeout: str
    failure_behavior: str


class InteractionCatalog:
    REQUIRED_FIELDS = {
        "id",
        "type",
        "producer",
        "consumer",
        "transaction_boundary",
        "idempotency",
        "timeout",
        "failure_behavior",
    }

    def __init__(self, interactions: tuple[InteractionRecord, ...]) -> None:
        self.interactions = tuple(sorted(interactions, key=lambda record: record.interaction_id))

    @classmethod
    def from_mappings(cls, mappings: list[dict[str, Any]]) -> "InteractionCatalog":
        records: list[InteractionRecord] = []
        for raw in mappings:
            missing = sorted(cls.REQUIRED_FIELDS - set(raw))
            if missing:
                raise WorkflowError(
                    f"interaction is missing required field(s): {', '.join(missing)}",
                    exit_code=ExitCode.VALIDATION_FAILED,
                    code="INTERACTION_INCOMPLETE",
                )
            interaction_type = str(raw["type"])
            if interaction_type not in INTERACTION_TYPES:
                raise WorkflowError(
                    f"unknown interaction type: {interaction_type}",
                    exit_code=ExitCode.VALIDATION_FAILED,
                    code="INTERACTION_TYPE_INVALID",
                )
            records.append(
                InteractionRecord(
                    interaction_id=str(raw["id"]),
                    interaction_type=interaction_type,
                    producer=str(raw["producer"]),
                    consumer=str(raw["consumer"]),
                    transaction_boundary=str(raw["transaction_boundary"]),
                    idempotency=str(raw["idempotency"]),
                    timeout=str(raw["timeout"]),
                    failure_behavior=str(raw["failure_behavior"]),
                )
            )
        try:
            assert_unique_ids(record.interaction_id for record in records)
        except ValueError as exc:
            raise WorkflowError(
                str(exc),
                exit_code=ExitCode.VALIDATION_FAILED,
                code="INTERACTION_ID_DUPLICATE",
            ) from exc
        return cls(tuple(records))
