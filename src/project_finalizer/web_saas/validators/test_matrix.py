from __future__ import annotations

import re

from project_finalizer.models import ValidationReport
from project_finalizer.web_saas.validators._common import issue, mapping


def _wp_rank(value: str) -> int:
    match = re.fullmatch(r"WP-(\d+)", value)
    return int(match.group(1)) if match else -1


class TestMatrixValidator:
    name = "web-saas-test-matrix"
    layer = "security"

    def validate(self, ctx) -> ValidationReport:
        matrix = mapping(ctx, "test_matrix")
        invariants = matrix.get("invariants", [])
        available = {str(value) for value in matrix.get("available", [])}
        reached = max(
            (
                _wp_rank(str(wp.get("id", "")))
                for wp in getattr(ctx, "work_packages", ())
                if isinstance(wp, dict)
                and str(wp.get("state", "")).upper() in {"READY", "COMPLETE", "COMPLETED"}
            ),
            default=-1,
        )
        issues = []
        for invariant in invariants:
            if not isinstance(invariant, dict):
                continue
            active = _wp_rank(str(invariant.get("active_from_wp", "")))
            if active < 0 or reached < active:
                continue
            for required in invariant.get("required_tests", []):
                if str(required) not in available:
                    issues.append(
                        issue(
                            "WS_TEST_REQUIRED_CLASS_MISSING",
                            f"active invariant requires test class: {required}",
                            subject_id=str(invariant.get("id", "")),
                        )
                    )
        return ValidationReport(tuple(issues))
