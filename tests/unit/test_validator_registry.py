from __future__ import annotations

import json
from pathlib import Path

import pytest

from project_finalizer.cli import main
from project_finalizer.errors import ExitCode
from project_finalizer.models import ValidationIssue, ValidationReport
from project_finalizer.validators import ValidatorRegistry


class ZValidator:
    name = "z"
    layer = "structure"

    def validate(self, ctx: object) -> ValidationReport:
        del ctx
        return ValidationReport(
            (
                ValidationIssue("Z2", "b", "ERROR", path="z.md", subject_id="two"),
                ValidationIssue("Z1", "a", "ERROR", path="z.md", subject_id="one"),
            )
        )


class AValidator:
    name = "a"
    layer = "syntax"

    def validate(self, ctx: object) -> ValidationReport:
        del ctx
        return ValidationReport((ValidationIssue("A1", "a", "ERROR"),))


class BoomValidator:
    name = "boom"
    layer = "semantics"

    def validate(self, ctx: object) -> ValidationReport:
        del ctx
        raise RuntimeError("boom")


def test_registry_runs_layers_then_names_then_issue_codes() -> None:
    report = ValidatorRegistry([ZValidator(), AValidator()]).run(object())
    assert [issue.code for issue in report.issues] == ["A1", "Z1", "Z2"]


def test_registry_converts_internal_exception_to_tagged_issue() -> None:
    report = ValidatorRegistry([BoomValidator()]).run(object())
    assert len(report.issues) == 1
    issue = report.issues[0]
    assert issue.code == "INTERNAL_VALIDATOR_ERROR"
    assert issue.subject_id == "boom"
    assert "boom" in issue.message


def test_registry_rejects_unknown_layer() -> None:
    class UnknownValidator:
        name = "unknown"
        layer = "mystery"

        def validate(self, ctx: object) -> ValidationReport:
            del ctx
            return ValidationReport()

    with pytest.raises(ValueError, match="unknown validator layer"):
        ValidatorRegistry([UnknownValidator()])


def test_validate_cli_internal_error_uses_internal_exit_code(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    from project_finalizer.commands import validate as command

    monkeypatch.setattr(command, "build_default_registry", lambda: ValidatorRegistry([BoomValidator()]))
    exit_code = main(["validate", "--project", str(tmp_path)])
    assert exit_code == int(ExitCode.INTERNAL_WORKFLOW_ERROR)


def test_validate_cli_json_preserves_validation_exit_semantics(tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]) -> None:
    from project_finalizer.commands import validate as command

    monkeypatch.setattr(command, "build_default_registry", lambda: ValidatorRegistry([AValidator()]))
    exit_code = main(["validate", "--project", str(tmp_path), "--format", "json"])
    assert exit_code == int(ExitCode.VALIDATION_FAILED)
    payload = json.loads(capsys.readouterr().out)
    assert payload["ok"] is False
    assert payload["issues"][0]["code"] == "A1"
