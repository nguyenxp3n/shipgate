from project_finalizer.readiness import ReadinessInputs, evaluate_build_readiness


def test_pending_protected_decision_fails_build_readiness() -> None:
    report = evaluate_build_readiness(ReadinessInputs(pending_protected_decisions=("DR-004",)))
    assert report.verdict == "FAIL"
    assert "READINESS_PROTECTED_DECISION" in report.blocker_codes


def test_stale_artifact_fails_build_readiness() -> None:
    report = evaluate_build_readiness(ReadinessInputs(stale_required_artifacts=("OPENAPI",)))
    assert "READINESS_STALE_ARTIFACT" in report.blocker_codes


def test_missing_wp000_fails_build_readiness() -> None:
    report = evaluate_build_readiness(ReadinessInputs(wp_entrypoint_exists=False))
    assert "READINESS_WP_ENTRYPOINT" in report.blocker_codes


def test_open_high_fails_build_readiness() -> None:
    report = evaluate_build_readiness(ReadinessInputs(high_blockers=1))
    assert "READINESS_HIGH_BLOCKER" in report.blocker_codes


def test_all_green_is_build_ready_only() -> None:
    report = evaluate_build_readiness(ReadinessInputs())
    assert report.verdict == "PASS"
    assert report.blocker_codes == ()
    assert "PRODUCTION" not in report.verdict
