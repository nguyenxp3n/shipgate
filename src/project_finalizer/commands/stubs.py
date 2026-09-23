from __future__ import annotations

import argparse

from project_finalizer.errors import ExitCode, WorkflowError


def not_implemented(args: argparse.Namespace) -> ExitCode:
    del args
    raise WorkflowError(
        "phase command is not implemented in foundation build",
        exit_code=ExitCode.INVALID_PROJECT_STATE,
        code="NOT_IMPLEMENTED",
    )
