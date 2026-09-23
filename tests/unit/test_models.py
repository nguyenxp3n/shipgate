from project_finalizer.models import ValidationIssue, ValidationReport


def test_validation_report_ok_only_when_empty():
    assert ValidationReport(issues=()).ok is True
    report = ValidationReport(issues=(ValidationIssue(code="X", message="bad", severity="ERROR"),))
    assert report.ok is False
