from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import yaml
from packaging.specifiers import InvalidSpecifier, SpecifierSet
from packaging.version import InvalidVersion, Version

from project_finalizer.errors import ExitCode, WorkflowError
from project_finalizer.schemas import SchemaRegistry


@dataclass(frozen=True)
class ProfileManifest:
    profile_id: str
    version: str
    core_compatibility: str
    required_capabilities: tuple[str, ...]
    optional_capabilities: tuple[str, ...]
    validators: tuple[str, ...]


def _find_schema_root(start: Path) -> Path:
    for parent in (start, *start.parents):
        candidate = parent / "schemas"
        if (candidate / "profile.schema.json").is_file():
            return candidate
    raise WorkflowError(
        f"could not locate schema root from {start}",
        exit_code=ExitCode.PROFILE_ERROR,
        code="PROFILE_SCHEMA_ROOT_NOT_FOUND",
    )


def assert_core_compatible(profile: ProfileManifest, core_version: str) -> None:
    try:
        spec = SpecifierSet(profile.core_compatibility)
        version = Version(core_version)
    except (InvalidSpecifier, InvalidVersion) as exc:
        raise WorkflowError(
            f"invalid profile compatibility expression: {profile.core_compatibility}",
            exit_code=ExitCode.PROFILE_ERROR,
            code="PROFILE_CORE_COMPATIBILITY_INVALID",
        ) from exc
    if version not in spec:
        raise WorkflowError(
            f"profile {profile.profile_id}@{profile.version} is incompatible with core {core_version}",
            exit_code=ExitCode.PROFILE_ERROR,
            code="PROFILE_CORE_INCOMPATIBLE",
        )


def load_profile_manifest(path: Path, *, core_version: str) -> ProfileManifest:
    try:
        raw = yaml.safe_load(path.read_text(encoding="utf-8"))
    except (OSError, yaml.YAMLError) as exc:
        raise WorkflowError(
            f"failed to load profile manifest {path}: {exc}",
            exit_code=ExitCode.PROFILE_ERROR,
            code="PROFILE_MANIFEST_INVALID",
        ) from exc
    SchemaRegistry(_find_schema_root(path.parent)).validate("profile", raw)
    profile_raw = raw["profile"]
    profile = ProfileManifest(
        profile_id=str(profile_raw["id"]),
        version=str(profile_raw["version"]),
        core_compatibility=str(profile_raw["workflow_core_compatibility"]),
        required_capabilities=tuple(str(v) for v in raw["required_capabilities"]),
        optional_capabilities=tuple(str(v) for v in raw["optional_capabilities"]),
        validators=tuple(str(v) for v in raw["validators"]),
    )
    assert_core_compatible(profile, core_version)
    return profile
