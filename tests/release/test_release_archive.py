from pathlib import Path

from project_finalizer.release import build_zip, stage_release, verify_reextract, verify_zip, write_sha256sums


def test_stage_archive_and_reextract_are_byte_identical(tmp_path: Path) -> None:
    source = tmp_path / "source"
    source.mkdir()
    (source / "a.txt").write_text("alpha\n", encoding="utf-8")
    (source / "nested").mkdir()
    (source / "nested/b.txt").write_text("beta\n", encoding="utf-8")
    stage = tmp_path / "stage"
    stage_release(source, stage)
    write_sha256sums(stage)
    archive = tmp_path / "release.zip"
    build_zip(stage, archive)
    verify_zip(archive)
    verify_reextract(stage, archive, tmp_path / "extract")


def test_repeated_archives_have_identical_hash(tmp_path: Path) -> None:
    source = tmp_path / "source"
    source.mkdir()
    (source / "a.txt").write_text("same\n", encoding="utf-8")
    stage = tmp_path / "stage"
    stage_release(source, stage)
    write_sha256sums(stage)
    first = build_zip(stage, tmp_path / "one.zip")
    second = build_zip(stage, tmp_path / "two.zip")
    assert first == second
