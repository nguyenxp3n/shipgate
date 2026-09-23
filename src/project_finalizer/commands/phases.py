from __future__ import annotations

import argparse
from pathlib import Path

from project_finalizer.errors import ExitCode
from project_finalizer.orchestrator import run_phase


def handle_phase(args: argparse.Namespace) -> ExitCode:
    return run_phase(args.phase_id, Path(args.project))
