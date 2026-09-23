from __future__ import annotations

import hashlib
from dataclasses import asdict, dataclass
from pathlib import Path

from project_finalizer.errors import ExitCode, WorkflowError
from project_finalizer.io import ProjectFS


@dataclass(frozen=True)
class InputItem:
    path: str
    size: int
    sha256: str
    media_class: str


@dataclass(frozen=True)
class InputInventory:
    items: tuple[InputItem, ...]


@dataclass(frozen=True)
class RequirementRecord:
    requirement_id: str
    source_path: str
    location: str
    statement: str
    classification: str
    confidence: str = "explicit"
    status: str = "unresolved_authority"


@dataclass(frozen=True)
class ConflictClaim:
    source: str
    statement: str


@dataclass(frozen=True)
class ConflictRecord:
    conflict_id: str
    subject: str
    claims: tuple[ConflictClaim, ...]
    status: str = "requires_resolution"


def _media_class(path: Path) -> str:
    suffix = path.suffix.lower()
    if suffix in {".md", ".txt", ".rst"}:
        return "text"
    if suffix in {".yaml", ".yml", ".json", ".toml"}:
        return "structured_text"
    if suffix == ".pdf":
        return "pdf"
    if suffix in {".png", ".jpg", ".jpeg", ".webp", ".gif", ".svg"}:
        return "image"
    if suffix in {".xlsx", ".csv", ".tsv"}:
        return "spreadsheet"
    if suffix in {".pptx", ".odp"}:
        return "slides"
    if suffix in {".py", ".go", ".rs", ".js", ".ts", ".tsx", ".java"}:
        return "code"
    return "binary"


def scan_inputs(root: Path) -> tuple[InputItem, ...]:
    real_root = root.resolve(strict=False)
    if not root.is_dir():
        raise WorkflowError(
            f"input root does not exist or is not a directory: {root}",
            exit_code=ExitCode.VALIDATION_FAILED,
            code="INPUT_ROOT_INVALID",
        )
    items: list[InputItem] = []
    for path in sorted(root.rglob("*"), key=lambda p: p.relative_to(root).as_posix()):
        if path.is_symlink():
            raise WorkflowError(
                f"input symlink is not allowed: {path.relative_to(root).as_posix()}",
                exit_code=ExitCode.VALIDATION_FAILED,
                code="INPUT_SYMLINK_FORBIDDEN",
            )
        if not path.is_file():
            continue
        resolved = path.resolve(strict=True)
        if resolved != real_root and real_root not in resolved.parents:
            raise WorkflowError(
                f"input path is outside input root: {path}",
                exit_code=ExitCode.VALIDATION_FAILED,
                code="INPUT_PATH_OUTSIDE_ROOT",
            )
        data = path.read_bytes()
        items.append(
            InputItem(
                path=path.relative_to(root).as_posix(),
                size=len(data),
                sha256=hashlib.sha256(data).hexdigest(),
                media_class=_media_class(path),
            )
        )
    return tuple(items)


def write_intake_bundle(
    fs: ProjectFS,
    inventory: InputInventory,
    requirements: tuple[RequirementRecord, ...] = (),
    conflicts: tuple[ConflictRecord, ...] = (),
) -> None:
    fs.write_yaml_atomic(
        ".workflow/intake/input-inventory.yaml",
        {"items": [asdict(item) for item in inventory.items]},
    )
    fs.write_yaml_atomic(
        ".workflow/intake/requirements.yaml",
        {"requirements": [asdict(item) for item in requirements]},
    )
    fs.write_yaml_atomic(
        ".workflow/intake/conflicts.yaml",
        {"conflicts": [asdict(item) for item in conflicts]},
    )
