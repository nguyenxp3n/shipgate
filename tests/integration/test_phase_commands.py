from pathlib import Path

import yaml

from project_finalizer.cli import main
from project_finalizer.io import ProjectFS
from project_finalizer.project import initialize_project
from project_finalizer.state import StateStore


def test_discover_missing_role_output_creates_packet_and_fails(tmp_path: Path, capsys):
    root = tmp_path / "project"
    root.mkdir()
    initialize_project(root, profile="web-saas")
    code = main(["discover", "--project", str(root)])
    err = capsys.readouterr().err
    assert code == 30
    assert "AGENT_ROLE_OUTPUT_REQUIRED" in err
    assert ".workflow/phase-outputs/discovery/input-inventory.yaml" in err
    packet = root / ".workflow/role-packets/discovery/OUTPUT-CONTRACT.yaml"
    assert packet.is_file()


def test_discover_valid_role_output_transitions(tmp_path: Path):
    root = tmp_path / "project"
    root.mkdir()
    initialize_project(root, profile="web-saas")
    out = root / ".workflow/phase-outputs/discovery"
    out.mkdir(parents=True)
    (out / "input-inventory.yaml").write_text(yaml.safe_dump({"items": []}))
    (out / "requirements.yaml").write_text(yaml.safe_dump({"requirements": []}))
    (out / "conflicts.yaml").write_text(yaml.safe_dump({"conflicts": []}))
    assert main(["discover", "--project", str(root)]) == 0
    assert StateStore(ProjectFS(root)).load().current == "INTAKE_COMPLETE"


def test_discover_runs_declared_reference_validator_before_transition(tmp_path: Path, capsys):
    root = tmp_path / "project"
    root.mkdir()
    initialize_project(root, profile="web-saas")
    authority_dir = root / "docs/agent-spec"
    authority_dir.mkdir(parents=True)
    (authority_dir / "AUTHORITY-MATRIX.yaml").write_text(
        yaml.safe_dump(
            {
                "subjects": {
                    "product_behavior": {
                        "mode": "single",
                        "primary": ["docs/core/MISSING-PRODUCT-SPEC.md"],
                    }
                }
            },
            sort_keys=False,
        ),
        encoding="utf-8",
    )
    out = root / ".workflow/phase-outputs/discovery"
    out.mkdir(parents=True)
    (out / "input-inventory.yaml").write_text(yaml.safe_dump({"items": []}))
    (out / "requirements.yaml").write_text(yaml.safe_dump({"requirements": []}))
    (out / "conflicts.yaml").write_text(yaml.safe_dump({"conflicts": []}))

    code = main(["discover", "--project", str(root)])
    err = capsys.readouterr().err

    assert code == 10
    assert "PHASE_VALIDATION_FAILED" in err
    assert "REF_MISSING_PATH" in err
    assert StateStore(ProjectFS(root)).load().current == "RAW_INPUT"
