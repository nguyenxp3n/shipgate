from pathlib import Path

from project_finalizer.generators.adapters import generate_adapters

BOOTSTRAP = [
    "Agent Operating Manual",
    "Authority Matrix",
    "SPEC-MANIFEST",
    "work-packages/README.md",
    "WP-000",
]


def test_all_adapters_share_exact_canonical_bootstrap_order(tmp_path: Path) -> None:
    generated = generate_adapters(tmp_path, project_name="Demo", version="1.0.0")
    assert {path.name for path in generated} == {"AGENT.md", "AGENTS.md", "CLAUDE.md", "GEMINI.md"}
    for path in generated:
        text = path.read_text(encoding="utf-8")
        positions = [text.index(marker) for marker in BOOTSTRAP]
        assert positions == sorted(positions), path
        assert "docs/audits/historical" not in text
