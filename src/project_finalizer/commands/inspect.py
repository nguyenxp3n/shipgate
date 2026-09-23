from __future__ import annotations

import argparse
from pathlib import Path

from project_finalizer.artifacts import ArtifactGraph
from project_finalizer.decisions import DecisionStore
from project_finalizer.errors import ExitCode
from project_finalizer.io import ProjectFS
from project_finalizer.phases import phase_for_state
from project_finalizer.project import load_project_metadata
from project_finalizer.state import StateStore


def handle_inspect(args: argparse.Namespace) -> ExitCode:
    root = Path(args.project).resolve()
    fs = ProjectFS(root)
    metadata = load_project_metadata(root)["project"]
    state = StateStore(fs).load()
    pending = DecisionStore(fs).list_pending()
    graph = ArtifactGraph.load(fs)
    current_hashes = {
        record.artifact_id: fs.sha256(record.path)
        for record in graph.records
        if fs.resolve(record.path).is_file()
    }
    stale = graph.stale_artifacts(current_hashes)
    phase = phase_for_state(state.current)
    print(f"Project: {metadata['name']}")
    print(f"Profile: {metadata['profile']}@{metadata['profile_version']}")
    print(f"State: {state.current}")
    print(f"Pending decisions: {len(pending)}")
    print(f"Stale artifacts: {len(stale)}")
    print(f"Next: workflow {phase.phase_id if phase else 'status'}")
    return ExitCode.PASS
