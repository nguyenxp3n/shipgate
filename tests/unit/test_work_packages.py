import pytest

from project_finalizer.errors import WorkflowError
from project_finalizer.work_packages import WorkPackage, WorkPackageGraph


def test_wp_graph_rejects_cycle():
    with pytest.raises(WorkflowError, match="cycle"):
        WorkPackageGraph.from_edges({"WP-000": ("WP-001",), "WP-001": ("WP-000",)})


def test_wp_graph_requires_wp000_entrypoint():
    with pytest.raises(WorkflowError, match="WP-000"):
        WorkPackageGraph.from_edges({"WP-001": ()})


def test_topological_order_is_deterministic():
    graph = WorkPackageGraph.from_edges(
        {"WP-000": (), "WP-001": ("WP-000",), "WP-002": ("WP-000",), "WP-003": ("WP-001", "WP-002")}
    )
    assert graph.topological_order() == ("WP-000", "WP-001", "WP-002", "WP-003")


def test_ready_wp_requires_scope_acceptance_and_stop_contracts():
    package = WorkPackage(
        wp_id="WP-001",
        title="Auth",
        state="READY",
        purpose="",
        depends_on=("WP-000",),
        authority_refs=(),
        allowed_paths=(),
        forbidden_paths=(),
        acceptance_commands=(),
        stop_conditions=(),
        protected_surface=True,
    )
    with pytest.raises(WorkflowError, match="READY work package"):
        package.validate()
