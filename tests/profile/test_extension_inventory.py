from pathlib import Path

from project_finalizer.web_saas.extensions import ExtensionRegistry

EXTENSIONS = {
    "multi-tenant", "payments", "file-storage", "email", "realtime", "search",
    "ai-integration", "background-processing", "webhook-provider", "analytics", "pwa",
}
REQUIRED = {"EXTENSION-MANIFEST.yaml", "REQUIREMENTS.md", "TESTING.yaml", "AUDIT-RULES.yaml", "WORK-PACKAGE-RULES.md"}


def test_all_extension_packs_have_complete_inventory(repo_root: Path) -> None:
    root = repo_root / "profiles/web-saas/extensions"
    missing = []
    for extension in EXTENSIONS:
        for name in REQUIRED:
            if not (root / extension / name).is_file():
                missing.append(f"{extension}/{name}")
    assert sorted(missing) == []


def test_all_shipped_extensions_load_when_enabled(repo_root: Path) -> None:
    root = repo_root / "profiles/web-saas/extensions"
    registry = ExtensionRegistry(root)
    mapping = {
        "multi_tenant": "optional_enabled",
        "payments": "optional_enabled",
        "files": "optional_enabled",
        "email": "optional_enabled",
        "realtime": "optional_enabled",
        "search": "optional_enabled",
        "ai_integration": "optional_enabled",
        "jobs": "optional_enabled",
        "webhooks": "optional_enabled",
        "analytics": "optional_enabled",
        "pwa": "optional_enabled",
    }
    loaded = registry.load_enabled(mapping)
    assert {item.extension_id for item in loaded} == EXTENSIONS
