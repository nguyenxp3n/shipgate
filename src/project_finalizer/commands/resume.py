from __future__ import annotations

import argparse
from pathlib import Path

from project_finalizer.errors import ExitCode
from project_finalizer.orchestrator import resume_project


def handle_resume(args: argparse.Namespace) -> ExitCode:
    return resume_project(Path(args.project))
