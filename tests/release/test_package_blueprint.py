from pathlib import Path


REQUIRED_ROOT = {
    "START-HERE.md", "README.md", "CHANGELOG.md", "VERSION",
    "AGENTS.md", "CLAUDE.md", "GEMINI.md", "Taskfile.yml", "pyproject.toml",
    "uv.lock", "WORKFLOW-MANIFEST.yaml", "core", "profiles", "adapters",
    "schemas", "prompts", "validators", "generators", "cli", "tests",
    "examples", "docs", "fixtures", "release",
}


def test_release_source_tree_matches_blueprint(repo_root: Path) -> None:
    assert REQUIRED_ROOT <= {p.name for p in repo_root.iterdir()}
    assert (repo_root / "VERSION").read_text(encoding="utf-8").strip() == "2.0.0"
