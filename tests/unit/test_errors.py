from project_finalizer.errors import ExitCode


def test_exit_code_contract_is_stable():
    assert ExitCode.PASS == 0
    assert ExitCode.VALIDATION_FAILED == 10
    assert ExitCode.HUMAN_DECISION_REQUIRED == 20
    assert ExitCode.INVALID_PROJECT_STATE == 30
    assert ExitCode.PROFILE_ERROR == 40
    assert ExitCode.STALE_ARTIFACTS == 50
    assert ExitCode.AUDIT_BLOCKERS_REMAIN == 60
    assert ExitCode.BUILD_READINESS_FAILED == 70
    assert ExitCode.RELEASE_INTEGRITY_FAILED == 80
    assert ExitCode.INTERNAL_WORKFLOW_ERROR == 90

from project_finalizer.cli import run_cli
from project_finalizer.errors import WorkflowError


def test_run_cli_maps_workflow_error_to_exit_code(capsys):
    def fail() -> int:
        raise WorkflowError(
            "broken",
            exit_code=ExitCode.VALIDATION_FAILED,
            code="BROKEN",
        )

    assert run_cli(fail) == int(ExitCode.VALIDATION_FAILED)
    assert capsys.readouterr().err.strip() == "ERROR BROKEN: broken"
