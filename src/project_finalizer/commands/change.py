from __future__ import annotations

import argparse
from pathlib import Path

from project_finalizer.artifacts import ArtifactGraph
from project_finalizer.changes import ChangeStore
from project_finalizer.errors import ExitCode
from project_finalizer.io import ProjectFS


def _store(args: argparse.Namespace) -> tuple[ProjectFS, ChangeStore]:
    fs = ProjectFS(Path(args.project).resolve())
    return fs, ChangeStore(fs)


def handle_begin(args: argparse.Namespace) -> ExitCode:
    _fs, store = _store(args)
    change_id = args.change_id or store.next_id()
    store.begin(
        change_id,
        reason=args.reason,
        finding=args.finding,
        affected_authorities=tuple(args.authority or ()),
        downstream_artifacts=tuple(args.artifact or ()),
        version_impact=args.version_impact,
    )
    print(change_id)
    return ExitCode.PASS


def handle_validate(args: argparse.Namespace) -> ExitCode:
    _fs, store = _store(args)
    store.validate(args.change_id, validators_green=True)
    print(f"Validated: {args.change_id}")
    return ExitCode.PASS


def handle_close(args: argparse.Namespace) -> ExitCode:
    fs, store = _store(args)
    graph = ArtifactGraph.load(fs)
    hashes: dict[str, str] = {}
    for record in graph.records:
        if fs.resolve(record.path).is_file():
            hashes[record.artifact_id] = fs.sha256(record.path)
    store.close(args.change_id, artifact_graph=graph, current_hashes=hashes)
    print(f"Closed: {args.change_id}")
    return ExitCode.PASS
