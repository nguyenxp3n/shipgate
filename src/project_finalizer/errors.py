from __future__ import annotations

from enum import IntEnum


class ExitCode(IntEnum):
    PASS = 0
    VALIDATION_FAILED = 10
    HUMAN_DECISION_REQUIRED = 20
    INVALID_PROJECT_STATE = 30
    PROFILE_ERROR = 40
    STALE_ARTIFACTS = 50
    AUDIT_BLOCKERS_REMAIN = 60
    BUILD_READINESS_FAILED = 70
    RELEASE_INTEGRITY_FAILED = 80
    INTERNAL_WORKFLOW_ERROR = 90


class WorkflowError(Exception):
    def __init__(self, message: str, *, exit_code: ExitCode, code: str) -> None:
        super().__init__(message)
        self.exit_code = exit_code
        self.code = code
