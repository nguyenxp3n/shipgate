from pathlib import Path

import yaml

from project_finalizer.intake import scan_inputs


def test_teamnotes_raw_input_has_multiple_source_classes(repo_root: Path) -> None:
    items = scan_inputs(repo_root / "examples/teamnotes/raw-input")
    assert {item.path for item in items} >= {
        "product-notes.md", "api-notes.md", "data-notes.md",
        "security-notes.md", "operations-notes.md",
    }


def test_teamnotes_normalized_requirements_keep_provenance_and_conflict_resolution(repo_root: Path) -> None:
    base = repo_root / "examples/teamnotes"
    req = yaml.safe_load((base / "expected-normalized/requirements.yaml").read_text(encoding="utf-8"))
    assert all(item["source"]["path"] and item["source"]["location"] for item in req["requirements"])
    conflicts = yaml.safe_load((base / "expected-normalized/conflicts.yaml").read_text(encoding="utf-8"))
    assert conflicts["conflicts"][0]["resolution_ref"] == "DR-TN-001"
    assert (base / "expected-core-spec/decisions/DR-TN-001.yaml").is_file()
