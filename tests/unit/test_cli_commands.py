from pathlib import Path

from project_finalizer.cli import build_parser, main

PUBLIC_COMMANDS = {
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
}


def test_parser_exposes_every_public_command():
    parser = build_parser()
    subparsers_action = next(
        action for action in parser._actions if action.__class__.__name__ == "_SubParsersAction"
    )
    assert PUBLIC_COMMANDS == set(subparsers_action.choices)


def test_phase_without_initialized_project_never_returns_success(capsys):
    code = main(["discover", "--project", "."])
    assert code != 0
    assert "PROJECT_STATE_MISSING" in capsys.readouterr().err


def test_status_without_state_reports_raw_input(tmp_path: Path, capsys):
    code = main(["status", "--project", str(tmp_path)])
    captured = capsys.readouterr()
    assert code == 0
    assert "RAW_INPUT" in captured.out
    assert "workflow init" in captured.out
