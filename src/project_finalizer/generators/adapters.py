from __future__ import annotations

import hashlib
import re
from collections.abc import Mapping
from pathlib import Path

import yaml

_MARKER = re.compile(r"\{\{([A-Z0-9_]+)\}\}")
_TEMPLATE_OUTPUTS = {
    "adapters/generic/AGENT.template.md": "AGENT.md",
    "adapters/codex/AGENTS.template.md": "AGENTS.md",
    "adapters/claude-code/CLAUDE.template.md": "CLAUDE.md",
    "adapters/gemini-antigravity/GEMINI.template.md": "GEMINI.md",
}


def _workflow_root() -> Path:
    return Path(__file__).resolve().parents[3]


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def render_adapter_template(text: str, substitutions: Mapping[str, str]) -> str:
    declared = set(_MARKER.findall(text))
    unknown = sorted(declared - set(substitutions))
    if unknown:
        raise ValueError(f"unknown adapter marker: {unknown[0]}")
    rendered = text
    for name in sorted(declared):
        rendered = rendered.replace("{{" + name + "}}", substitutions[name])
    leftover = _MARKER.search(rendered)
    if leftover:
        raise ValueError(f"unfilled adapter marker: {leftover.group(1)}")
    return rendered


def generate_adapters(project_root: Path, *, project_name: str, version: str) -> tuple[Path, ...]:
    project_root = Path(project_root).resolve()
    project_root.mkdir(parents=True, exist_ok=True)
    substitutions = {
        "PROJECT_NAME": project_name,
        "VERSION": version,
        "OPERATING_MANUAL": "docs/agent-spec/AGENT-OPERATING-MANUAL.md",
        "AUTHORITY_MATRIX": "docs/agent-spec/AUTHORITY-MATRIX.yaml",
        "SPEC_MANIFEST": "docs/agent-spec/SPEC-MANIFEST.yaml",
        "WORK_PACKAGES_README": "docs/agent-spec/work-packages/README.md",
        "WP000": "docs/agent-spec/work-packages/WP-000.md",
        "COMMAND_GATEWAY": "Taskfile.yml",
    }
    outputs: list[Path] = []
    manifest: list[dict[str, str]] = []
    workflow_root = _workflow_root()
    for template_rel, output_name in _TEMPLATE_OUTPUTS.items():
        template = workflow_root / template_rel
        text = render_adapter_template(template.read_text(encoding="utf-8"), substitutions)
        output = project_root / output_name
        output.write_text(text, encoding="utf-8")
        outputs.append(output)
        manifest.append(
            {
                "path": output_name,
                "template": template_rel,
                "sha256": _sha256(output),
            }
        )
    metadata = project_root / ".workflow"
    metadata.mkdir(parents=True, exist_ok=True)
    (metadata / "adapter-manifest.yaml").write_text(
        yaml.safe_dump({"adapters": manifest}, sort_keys=False),
        encoding="utf-8",
    )
    return tuple(outputs)
