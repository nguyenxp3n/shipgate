from __future__ import annotations

import argparse
import sys
from collections.abc import Callable, Sequence
from pathlib import Path

from project_finalizer.commands.audit_input import handle_audit_input
from project_finalizer.commands.change import handle_begin as change_begin, handle_close as change_close, handle_validate as change_validate
from project_finalizer.commands.decisions import handle_list as decisions_list, handle_resolve as decisions_resolve, handle_show as decisions_show
from project_finalizer.commands.finalize import handle_finalize
from project_finalizer.commands.init import handle_init
from project_finalizer.commands.inspect import handle_inspect
from project_finalizer.commands.phases import handle_phase
from project_finalizer.commands.readiness import handle_readiness
from project_finalizer.commands.release import handle_release
from project_finalizer.commands.resume import handle_resume
from project_finalizer.commands.status import handle_status
from project_finalizer.commands.transition import handle_transition
from project_finalizer.commands.validate import handle_validate
from project_finalizer.commands.stubs import not_implemented
from project_finalizer.errors import ExitCode, WorkflowError

VERSION_TEXT = "shipgate 2.0.0"
PUBLIC_COMMANDS = (
    "init",
    "inspect",
    "discover",
    "normalize",
    "resolve",
    "spec",
    "architecture",
    "contracts",
    "agent-spec",
    "wp",
    "audit",
    "correct",
    "readiness",
    "validate",
    "status",
    "transition",
    "release",
    "resume",
    "decisions",
    "change",
    "audit-input",
    "finalize",
)

Handler = Callable[[argparse.Namespace], int | ExitCode]


def _add_project_argument(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--project", type=Path, default=Path("."))


def _register_leaf(
    subparsers: argparse._SubParsersAction[argparse.ArgumentParser],
    name: str,
    handler: Handler,
) -> argparse.ArgumentParser:
    parser = subparsers.add_parser(name)
    _add_project_argument(parser)
    parser.set_defaults(handler=handler)
    return parser


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="workflow")
    parser.add_argument("--version", action="version", version=VERSION_TEXT)
    subparsers = parser.add_subparsers(dest="command")

    for name in PUBLIC_COMMANDS:
        if name in {"decisions", "change"}:
            parent = subparsers.add_parser(name)
            parent.set_defaults(handler=not_implemented)
            nested = parent.add_subparsers(dest=f"{name}_command")
            nested_names = ("list", "show", "resolve") if name == "decisions" else (
                "begin",
                "validate",
                "close",
            )
            for nested_name in nested_names:
                leaf = nested.add_parser(nested_name)
                _add_project_argument(leaf)
                if name == "decisions":
                    if nested_name == "list":
                        leaf.set_defaults(handler=decisions_list)
                    elif nested_name == "show":
                        leaf.add_argument("decision_id")
                        leaf.set_defaults(handler=decisions_show)
                    else:
                        leaf.add_argument("decision_id")
                        group = leaf.add_mutually_exclusive_group(required=True)
                        group.add_argument("--choice")
                        group.add_argument("--text")
                        leaf.set_defaults(handler=decisions_resolve)
                else:
                    if nested_name == "begin":
                        leaf.add_argument("--change-id")
                        leaf.add_argument("--finding")
                        leaf.add_argument("--reason", default="corrective change")
                        leaf.add_argument("--authority", action="append")
                        leaf.add_argument("--artifact", action="append")
                        leaf.add_argument("--version-impact", choices=("none", "patch", "minor", "major"), default="patch")
                        leaf.set_defaults(handler=change_begin)
                    elif nested_name == "validate":
                        leaf.add_argument("change_id")
                        leaf.set_defaults(handler=change_validate)
                    else:
                        leaf.add_argument("change_id")
                        leaf.set_defaults(handler=change_close)
            continue
        if name == "init":
            command_parser = subparsers.add_parser(name)
            command_parser.add_argument("root")
            command_parser.add_argument("--profile", default="web-saas")
            command_parser.set_defaults(handler=handle_init)
            continue
        phase_commands = {"discover", "normalize", "resolve", "spec", "architecture", "contracts", "agent-spec", "wp", "audit", "correct"}
        if name == "inspect":
            handler = handle_inspect
        elif name == "audit-input":
            handler = handle_audit_input
        elif name == "status":
            handler = handle_status
        elif name == "transition":
            handler = handle_transition
        elif name == "resume":
            handler = handle_resume
        elif name == "finalize":
            handler = handle_finalize
        elif name == "validate":
            handler = handle_validate
        elif name == "readiness":
            handler = handle_readiness
        elif name == "release":
            handler = handle_release
        elif name in phase_commands:
            handler = handle_phase
        else:
            handler = not_implemented
        command_parser = _register_leaf(subparsers, name, handler)
        if name in phase_commands:
            command_parser.set_defaults(phase_id=name)
        if name == "transition":
            command_parser.add_argument("target")
        if name == "audit-input":
            command_parser.add_argument("--dry-run", action="store_true")
        if name == "validate":
            command_parser.add_argument("--format", choices=("human", "json"), default="human")
        if name == "release":
            command_parser.add_argument("--output", type=Path)

    return parser


def run_cli(command: Callable[[], int]) -> int:
    try:
        return command()
    except WorkflowError as exc:
        print(f"ERROR {exc.code}: {exc}", file=sys.stderr)
        return int(exc.exit_code)


def _parse_and_dispatch(argv: Sequence[str] | None) -> int:
    parser = build_parser()
    try:
        args = parser.parse_args(argv)
    except SystemExit as exc:
        return int(exc.code)
    handler = getattr(args, "handler", None)
    if handler is None:
        parser.print_help()
        return int(ExitCode.PASS)
    return int(handler(args))


def main(argv: Sequence[str] | None = None) -> int:
    return run_cli(lambda: _parse_and_dispatch(argv))


def entrypoint() -> None:
    raise SystemExit(main())
