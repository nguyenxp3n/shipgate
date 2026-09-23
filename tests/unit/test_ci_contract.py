from pathlib import Path

import yaml


def test_ci_uses_taskfile_gateway_instead_of_duplicate_tool_commands(repo_root: Path) -> None:
    raw = yaml.safe_load((repo_root / ".github/workflows/ci.yml").read_text(encoding="utf-8"))
    jobs = raw["jobs"]
    commands = []
    for job in jobs.values():
        for step in job.get("steps", []):
            if isinstance(step, dict) and isinstance(step.get("run"), str):
                commands.extend(line.strip() for line in step["run"].splitlines() if line.strip())
    required = {
        "task format:check",
        "task lint",
        "task typecheck",
        "task test",
        "task test:fixtures",
        "task test:release",
    }
    assert required <= set(commands)
    assert any(command in {"task release:dry-run", "task release"} for command in commands)
    forbidden = ("pytest ", "mypy ", "ruff ")
    assert not any(command.startswith(forbidden) for command in commands)
