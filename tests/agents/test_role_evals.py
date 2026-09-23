from pathlib import Path

import yaml

from project_finalizer.agents.eval import evaluate_role_output


def _fixture(repo_root: Path, name: str):
    root = repo_root / "fixtures/role-evals" / name
    packet = yaml.safe_load((root / "packet.yaml").read_text(encoding="utf-8"))
    output = yaml.safe_load((root / "output.yaml").read_text(encoding="utf-8"))
    return packet, output


def test_discovery_conflict_cannot_choose_winner_without_decision(repo_root: Path) -> None:
    packet, output = _fixture(repo_root, "discovery-conflict")
    report = evaluate_role_output("discovery", packet, output)
    assert "ROLE_DISCOVERY_CHOSE_WINNER" in {issue.code for issue in report.issues}


def test_senior_auditor_cannot_mutate_canonical_contract(repo_root: Path) -> None:
    packet, output = _fixture(repo_root, "senior-auditor-write-boundary")
    report = evaluate_role_output("senior-auditor", packet, output)
    assert "ROLE_WRITE_BOUNDARY_VIOLATION" in {issue.code for issue in report.issues}


def test_protected_decision_is_escalated(repo_root: Path) -> None:
    packet, output = _fixture(repo_root, "protected-decision")
    report = evaluate_role_output("technical-architect", packet, output)
    assert "ROLE_PROTECTED_DECISION_NOT_ESCALATED" in {issue.code for issue in report.issues}


def test_contract_compiler_cannot_invent_unsupported_endpoint(repo_root: Path) -> None:
    packet, output = _fixture(repo_root, "contract-compiler-invention")
    report = evaluate_role_output("contract-compiler", packet, output)
    assert "ROLE_UNSUPPORTED_ADDITION" in {issue.code for issue in report.issues}


def test_readiness_reviewer_cannot_guess_protected_resolution(repo_root: Path) -> None:
    packet, output = _fixture(repo_root, "readiness-protected-guess")
    report = evaluate_role_output("readiness-reviewer", packet, output)
    assert "ROLE_READINESS_PROTECTED_GUESS" in {issue.code for issue in report.issues}
