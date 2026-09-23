from pathlib import Path

import yaml

REQUIRED = {
    "setup",
    "format",
    "format:check",
    "lint",
    "typecheck",
    "test",
    "test:unit",
    "test:integration",
    "test:fixtures",
    "test:release",
    "qa",
    "release",
}


def test_taskfile_exposes_canonical_gateway(repo_root: Path) -> None:
    raw = yaml.safe_load((repo_root / "Taskfile.yml").read_text(encoding="utf-8"))
    tasks = raw["tasks"]
    assert REQUIRED <= set(tasks)
    qa = tasks["qa"]["cmds"]
    delegated = {item["task"] for item in qa if isinstance(item, dict) and "task" in item}
    assert {"format:check", "lint", "typecheck", "test"} <= delegated
    assert tasks["release"]["cmds"] in (["uv run shipgate release"], ["uv run workflow release"])
