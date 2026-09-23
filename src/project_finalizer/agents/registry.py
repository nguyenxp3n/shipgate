from __future__ import annotations

from dataclasses import dataclass
from fnmatch import fnmatchcase
from pathlib import Path
from typing import Any

import yaml


def _matches(path: str, patterns: tuple[str, ...]) -> bool:
    normalized = path.replace("\\", "/")
    return any(fnmatchcase(normalized, pattern) for pattern in patterns)


@dataclass(frozen=True)
class AgentRole:
    role_id: str
    read_globs: tuple[str, ...]
    write_globs: tuple[str, ...]
    forbidden_globs: tuple[str, ...]
    required_inputs: tuple[str, ...]
    output_contract: str
    fresh_context_preferred: bool
    canonical_writes_allowed: bool
    include_historical: bool = False

    def can_write(self, path: str) -> bool:
        if _matches(path, self.forbidden_globs):
            return False
        return _matches(path, self.write_globs)

    def can_read(self, path: str) -> bool:
        if not self.include_historical and _matches(path, ("docs/audits/historical/**",)):
            return False
        return _matches(path, self.read_globs)


class RoleRegistry:
    def __init__(self, roles: tuple[AgentRole, ...]) -> None:
        ids = [role.role_id for role in roles]
        if len(ids) != len(set(ids)):
            raise ValueError("duplicate agent role id")
        self.roles = tuple(sorted(roles, key=lambda role: role.role_id))
        self._by_id = {role.role_id: role for role in self.roles}

    @classmethod
    def load(cls, path: Path) -> RoleRegistry:
        raw: Any = yaml.safe_load(path.read_text(encoding="utf-8"))
        if not isinstance(raw, dict) or not isinstance(raw.get("roles"), list):
            raise ValueError("invalid role registry")
        roles = []
        for item in raw["roles"]:
            if not isinstance(item, dict):
                raise ValueError("invalid role registry entry")
            roles.append(
                AgentRole(
                    role_id=str(item["id"]),
                    read_globs=tuple(str(v) for v in item.get("read", [])),
                    write_globs=tuple(str(v) for v in item.get("write", [])),
                    forbidden_globs=tuple(str(v) for v in item.get("forbidden", [])),
                    required_inputs=tuple(str(v) for v in item.get("required_inputs", [])),
                    output_contract=str(item["output_contract"]),
                    fresh_context_preferred=bool(item.get("fresh_context_preferred", False)),
                    canonical_writes_allowed=bool(item.get("canonical_writes_allowed", False)),
                    include_historical=bool(item.get("include_historical", False)),
                )
            )
        return cls(tuple(roles))

    def get(self, role_id: str) -> AgentRole:
        try:
            return self._by_id[role_id]
        except KeyError as exc:
            raise KeyError(f"unknown agent role: {role_id}") from exc
