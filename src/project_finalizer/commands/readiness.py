from __future__ import annotations

import argparse
from pathlib import Path

from project_finalizer.artifacts import ArtifactGraph
from project_finalizer.audit import AuditLedger
from project_finalizer.decisions import DecisionStore
from project_finalizer.errors import ExitCode
from project_finalizer.io import ProjectFS
from project_finalizer.readiness import ReadinessInputs, evaluate_build_readiness
from project_finalizer.state import StateStore


def _audit_records(fs: ProjectFS, name: str) -> list[dict]:
    path = f"docs/audits/{name}.yaml"
    target = fs.resolve(path)
    if not target.is_file():
        return []
    raw = fs.read_yaml(path)
    if isinstance(raw, list):
        return [dict(item) for item in raw if isinstance(item, dict)]
    if isinstance(raw, dict) and isinstance(raw.get(name), list):
        return [dict(item) for item in raw[name] if isinstance(item, dict)]
    return []


def _stale(fs: ProjectFS) -> tuple[str, ...]:
    graph = ArtifactGraph.load(fs)
    hashes: dict[str, str] = {}
    for record in graph.records:
        if fs.resolve(record.path).is_file():
            hashes[record.artifact_id] = fs.sha256(record.path)
    return graph.stale_artifacts(hashes)


def _has_wp000(root: Path) -> bool:
    directory = root / "docs/agent-spec/work-packages"
    return any((directory / name).is_file() for name in ("WP-000.yaml", "WP-000.yml", "WP-000.md"))


def collect_readiness_inputs(root: Path) -> ReadinessInputs:
    fs = ProjectFS(root)
    state_store = StateStore(fs)
    current = state_store.load().current if state_store.exists() else "RAW_INPUT"
    audit = AuditLedger.from_records(
        findings=_audit_records(fs, "findings"),
        dispositions=_audit_records(fs, "dispositions"),
    ).closure_report()
    return ReadinessInputs(
        documentation_complete=current in {"CORRECTIVE_COMPLETE", "BUILD_READY", "FINAL_RELEASE"},
        wp_entrypoint_exists=_has_wp000(root),
        stale_required_artifacts=_stale(fs),
        pending_protected_decisions=DecisionStore(fs).list_pending(),
        critical_blockers=sum(issue.code == "AUDIT_CRITICAL_OPEN" for issue in audit.issues),
        high_blockers=sum(issue.code == "AUDIT_HIGH_OPEN" for issue in audit.issues),
    )


def handle_readiness(args: argparse.Namespace) -> int:
    root = Path(args.project).resolve()
    fs = ProjectFS(root)
    report = evaluate_build_readiness(collect_readiness_inputs(root))
    print(f"Build readiness: {report.verdict}")
    for code in report.blocker_codes:
        print(f"  {code}")
    if report.verdict != "PASS":
        return int(ExitCode.BUILD_READINESS_FAILED)
    fs.write_yaml_atomic(".workflow/readiness-report.yaml", report.to_mapping())
    return int(ExitCode.PASS)
