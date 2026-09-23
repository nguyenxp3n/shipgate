from __future__ import annotations

import hashlib
import shutil
from pathlib import Path, PurePosixPath
from zipfile import ZIP_DEFLATED, BadZipFile, ZipFile, ZipInfo

from project_finalizer.errors import ExitCode, WorkflowError

_FIXED_TIME = (1980, 1, 1, 0, 0, 0)
_EXCLUDED_DIRS = {
    ".git",
    ".venv",
    ".worktrees",
    ".superpowers",
    "__pycache__",
    ".pytest_cache",
    ".mypy_cache",
    ".ruff_cache",
}


def _excluded(relative: Path) -> bool:
    parts = relative.parts
    if any(part in _EXCLUDED_DIRS for part in parts):
        return True
    if relative.suffix == ".pyc":
        return True
    return (
        len(parts) >= 4
        and parts[0] == ".workflow"
        and parts[1] == "runs"
        and "partial" in parts[3:]
    )


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def stage_release(source: Path, staging: Path) -> Path:
    source = source.resolve()
    staging = staging.resolve()
    if not source.is_dir():
        raise WorkflowError(
            "release source is not a directory",
            exit_code=ExitCode.RELEASE_INTEGRITY_FAILED,
            code="RELEASE_SOURCE_INVALID",
        )
    if staging == source or source in staging.parents:
        raise WorkflowError(
            "staging must be outside the source tree",
            exit_code=ExitCode.RELEASE_INTEGRITY_FAILED,
            code="RELEASE_STAGE_INVALID",
        )
    if staging.exists():
        shutil.rmtree(staging)
    staging.mkdir(parents=True)
    for path in sorted(source.rglob("*"), key=lambda item: item.relative_to(source).as_posix()):
        relative = path.relative_to(source)
        if _excluded(relative):
            continue
        if path.is_symlink():
            raise WorkflowError(
                f"unsafe symlink in release source: {relative.as_posix()}",
                exit_code=ExitCode.RELEASE_INTEGRITY_FAILED,
                code="RELEASE_UNSAFE_SYMLINK",
            )
        target = staging / relative
        if path.is_dir():
            target.mkdir(parents=True, exist_ok=True)
        elif path.is_file():
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(path, target)
    return staging


def write_sha256sums(staging: Path) -> Path:
    staging = staging.resolve()
    entries: list[str] = []
    for path in sorted(staging.rglob("*"), key=lambda item: item.relative_to(staging).as_posix()):
        if path.is_file() and path.name != "SHA256SUMS.txt":
            entries.append(f"{sha256_file(path)}  {path.relative_to(staging).as_posix()}")
    output = staging / "SHA256SUMS.txt"
    output.write_text("\n".join(entries) + ("\n" if entries else ""), encoding="utf-8")
    return output


def _zip_info(relative: str) -> ZipInfo:
    info = ZipInfo(relative, date_time=_FIXED_TIME)
    info.compress_type = ZIP_DEFLATED
    info.create_system = 3
    info.external_attr = (0o100644 & 0xFFFF) << 16
    return info


def build_zip(staging: Path, archive: Path) -> str:
    staging = staging.resolve()
    archive = archive.resolve()
    archive.parent.mkdir(parents=True, exist_ok=True)
    with ZipFile(archive, "w", compression=ZIP_DEFLATED, compresslevel=9) as handle:
        for path in sorted(staging.rglob("*"), key=lambda item: item.relative_to(staging).as_posix()):
            if not path.is_file():
                continue
            relative = path.relative_to(staging).as_posix()
            handle.writestr(
                _zip_info(relative),
                path.read_bytes(),
                compress_type=ZIP_DEFLATED,
                compresslevel=9,
            )
    return sha256_file(archive)


def _safe_member(name: str) -> bool:
    normalized = name.replace("\\", "/")
    pure = PurePosixPath(normalized)
    return not pure.is_absolute() and ".." not in pure.parts and normalized not in {"", "."}


def verify_zip(archive: Path) -> None:
    try:
        with ZipFile(archive, "r") as handle:
            for info in handle.infolist():
                if not _safe_member(info.filename):
                    raise WorkflowError(
                        f"unsafe archive member: {info.filename}",
                        exit_code=ExitCode.RELEASE_INTEGRITY_FAILED,
                        code="RELEASE_UNSAFE_ARCHIVE_MEMBER",
                    )
            corrupt = handle.testzip()
            if corrupt is not None:
                raise WorkflowError(
                    f"corrupt archive member: {corrupt}",
                    exit_code=ExitCode.RELEASE_INTEGRITY_FAILED,
                    code="RELEASE_ARCHIVE_CORRUPT",
                )
    except WorkflowError:
        raise
    except (BadZipFile, OSError, ValueError) as exc:
        raise WorkflowError(
            f"invalid release archive: {exc}",
            exit_code=ExitCode.RELEASE_INTEGRITY_FAILED,
            code="RELEASE_ARCHIVE_INVALID",
        ) from exc


def verify_reextract(staging: Path, archive: Path, extraction: Path) -> None:
    staging = staging.resolve()
    extraction = extraction.resolve()
    verify_zip(archive)
    if extraction.exists():
        shutil.rmtree(extraction)
    extraction.mkdir(parents=True)
    with ZipFile(archive, "r") as handle:
        for info in handle.infolist():
            if not _safe_member(info.filename):
                raise WorkflowError(
                    f"unsafe archive member: {info.filename}",
                    exit_code=ExitCode.RELEASE_INTEGRITY_FAILED,
                    code="RELEASE_UNSAFE_ARCHIVE_MEMBER",
                )
            destination = extraction.joinpath(*PurePosixPath(info.filename).parts)
            destination.parent.mkdir(parents=True, exist_ok=True)
            if not info.is_dir():
                destination.write_bytes(handle.read(info))
    stage_files = {
        path.relative_to(staging).as_posix(): sha256_file(path)
        for path in staging.rglob("*")
        if path.is_file()
    }
    extracted_files = {
        path.relative_to(extraction).as_posix(): sha256_file(path)
        for path in extraction.rglob("*")
        if path.is_file()
    }
    if stage_files != extracted_files:
        raise WorkflowError(
            "re-extracted release tree differs from staging",
            exit_code=ExitCode.RELEASE_INTEGRITY_FAILED,
            code="RELEASE_REEXTRACT_MISMATCH",
        )


def write_zip_sidecar(archive: Path) -> Path:
    digest = sha256_file(archive)
    sidecar = Path(f"{archive}.sha256")
    sidecar.write_text(f"{digest}  {archive.name}\n", encoding="utf-8")
    return sidecar
