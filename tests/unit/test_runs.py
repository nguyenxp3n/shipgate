from pathlib import Path

from project_finalizer.io import ProjectFS
from project_finalizer.runs import RunLedger


def test_started_run_outputs_are_untrusted_until_completion(tmp_path: Path):
    root = tmp_path / "project"
    root.mkdir()
    fs = ProjectFS(root)
    ledger = RunLedger(fs)
    ledger.start("RUN-001", agent_role="contract_compiler", inputs=())
    output = root / "out.yaml"
    output.write_text("partial")
    ledger.record_partial_outputs("RUN-001", ("out.yaml",))
    assert ledger.output_trust("RUN-001") == "UNTRUSTED_PARTIAL"
    assert ledger.trusted_outputs("RUN-001") == ()
