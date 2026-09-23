from project_finalizer.audit import AuditLedger


def finding(fid="CTR-001", severity="CRITICAL"):
    return {
        "id": fid,
        "category": "CONTRADICTION",
        "severity": severity,
        "status": "OPEN",
        "affected_artifacts": ["a.md"],
        "evidence": ["a conflicts with b"],
        "risk": "wrong implementation",
        "recommendation": "resolve contradiction",
    }


def disposition(fid="CTR-001", kind="FIXED"):
    return {
        "finding_id": fid,
        "disposition": kind,
        "reason": "resolved",
        "resolution_refs": ["ADR-001"] if kind in {"FIXED", "ALREADY_FIXED"} else [],
        "verification_refs": ["test-001"] if kind in {"FIXED", "ALREADY_FIXED"} else [],
    }


def test_orphan_disposition_blocks_closure() -> None:
    ledger = AuditLedger.from_records(findings=[], dispositions=[disposition(kind="REJECTED")])
    assert "AUDIT_ORPHAN_DISPOSITION" in {i.code for i in ledger.closure_report().issues}


def test_critical_and_high_without_disposition_remain_open() -> None:
    ledger = AuditLedger.from_records(findings=[finding("CTR-001", "CRITICAL"), finding("TEC-002", "HIGH")], dispositions=[])
    codes = {i.code for i in ledger.closure_report().issues}
    assert {"AUDIT_CRITICAL_OPEN", "AUDIT_HIGH_OPEN"} <= codes


def test_deferred_critical_is_terminal_but_still_blocker() -> None:
    ledger = AuditLedger.from_records(findings=[finding()], dispositions=[disposition(kind="DEFERRED")])
    assert "AUDIT_CRITICAL_OPEN" in {i.code for i in ledger.closure_report().issues}


def test_fixed_requires_resolution_and_verification_refs() -> None:
    bad = disposition()
    bad["resolution_refs"] = []
    bad["verification_refs"] = []
    report = AuditLedger.from_records(findings=[finding()], dispositions=[bad]).closure_report()
    assert "AUDIT_DISPOSITION_EVIDENCE_MISSING" in {i.code for i in report.issues}


def test_closed_audit_is_clean() -> None:
    ledger = AuditLedger.from_records(findings=[finding()], dispositions=[disposition()])
    assert ledger.closure_report().ok
