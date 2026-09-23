from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Mapping

import yaml

_ENABLED_STATES = {"required", "optional_enabled"}


@dataclass(frozen=True)
class ExtensionManifest:
    extension_id: str
    capability: str
    documents: tuple[str, ...]
    schemas: tuple[str, ...]
    validators: tuple[str, ...]
    testing: tuple[str, ...]
    audit_rules: tuple[str, ...]
    work_package_rules: tuple[str, ...]
    root: Path

    def obligation_paths(self) -> tuple[Path, ...]:
        refs = (*self.documents, *self.schemas, *self.testing, *self.audit_rules, *self.work_package_rules)
        return tuple(self.root / ref for ref in refs)


class ExtensionRegistry:
    def __init__(self, root: Path) -> None:
        self.root = Path(root)

    def _load_manifest(self, directory: Path) -> ExtensionManifest:
        path = directory / "EXTENSION-MANIFEST.yaml"
        if not path.is_file():
            raise ValueError(f"missing extension manifest: {directory.name}")
        raw = yaml.safe_load(path.read_text(encoding="utf-8"))
        if not isinstance(raw, dict):
            raise ValueError(f"invalid extension manifest: {directory.name}")
        required = (
            "id",
            "capability",
            "documents",
            "schemas",
            "validators",
            "testing",
            "audit_rules",
            "work_package_rules",
        )
        if any(key not in raw for key in required):
            raise ValueError("incomplete extension obligation pack")
        list_fields = {key: raw.get(key) for key in required[2:]}
        if any(not isinstance(value, list) for value in list_fields.values()):
            raise ValueError("incomplete extension obligation pack")
        if not raw["documents"] or not raw["validators"] or not raw["testing"] or not raw["audit_rules"] or not raw["work_package_rules"]:
            raise ValueError("incomplete extension obligation pack")
        manifest = ExtensionManifest(
            extension_id=str(raw["id"]),
            capability=str(raw["capability"]),
            documents=tuple(str(v) for v in raw["documents"]),
            schemas=tuple(str(v) for v in raw["schemas"]),
            validators=tuple(str(v) for v in raw["validators"]),
            testing=tuple(str(v) for v in raw["testing"]),
            audit_rules=tuple(str(v) for v in raw["audit_rules"]),
            work_package_rules=tuple(str(v) for v in raw["work_package_rules"]),
            root=directory,
        )
        missing = [str(path.relative_to(directory)) for path in manifest.obligation_paths() if not path.is_file()]
        if missing:
            raise ValueError(f"incomplete extension obligation pack: missing {', '.join(sorted(missing))}")
        return manifest

    def manifests(self) -> tuple[ExtensionManifest, ...]:
        if not self.root.is_dir():
            return ()
        loaded = [self._load_manifest(path) for path in sorted(self.root.iterdir()) if path.is_dir()]
        return tuple(sorted(loaded, key=lambda item: item.extension_id))

    def load_enabled(self, capabilities: Mapping[str, str]) -> tuple[ExtensionManifest, ...]:
        enabled = {name for name, state in capabilities.items() if str(state) in _ENABLED_STATES}
        if not enabled:
            return ()
        loaded: list[ExtensionManifest] = []
        if not self.root.is_dir():
            # An enabled capability with no extension root is a partial obligation pack.
            raise ValueError("incomplete extension obligation pack")
        for directory in sorted(path for path in self.root.iterdir() if path.is_dir()):
            path = directory / "EXTENSION-MANIFEST.yaml"
            if not path.is_file():
                continue
            raw = yaml.safe_load(path.read_text(encoding="utf-8"))
            capability = str(raw.get("capability", "")) if isinstance(raw, dict) else ""
            if capability in enabled:
                loaded.append(self._load_manifest(directory))
        found = {item.capability for item in loaded}
        extension_capabilities = set()
        for directory in sorted(path for path in self.root.iterdir() if path.is_dir()):
            manifest_path = directory / "EXTENSION-MANIFEST.yaml"
            if manifest_path.is_file():
                raw = yaml.safe_load(manifest_path.read_text(encoding="utf-8"))
                if isinstance(raw, dict) and raw.get("capability"):
                    extension_capabilities.add(str(raw["capability"]))
        missing = sorted((enabled & extension_capabilities) - found)
        if missing:
            raise ValueError(f"incomplete extension obligation pack: {missing[0]}")
        return tuple(sorted(loaded, key=lambda item: item.extension_id))
