from pathlib import Path

from project_finalizer.io import ProjectFS
from project_finalizer.runs import RunLedger


def test_completed_run_outputs_become_trusted(tmp_path: Path):
    root = tmp_path / "project"
    root.mkdir()
    fs = ProjectFS(root)
    ledger = RunLedger(fs)
    ledger.start("RUN-001", agent_role="auditor", inputs=())
    (root / "audit.yaml").write_text("ok")
    ledger.record_partial_outputs("RUN-001", ("audit.yaml",))
    ledger.complete("RUN-001", validator_results=("audit-schema:PASS",))
    assert ledger.output_trust("RUN-001") == "TRUSTED_COMPLETE"
    assert ledger.trusted_outputs("RUN-001")[0]["path"] == "audit.yaml"
