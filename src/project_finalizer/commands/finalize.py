from __future__ import annotations

import argparse
from pathlib import Path

from project_finalizer.errors import ExitCode
from project_finalizer.orchestrator import finalize_project


def handle_finalize(args: argparse.Namespace) -> ExitCode:
    return finalize_project(Path(args.project))
