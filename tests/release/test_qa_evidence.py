from pathlib import Path

import yaml

from project_finalizer.generators.qa_reports import QAEvidence, generate_qa_reports

EXPECTED_AREAS = {
    "LIFECYCLE",
    "AUTHORITY",
    "PROVENANCE",
    "CONTROLLED_AUTONOMY",
    "MODULE_OWNERSHIP",
    "CROSS_MODULE_CONTRACTS",
    "MACHINE_CONTRACTS",
    "TESTING",
    "WORK_PACKAGES",
    "AUDIT",
    "STALENESS",
    "SECURITY_PROFILE",
    "WEB_SAAS_EXTENSIONS",
    "ADAPTERS",
    "REVIEW_ASSURANCE",
    "RELEASE",
    "EXAMPLE",
    "NEGATIVE_FIXTURES",
    "SELF_HOSTING",
}


QA_REPORTS = {
    "QA-CORE-ARCHITECTURE.md",
    "QA-WEB-SAAS-PROFILE.md",
    "QA-VALIDATORS.md",
    "QA-AGENT-ROLE-CONTRACTS.md",
    "QA-EXAMPLE-PROJECT.md",
    "QA-RELEASE-INTEGRITY.md",
    "QA-BUILD-READINESS.md",
}


def test_acceptance_traceability_covers_every_final_matrix_area(repo_root: Path) -> None:
    traceability = repo_root / "docs/ACCEPTANCE-TRACEABILITY.yaml"
    raw = yaml.safe_load(traceability.read_text(encoding="utf-8"))
    rows = raw["acceptance"]
    assert {row["id"] for row in rows} == EXPECTED_AREAS
    for row in rows:
        assert row["evidence"]
        assert row["report"] in QA_REPORTS


def test_qa_generator_reports_assurance_truthfully(tmp_path: Path, repo_root: Path) -> None:
    traceability = repo_root / "docs/ACCEPTANCE-TRACEABILITY.yaml"
    evidence = QAEvidence(
        area_status={area: "PASS" for area in EXPECTED_AREAS},
        commands=("PYTHONPATH=src python3 -m pytest -q",),
        independent_review=False,
        self_review=True,
        provider_integration=False,
    )

    outputs = generate_qa_reports(tmp_path, traceability=traceability, evidence=evidence)

    assert {path.name for path in outputs} == QA_REPORTS
    readiness = (tmp_path / "QA-BUILD-READINESS.md").read_text(encoding="utf-8")
    assert "Independent senior review: NOT PERFORMED" in readiness
    assert "Self-review: PERFORMED" in readiness
    assert "AI-provider execution integration: NOT PERFORMED" in readiness
    assert "Runtime target-project validation: NOT PERFORMED" in readiness
    assert "Production target-project validation: NOT PERFORMED" in readiness


def test_qa_generator_never_turns_missing_evidence_into_pass(
    tmp_path: Path,
    repo_root: Path,
) -> None:
    evidence = QAEvidence(
        area_status={"LIFECYCLE": "PASS"},
        commands=("example-command",),
        independent_review=False,
        self_review=False,
        provider_integration=False,
    )

    generate_qa_reports(
        tmp_path,
        traceability=repo_root / "docs/ACCEPTANCE-TRACEABILITY.yaml",
        evidence=evidence,
    )

    validation = (tmp_path / "QA-VALIDATORS.md").read_text(encoding="utf-8")
    assert "AUTHORITY: NOT VERIFIED" in validation
    assert "AUTHORITY: PASS" not in validation


def test_qa_generator_records_environment_limitations(tmp_path: Path, repo_root: Path) -> None:
    evidence = QAEvidence(
        area_status={area: "PASS" for area in EXPECTED_AREAS},
        commands=("PYTHONPATH=src python3 -m pytest -q",),
        independent_review=False,
        self_review=False,
        provider_integration=False,
        limitations=(
            "Exact Python 3.12 / official go-task / Ruff / mypy / real openapi-spec-validator integration was not performed in this environment.",
        ),
    )

    generate_qa_reports(
        tmp_path,
        traceability=repo_root / "docs/ACCEPTANCE-TRACEABILITY.yaml",
        evidence=evidence,
    )

    readiness = (tmp_path / "QA-BUILD-READINESS.md").read_text(encoding="utf-8")
    assert "## Environment limitations" in readiness
    assert "real openapi-spec-validator integration was not performed" in readiness
