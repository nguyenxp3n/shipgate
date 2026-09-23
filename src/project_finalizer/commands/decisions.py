from __future__ import annotations

import argparse
from pathlib import Path

import yaml

from project_finalizer.decisions import DecisionStore
from project_finalizer.errors import ExitCode, WorkflowError
from project_finalizer.io import ProjectFS


def _store(args: argparse.Namespace) -> DecisionStore:
    return DecisionStore(ProjectFS(Path(args.project).resolve()))


def handle_list(args: argparse.Namespace) -> ExitCode:
    store = _store(args)
    for decision_id in store.list():
        raw = store.show(decision_id)
        print(f"{decision_id}\t{raw['status']}\t{raw['subject']}")
    return ExitCode.PASS


def handle_show(args: argparse.Namespace) -> ExitCode:
    print(yaml.safe_dump(_store(args).show(args.decision_id), sort_keys=False), end="")
    return ExitCode.PASS


def handle_resolve(args: argparse.Namespace) -> ExitCode:
    store = _store(args)
    if args.choice is not None:
        store.resolve_choice(args.decision_id, args.choice)
    elif args.text is not None:
        store.resolve_text(args.decision_id, args.text)
    else:
        raise WorkflowError(
            "decision resolution requires --choice or --text",
            exit_code=ExitCode.HUMAN_DECISION_REQUIRED,
            code="DECISION_RESOLUTION_REQUIRED",
        )
    print(f"Resolved: {args.decision_id}")
    return ExitCode.PASS
