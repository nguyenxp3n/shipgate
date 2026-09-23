from __future__ import annotations

import argparse
from pathlib import Path

from project_finalizer.errors import ExitCode
from project_finalizer.io import ProjectFS
from project_finalizer.state import ADJACENCY, StateStore

NEXT_COMMAND = {
    "RAW_INPUT": "workflow init",
    "INTAKE_COMPLETE": "workflow normalize",
    "SOURCE_NORMALIZED": "workflow spec",
    "CORE_SPEC_FROZEN": "workflow contracts",
    "MACHINE_CONTRACTS_READY": "workflow agent-spec",
    "AGENT_SPEC_READY": "workflow wp",
    "WORK_PACKAGES_READY": "workflow audit",
    "SENIOR_AUDITED": "workflow correct",
    "CORRECTIVE_COMPLETE": "workflow readiness",
    "BUILD_READY": "workflow release",
    "FINAL_RELEASE": "none",
}


def handle_status(args: argparse.Namespace) -> ExitCode:
    project = Path(args.project).resolve()
    fs = ProjectFS(project)
    store = StateStore(fs)
    current = store.load().current if store.exists() else "RAW_INPUT"
    print(f"Project: {project.name or project}")
    print(f"State: {current}")
    print()
    print("Next:")
    print(f"  {NEXT_COMMAND[current]}")
    return ExitCode.PASS


def allowed_next_for(state: str) -> tuple[str, ...]:
    return ADJACENCY[state]
