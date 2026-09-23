from pathlib import Path

from project_finalizer.cli import main
from project_finalizer.decisions import DecisionStore
from project_finalizer.io import ProjectFS
from project_finalizer.project import initialize_project
from project_finalizer.state import StateStore


def test_finalize_stops_for_pending_human_decision(tmp_path: Path, capsys):
    root = tmp_path / "project"
    root.mkdir()
    initialize_project(root, profile="web-saas")
    store = DecisionStore(ProjectFS(root))
    store.create("DR-001", subject="license", question="Choose license", options=("A", "B"))
    code = main(["finalize", "--project", str(root)])
    err = capsys.readouterr().err
    assert code == 20
    assert "DR-001" in err
    assert StateStore(ProjectFS(root)).load().current == "RAW_INPUT"


def test_finalize_stops_at_next_agent_action_and_creates_packet(tmp_path: Path, capsys):
    root = tmp_path / "project"
    root.mkdir()
    initialize_project(root, profile="web-saas")
    code = main(["finalize", "--project", str(root)])
    err = capsys.readouterr().err
    assert code == 30
    assert "AGENT_ROLE_OUTPUT_REQUIRED" in err
    assert (root / ".workflow/role-packets/discovery/OUTPUT-CONTRACT.yaml").is_file()
    assert StateStore(ProjectFS(root)).load().current == "RAW_INPUT"


def test_finalize_from_corrective_complete_runs_real_readiness_and_release(tmp_path: Path):
    root = tmp_path / "project"
    root.mkdir()
    initialize_project(root, profile="web-saas")
    fs = ProjectFS(root)
    fs.write_yaml_atomic(
        StateStore.PATH,
        {
            "current": "CORRECTIVE_COMPLETE",
            "previous": "SENIOR_AUDITED",
            "allowed_next": ["BUILD_READY"],
            "gates": {},
        },
    )
    wp_dir = root / "docs/agent-spec/work-packages"
    wp_dir.mkdir(parents=True)
    (wp_dir / "WP-000.md").write_text("# WP-000\n", encoding="utf-8")

    code = main(["finalize", "--project", str(root)])

    assert code == 0
    assert StateStore(fs).load().current == "FINAL_RELEASE"
    archive = root.parent / f"{root.name}-final-spec.zip"
    assert archive.is_file()
    assert Path(f"{archive}.sha256").is_file()
