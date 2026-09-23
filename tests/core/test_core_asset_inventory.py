from pathlib import Path

REQUIRED = {
    "governance/AGENT-OPERATING-MANUAL.template.md",
    "specification/PRODUCT-SPEC.template.md",
    "specification/TECHNICAL-SPEC.template.md",
    "specification/DOMAIN-MODEL.template.md",
    "specification/DATA-MODEL.template.md",
    "specification/API-SEMANTICS.template.md",
    "specification/SECURITY.template.md",
    "specification/DEPLOYMENT.template.md",
    "specification/OPERATIONS.template.md",
    "specification/OBSERVABILITY.template.md",
    "specification/FAILURE-MODES.template.md",
    "specification/NON-FUNCTIONAL-REQUIREMENTS.template.md",
    "testing/TESTING-STANDARD.md",
    "testing/COVERAGE-POLICY.md",
    "testing/CRITICAL-INVARIANTS.template.yaml",
    "testing/CONTRACT-TEST-MATRIX.template.yaml",
    "testing/SECURITY-TEST-MATRIX.template.yaml",
    "testing/E2E-JOURNEYS.template.yaml",
    "testing/PHASE-AWARE-GATES.md",
}


def test_core_handoff_asset_inventory(repo_root: Path) -> None:
    core = repo_root / "core"
    assert sorted(path for path in REQUIRED if not (core / path).is_file()) == []


def test_operating_manual_contains_required_governance_markers(repo_root: Path) -> None:
    text = (
        (repo_root / "core/governance/AGENT-OPERATING-MANUAL.template.md")
        .read_text(encoding="utf-8")
        .casefold()
    )
    for marker in (
        "level 1",
        "level 2",
        "level 3",
        "protected",
        "decision request",
        "historical audit",
        "command gateway",
        "work package",
        "dependency",
        "build_ready",
        "runtime_verified",
        "production_ready",
    ):
        assert marker in text


def test_generic_core_normative_templates_have_no_web_stack_authority(repo_root: Path) -> None:
    core = repo_root / "core"
    files = (
        list((core / "specification").glob("*"))
        + list((core / "testing").glob("*"))
        + [core / "governance/AGENT-OPERATING-MANUAL.template.md"]
    )
    forbidden = ("react", "postgresql", "same-site cookie", "cors origin")
    combined = "\n".join(
        path.read_text(encoding="utf-8").casefold() for path in files if path.is_file()
    )
    for term in forbidden:
        assert term not in combined
