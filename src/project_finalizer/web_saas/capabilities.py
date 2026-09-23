from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from typing import Mapping

from project_finalizer.profiles import ProfileManifest


class CapabilityState(StrEnum):
    REQUIRED = "required"
    OPTIONAL_ENABLED = "optional_enabled"
    DISABLED = "disabled"

    @classmethod
    def parse(cls, value: str) -> "CapabilityState":
        try:
            return cls(value)
        except ValueError as exc:
            raise ValueError(f"invalid capability state: {value}") from exc


REQUIRED_CAPABILITIES = (
    "frontend",
    "api",
    "auth",
    "authorization",
    "database",
    "observability",
)

OPTIONAL_CAPABILITIES = (
    "organizations",
    "cache",
    "jobs",
    "events",
    "files",
    "email",
    "notifications",
    "admin",
    "search",
    "analytics",
    "payments",
    "ai_integration",
    "realtime",
    "pwa",
    "webhooks",
)

KNOWN_CAPABILITIES = frozenset((*REQUIRED_CAPABILITIES, *OPTIONAL_CAPABILITIES))


@dataclass(frozen=True)
class CapabilitySet:
    states: tuple[tuple[str, CapabilityState], ...]

    @classmethod
    def from_mapping(cls, raw: Mapping[str, str]) -> "CapabilitySet":
        parsed: list[tuple[str, CapabilityState]] = []
        for name, value in sorted(raw.items()):
            if name not in KNOWN_CAPABILITIES:
                raise ValueError(f"unknown capability: {name}")
            parsed.append((name, CapabilityState.parse(value)))
        return cls(tuple(parsed))

    @classmethod
    def resolve(
        cls,
        profile: ProfileManifest,
        overrides: Mapping[str, str] | None = None,
    ) -> "CapabilitySet":
        overrides = overrides or {}
        allowed = set(profile.required_capabilities) | set(profile.optional_capabilities)
        unknown = sorted(set(overrides) - allowed)
        if unknown:
            raise ValueError(f"unknown capability: {unknown[0]}")
        raw: dict[str, str] = {
            name: CapabilityState.REQUIRED.value for name in profile.required_capabilities
        }
        raw.update(
            {name: CapabilityState.DISABLED.value for name in profile.optional_capabilities}
        )
        for name, value in overrides.items():
            state = CapabilityState.parse(value)
            if name in profile.required_capabilities and state is not CapabilityState.REQUIRED:
                raise ValueError(f"required capability cannot be disabled or downgraded: {name}")
            raw[name] = state.value
        return cls.from_mapping(raw)

    def state(self, name: str) -> CapabilityState:
        for candidate, state in self.states:
            if candidate == name:
                return state
        return CapabilityState.DISABLED

    def enabled(self, name: str) -> bool:
        return self.state(name) in {CapabilityState.REQUIRED, CapabilityState.OPTIONAL_ENABLED}

    def obligation_sets(self) -> tuple[str, ...]:
        return tuple(name for name, state in self.states if state is not CapabilityState.DISABLED)

    def to_mapping(self) -> dict[str, str]:
        return {name: state.value for name, state in self.states}
