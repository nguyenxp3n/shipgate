from project_finalizer.qa import render_assurance_summary


def test_assurance_report_discloses_unverified_runtime_and_review_truthfully() -> None:
    text = render_assurance_summary(independent_audit=False, self_review=True)
    assert "Static specification validation: PASS" in text
    assert "Autonomous coding-agent handoff: PASS" in text
    assert "Runtime implementation validation: NOT PERFORMED" in text
    assert "Production validation: NOT PERFORMED" in text
    assert "Independent audit: NOT PERFORMED" in text
    assert "Self-review: PERFORMED" in text


def test_independent_audit_and_self_review_are_independent_fields() -> None:
    text = render_assurance_summary(independent_audit=True, self_review=False)
    assert "Independent audit: PERFORMED" in text
    assert "Self-review: NOT PERFORMED" in text
