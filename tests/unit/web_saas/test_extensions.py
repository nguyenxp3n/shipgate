from pathlib import Path

import pytest
import yaml

from project_finalizer.web_saas.extensions import ExtensionRegistry


def test_enabled_extension_missing_validator_is_rejected(tmp_path: Path) -> None:
    ext = tmp_path / "payments"
    ext.mkdir()
    (ext / "REQUIREMENTS.md").write_text("requirements\n", encoding="utf-8")
    (ext / "TESTING.yaml").write_text("checks: []\n", encoding="utf-8")
    (ext / "AUDIT-RULES.yaml").write_text("rules: []\n", encoding="utf-8")
    (ext / "WORK-PACKAGE-RULES.md").write_text("rules\n", encoding="utf-8")
    (ext / "EXTENSION-MANIFEST.yaml").write_text(
        yaml.safe_dump(
            {
                "id": "payments",
                "capability": "payments",
                "documents": ["REQUIREMENTS.md"],
                "schemas": [],
                "validators": [],
                "testing": ["TESTING.yaml"],
                "audit_rules": ["AUDIT-RULES.yaml"],
                "work_package_rules": ["WORK-PACKAGE-RULES.md"],
            }
        ),
        encoding="utf-8",
    )
    registry = ExtensionRegistry(tmp_path)
    with pytest.raises(ValueError, match="incomplete extension obligation pack"):
        registry.load_enabled({"payments": "optional_enabled"})


def test_disabled_extension_activates_no_obligations(tmp_path: Path) -> None:
    registry = ExtensionRegistry(tmp_path)
    assert registry.load_enabled({"payments": "disabled"}) == ()
