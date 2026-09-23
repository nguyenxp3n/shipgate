from __future__ import annotations

import argparse
from pathlib import Path

from project_finalizer.errors import ExitCode
from project_finalizer.project import initialize_project


def handle_init(args: argparse.Namespace) -> ExitCode:
    root = Path(args.root).resolve()
    metadata = initialize_project(root, profile=args.profile)
    project = metadata["project"]
    print(f"Initialized: {project['name']} ({project['profile']}@{project['profile_version']})")
    return ExitCode.PASS
