from pathlib import Path

from project_finalizer.cli import main
from project_finalizer.io import ProjectFS
from project_finalizer.project import initialize_project
from project_finalizer.state import ProjectState, StateStore


def _ready_project(root: Path) -> None:
    initialize_project(root, profile="web-saas")
    fs = ProjectFS(root)
    state = ProjectState(
        current="CORRECTIVE_COMPLETE",
        previous="SENIOR_AUDITED",
        allowed_next=("BUILD_READY",),
        gates={},
    )
    fs.write_yaml_atomic(StateStore.PATH, state.to_mapping())
    wp = root / "docs/agent-spec/work-packages"
    wp.mkdir(parents=True)
    (wp / "WP-000.md").write_text("# WP-000\n", encoding="utf-8")


def test_release_readiness_failure_creates_no_zip(tmp_path: Path) -> None:
    root = tmp_path / "project"
    root.mkdir()
    initialize_project(root, profile="web-saas")
    output = tmp_path / "release.zip"
    code = main(["release", "--project", str(root), "--output", str(output)])
    assert code == 70
    assert not output.exists()


def test_release_ready_project_emits_verified_zip_and_final_state(tmp_path: Path) -> None:
    root = tmp_path / "project"
    root.mkdir()
    _ready_project(root)
    output = tmp_path / "release.zip"
    code = main(["release", "--project", str(root), "--output", str(output)])
    assert code == 0
    assert output.is_file()
    assert Path(f"{output}.sha256").is_file()
    assert StateStore(ProjectFS(root)).load().current == "FINAL_RELEASE"


def _ready_workflow_repository(root: Path, repo_root: Path) -> None:
    import shutil

    for relative in (
        "self-hosting",
        "schemas",
    ):
        shutil.copytree(repo_root / relative, root / relative)
    for relative in (
        "WORKFLOW-MANIFEST.yaml",
        "Taskfile.yml",
        "pyproject.toml",
        "LICENSE",
        "docs/decisions/DR-WF-001-license.yaml",
        "docs/superpowers/specs/shipgate-architecture-spec.md",
        "docs/superpowers/plans/shipgate-master-plan.md",
    ):
        source = repo_root / relative
        target = root / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, target)


def test_release_workflow_repository_uses_self_hosting_without_runtime_state(
    tmp_path: Path,
    repo_root: Path,
) -> None:
    root = tmp_path / "workflow-repo"
    root.mkdir()
    _ready_workflow_repository(root, repo_root)
    output = tmp_path / "workflow-v2.zip"

    code = main(["release", "--project", str(root), "--output", str(output)])

    assert code == 0
    assert output.is_file()
    assert Path(f"{output}.sha256").is_file()
    assert not (root / ".workflow").exists()
