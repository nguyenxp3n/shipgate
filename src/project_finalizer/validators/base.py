from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Protocol

from project_finalizer.models import ValidationReport


@dataclass(frozen=True)
class ValidationContext:
    project_root: Path
    authority_refs: tuple[str, ...] = ()
    known_ids: frozenset[str] = field(default_factory=frozenset)
    known_authority_ids: frozenset[str] = field(default_factory=frozenset)
    authority_matrix_path: Path | None = None
    modules: tuple[dict[str, Any], ...] = ()
    work_packages: tuple[dict[str, Any], ...] = ()
    required_paths: tuple[str, ...] = ()
    generated_artifacts: tuple[dict[str, Any], ...] = ()
    activated_invariants: frozenset[str] = field(default_factory=frozenset)
    openapi_path: Path | None = None
    error_catalog: frozenset[str] = field(default_factory=frozenset)
    api_policy: dict[str, Any] = field(default_factory=dict)


class Validator(Protocol):
    name: str
    layer: str

    def validate(self, ctx: ValidationContext) -> ValidationReport: ...
