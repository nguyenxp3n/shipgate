from __future__ import annotations

import argparse
from pathlib import Path

from project_finalizer.errors import ExitCode
from project_finalizer.io import ProjectFS
from project_finalizer.state import StateStore


def handle_transition(args: argparse.Namespace) -> ExitCode:
    fs = ProjectFS(Path(args.project).resolve())
    store = StateStore(fs)
    state = store.load()
    next_state = store.transition(args.target, state.gates)
    print(f"State: {next_state.current}")
    return ExitCode.PASS
