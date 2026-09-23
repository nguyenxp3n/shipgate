import pytest

from project_finalizer.errors import WorkflowError
from project_finalizer.modules import InteractionCatalog, ModuleCatalog


def test_two_modules_cannot_own_same_table():
    raw = [
        {"id": "users", "owned_data": ["users"], "must_not_write": []},
        {"id": "billing", "owned_data": ["users"], "must_not_write": []},
    ]
    with pytest.raises(WorkflowError, match="duplicate owner"):
        ModuleCatalog.from_mappings(raw)


def test_declared_foreign_write_is_rejected():
    raw = [
        {"id": "users", "owned_data": ["users"], "must_not_write": []},
        {"id": "billing", "owned_data": ["invoices"], "writes": ["users"]},
    ]
    with pytest.raises(WorkflowError, match="foreign write"):
        ModuleCatalog.from_mappings(raw)


def test_interaction_requires_complete_delivery_semantics():
    with pytest.raises(WorkflowError, match="missing"):
        InteractionCatalog.from_mappings(
            [
                {
                    "id": "INT-001",
                    "type": "DOMAIN_EVENT",
                    "producer": "billing",
                    "consumer": "analytics",
                }
            ]
        )


def test_module_dependency_cycle_is_rejected():
    with pytest.raises(WorkflowError, match="cycle"):
        ModuleCatalog.from_mappings(
            [
                {"id": "a", "owned_data": [], "must_not_write": [], "dependencies": ["b"]},
                {"id": "b", "owned_data": [], "must_not_write": [], "dependencies": ["a"]},
            ]
        )
