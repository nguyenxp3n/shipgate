from pathlib import Path

from project_finalizer.agents.packets import build_role_packet


def test_wp_compiler_packet_excludes_historical_audits_by_default(tmp_path: Path) -> None:
    project = tmp_path / "project"
    (project / "docs/core").mkdir(parents=True)
    (project / "docs/core/PRODUCT-SPEC.md").write_text("canonical\n", encoding="utf-8")
    (project / "docs/agent-spec").mkdir(parents=True)
    (project / "docs/agent-spec/SPEC-MANIFEST.yaml").write_text("version: 1\n", encoding="utf-8")
    (project / "docs/audits/historical").mkdir(parents=True)
    (project / "docs/audits/historical/old.md").write_text("old finding\n", encoding="utf-8")
    packet = build_role_packet(project, "wp-compiler")
    assert "docs/core/PRODUCT-SPEC.md" in packet.input_paths
    assert "docs/audits/historical/old.md" not in packet.input_paths
    assert any(path.endswith("OUTPUT-CONTRACT.md") for path in packet.contract_paths)
