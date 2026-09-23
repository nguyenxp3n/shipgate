from pathlib import Path

from project_finalizer.agents.registry import RoleRegistry


def test_senior_auditor_is_read_only_for_canonical_sources(repo_root: Path) -> None:
    registry = RoleRegistry.load(repo_root / "prompts/ROLE-REGISTRY.yaml")
    role = registry.get("senior-auditor")
    assert role.can_write("docs/audits/QA.md") is True
    assert role.can_write("contracts/openapi/openapi.yaml") is False
    assert role.can_write("docs/core/PRODUCT-SPEC.md") is False


def test_all_declared_role_contract_packages_exist(repo_root: Path) -> None:
    registry = RoleRegistry.load(repo_root / "prompts/ROLE-REGISTRY.yaml")
    for role in registry.roles:
        root = repo_root / "prompts" / role.role_id
        for name in (
            "SYSTEM-ROLE.md",
            "INPUT-CONTRACT.md",
            "OUTPUT-CONTRACT.md",
            "STOP-CONDITIONS.md",
            "QUALITY-RUBRIC.md",
        ):
            assert (root / name).is_file(), f"{role.role_id}/{name}"
