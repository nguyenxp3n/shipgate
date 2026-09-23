from __future__ import annotations

import json
from pathlib import Path

import yaml

from project_finalizer.models import ValidationIssue, ValidationReport
from project_finalizer.validators import ValidationContext

_SKIP = {".git", ".worktrees", ".venv", "__pycache__", ".pytest_cache", ".mypy_cache", ".ruff_cache"}


class SyntaxValidator:
    name = "syntax"
    layer = "syntax"

    def validate(self, ctx: ValidationContext) -> ValidationReport:
        issues: list[ValidationIssue] = []
        root = ctx.project_root
        if not root.exists():
            return ValidationReport()
        for path in sorted(root.rglob("*")):
            if not path.is_file() or any(part in _SKIP for part in path.relative_to(root).parts):
                continue
            rel = path.relative_to(root).as_posix()
            try:
                if path.suffix in {".yaml", ".yml"}:
                    yaml.safe_load(path.read_text(encoding="utf-8"))
                elif path.suffix == ".json":
                    json.loads(path.read_text(encoding="utf-8"))
            except (OSError, UnicodeError, yaml.YAMLError, json.JSONDecodeError) as exc:
                code = "SYNTAX_JSON_INVALID" if path.suffix == ".json" else "SYNTAX_YAML_INVALID"
                issues.append(ValidationIssue(code, str(exc), "ERROR", path=rel))
        return ValidationReport(tuple(issues))
