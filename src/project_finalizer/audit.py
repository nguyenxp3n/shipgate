from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from project_finalizer.models import ValidationIssue, ValidationReport

_TERMINAL = {"FIXED", "ALREADY_FIXED", "DEFERRED", "NOT_APPLICABLE", "REJECTED"}
_EVIDENCE_REQUIRED = {"FIXED", "ALREADY_FIXED"}


@dataclass(frozen=True)
class AuditLedger:
    findings: tuple[dict[str, Any], ...]
    dispositions: tuple[dict[str, Any], ...]

    @classmethod
    def from_records(cls, *, findings: list[dict[str, Any]], dispositions: list[dict[str, Any]]) -> "AuditLedger":
        return cls(tuple(dict(item) for item in findings), tuple(dict(item) for item in dispositions))

    def closure_report(self) -> ValidationReport:
        issues: list[ValidationIssue] = []
        finding_ids = [str(item.get("id", "")) for item in self.findings]
        disposition_ids = [str(item.get("finding_id", "")) for item in self.dispositions]
        for duplicate in sorted({fid for fid in finding_ids if finding_ids.count(fid) > 1}):
            issues.append(ValidationIssue("AUDIT_FINDING_DUPLICATE", f"duplicate finding ID: {duplicate}", "ERROR", subject_id=duplicate))
        for duplicate in sorted({fid for fid in disposition_ids if disposition_ids.count(fid) > 1}):
            issues.append(ValidationIssue("AUDIT_DISPOSITION_DUPLICATE", f"multiple dispositions for finding: {duplicate}", "ERROR", subject_id=duplicate))
        finding_map = {str(item.get("id", "")): item for item in self.findings}
        disposition_map = {str(item.get("finding_id", "")): item for item in self.dispositions}
        for fid in sorted(set(disposition_map) - set(finding_map)):
            issues.append(ValidationIssue("AUDIT_ORPHAN_DISPOSITION", f"disposition references unknown finding: {fid}", "ERROR", subject_id=fid))
        for fid in sorted(finding_map):
            finding = finding_map[fid]
            disposition = disposition_map.get(fid)
            severity = str(finding.get("severity", "")).upper()
            if disposition is None:
                issues.append(ValidationIssue("AUDIT_DISPOSITION_MISSING", f"finding has no terminal disposition: {fid}", "ERROR", subject_id=fid))
                if severity == "CRITICAL":
                    issues.append(ValidationIssue("AUDIT_CRITICAL_OPEN", f"Critical finding remains open: {fid}", "ERROR", subject_id=fid))
                elif severity == "HIGH":
                    issues.append(ValidationIssue("AUDIT_HIGH_OPEN", f"High finding remains open: {fid}", "ERROR", subject_id=fid))
                continue
            kind = str(disposition.get("disposition", ""))
            if kind not in _TERMINAL:
                issues.append(ValidationIssue("AUDIT_DISPOSITION_INVALID", f"invalid disposition for {fid}: {kind}", "ERROR", subject_id=fid))
                continue
            if kind in _EVIDENCE_REQUIRED and (not disposition.get("resolution_refs") or not disposition.get("verification_refs")):
                issues.append(ValidationIssue("AUDIT_DISPOSITION_EVIDENCE_MISSING", f"{kind} disposition requires resolution and verification refs", "ERROR", subject_id=fid))
            if kind == "DEFERRED" and severity == "CRITICAL":
                issues.append(ValidationIssue("AUDIT_CRITICAL_OPEN", f"Deferred Critical finding remains a blocker: {fid}", "ERROR", subject_id=fid))
            elif kind == "DEFERRED" and severity == "HIGH":
                issues.append(ValidationIssue("AUDIT_HIGH_OPEN", f"Deferred High finding remains a blocker: {fid}", "ERROR", subject_id=fid))
        return ValidationReport(tuple(sorted(issues, key=lambda issue: (issue.code, issue.subject_id or ""))))
