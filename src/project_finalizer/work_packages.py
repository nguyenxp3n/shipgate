from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass
from heapq import heappop, heappush

from project_finalizer.errors import ExitCode, WorkflowError


@dataclass(frozen=True)
class WorkPackage:
    wp_id: str
    title: str
    state: str
    purpose: str
    depends_on: tuple[str, ...]
    authority_refs: tuple[str, ...]
    allowed_paths: tuple[str, ...]
    forbidden_paths: tuple[str, ...]
    acceptance_commands: tuple[str, ...]
    stop_conditions: tuple[str, ...]
    protected_surface: bool = False
    completion_evidence: tuple[str, ...] = ()
    decision_requirements: tuple[str, ...] = ()

    def validate(self) -> None:
        if self.state not in {"READY", "BLOCKED", "COMPLETE"}:
            raise WorkflowError(
                f"invalid work package state: {self.state}",
                exit_code=ExitCode.VALIDATION_FAILED,
                code="WP_STATE_INVALID",
            )
        if self.state == "READY":
            missing: list[str] = []
            if not self.purpose.strip():
                missing.append("purpose")
            if not self.authority_refs:
                missing.append("authority_refs")
            if not self.allowed_paths:
                missing.append("allowed_paths")
            if not self.acceptance_commands:
                missing.append("acceptance_commands")
            if self.protected_surface and not self.stop_conditions:
                missing.append("stop_conditions")
            if missing:
                raise WorkflowError(
                    f"READY work package {self.wp_id} is missing: {', '.join(missing)}",
                    exit_code=ExitCode.VALIDATION_FAILED,
                    code="WP_READY_CONTRACT_INCOMPLETE",
                )


class WorkPackageGraph:
    def __init__(self, edges: dict[str, tuple[str, ...]]) -> None:
        if "WP-000" not in edges:
            raise WorkflowError(
                "work package graph requires WP-000 entrypoint",
                exit_code=ExitCode.VALIDATION_FAILED,
                code="WP_ENTRYPOINT_MISSING",
            )
        unknown = sorted({dep for deps in edges.values() for dep in deps if dep not in edges})
        if unknown:
            raise WorkflowError(
                f"work package graph references unknown dependencies: {', '.join(unknown)}",
                exit_code=ExitCode.VALIDATION_FAILED,
                code="WP_DEPENDENCY_UNKNOWN",
            )
        self.edges = {key: tuple(sorted(set(value))) for key, value in edges.items()}
        self._order = self._compute_topological_order()
        if self.edges["WP-000"]:
            raise WorkflowError(
                "WP-000 entrypoint cannot depend on another work package",
                exit_code=ExitCode.VALIDATION_FAILED,
                code="WP_ENTRYPOINT_DEPENDENCY_INVALID",
            )

    @classmethod
    def from_edges(cls, edges: dict[str, tuple[str, ...]]) -> WorkPackageGraph:
        return cls(edges)

    def _compute_topological_order(self) -> tuple[str, ...]:
        indegree = {node: len(deps) for node, deps in self.edges.items()}
        dependents: dict[str, list[str]] = {node: [] for node in self.edges}
        for node, deps in self.edges.items():
            for dep in deps:
                dependents[dep].append(node)
        ready: list[str] = []
        for node, degree in indegree.items():
            if degree == 0:
                heappush(ready, node)
        order: list[str] = []
        while ready:
            node = heappop(ready)
            order.append(node)
            for dependent in sorted(dependents[node]):
                indegree[dependent] -= 1
                if indegree[dependent] == 0:
                    heappush(ready, dependent)
        if len(order) != len(self.edges):
            raise WorkflowError(
                "work package dependency cycle detected",
                exit_code=ExitCode.VALIDATION_FAILED,
                code="WP_DEPENDENCY_CYCLE",
            )
        return tuple(order)

    def topological_order(self) -> tuple[str, ...]:
        return self._order

    def ready_packages(self, completed: Iterable[str] = ()) -> tuple[str, ...]:
        done = set(completed)
        return tuple(
            node for node in self._order if node not in done and set(self.edges[node]) <= done
        )


def compile_wp_skeletons(
    module_dependencies: dict[str, tuple[str, ...]],
    *,
    protected_edges: set[tuple[str, str]] | None = None,
) -> tuple[WorkPackage, ...]:
    protected_edges = protected_edges or set()
    module_to_wp = {
        module_id: f"WP-{index:03d}"
        for index, module_id in enumerate(sorted(module_dependencies), start=1)
    }
    packages: list[WorkPackage] = [
        WorkPackage(
            wp_id="WP-000",
            title="Repository bootstrap",
            state="READY",
            purpose="Create the repository/toolchain foundation required by every later package.",
            depends_on=(),
            authority_refs=("docs/agent-spec/AGENT-OPERATING-MANUAL.md",),
            allowed_paths=("/",),
            forbidden_paths=(),
            acceptance_commands=("task qa",),
            stop_conditions=("protected decision required",),
            protected_surface=True,
        )
    ]
    for module_id in sorted(module_dependencies):
        deps = tuple(
            sorted(
                {
                    "WP-000",
                    *(module_to_wp[d] for d in module_dependencies[module_id] if d in module_to_wp),
                }
            )
        )
        decisions = tuple(
            sorted(
                f"protected-edge:{module_id}->{dep}"
                for dep in module_dependencies[module_id]
                if (module_id, dep) in protected_edges
            )
        )
        packages.append(
            WorkPackage(
                wp_id=module_to_wp[module_id],
                title=f"Implement {module_id}",
                state="BLOCKED" if decisions else "READY",
                purpose=f"Implement the approved contract for module {module_id}.",
                depends_on=deps,
                authority_refs=(f"docs/agent-spec/modules/{module_id}.md",),
                allowed_paths=(f"internal/{module_id}/**",),
                forbidden_paths=(),
                acceptance_commands=(f"task test:{module_id}",),
                stop_conditions=("public contract change required", "protected decision required"),
                protected_surface=True,
                decision_requirements=decisions,
            )
        )
    WorkPackageGraph.from_edges({package.wp_id: package.depends_on for package in packages})
    for package in packages:
        if package.state == "READY":
            package.validate()
    return tuple(packages)
