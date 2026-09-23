from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from project_finalizer.agents.registry import RoleRegistry


@dataclass(frozen=True)
class RolePacket:
    role_id: str
    contract_paths: tuple[str, ...]
    input_paths: tuple[str, ...]
    output_globs: tuple[str, ...]


def _workflow_root() -> Path:
    return Path(__file__).resolve().parents[3]


def build_role_packet(project_root: Path, role_id: str) -> RolePacket:
    project_root = Path(project_root).resolve()
    prompts_root = _workflow_root() / "prompts"
    registry = RoleRegistry.load(prompts_root / "ROLE-REGISTRY.yaml")
    role = registry.get(role_id)
    role_root = prompts_root / role_id
    contract_names = (
        "SYSTEM-ROLE.md",
        "INPUT-CONTRACT.md",
        "OUTPUT-CONTRACT.md",
        "STOP-CONDITIONS.md",
        "QUALITY-RUBRIC.md",
    )
    contract_paths = tuple((role_root / name).relative_to(_workflow_root()).as_posix() for name in contract_names)
    inputs: list[str] = []
    if project_root.is_dir():
        for path in sorted(project_root.rglob("*")):
            if not path.is_file() or path.is_symlink():
                continue
            relative = path.relative_to(project_root).as_posix()
            if role.can_read(relative):
                inputs.append(relative)
    missing_required = [ref for ref in role.required_inputs if not (project_root / ref).exists()]
    # Required inputs describe the expected contract but are not synthesized. Packet construction
    # remains useful during early phases, so missing items are omitted rather than guessed.
    inputs.extend(ref for ref in role.required_inputs if ref not in missing_required and ref not in inputs)
    return RolePacket(
        role_id=role_id,
        contract_paths=contract_paths,
        input_paths=tuple(sorted(set(inputs))),
        output_globs=role.write_globs,
    )
