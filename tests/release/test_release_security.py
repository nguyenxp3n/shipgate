from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile

import pytest

from project_finalizer.errors import WorkflowError
from project_finalizer.release import stage_release, verify_zip


def test_stage_rejects_external_symlink(tmp_path: Path) -> None:
    source = tmp_path / "source"
    source.mkdir()
    outside = tmp_path / "secret.txt"
    outside.write_text("secret", encoding="utf-8")
    (source / "leak").symlink_to(outside)
    with pytest.raises(WorkflowError, match="unsafe symlink") as exc:
        stage_release(source, tmp_path / "stage")
    assert exc.value.code == "RELEASE_UNSAFE_SYMLINK"


@pytest.mark.parametrize("member", ["../escape.txt", "/absolute.txt"])
def test_verify_zip_rejects_traversal_members(tmp_path: Path, member: str) -> None:
    archive = tmp_path / "bad.zip"
    with ZipFile(archive, "w", compression=ZIP_DEFLATED) as handle:
        handle.writestr(member, "bad")
    with pytest.raises(WorkflowError) as exc:
        verify_zip(archive)
    assert exc.value.code == "RELEASE_UNSAFE_ARCHIVE_MEMBER"
