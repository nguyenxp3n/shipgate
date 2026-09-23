from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path

import yaml

QA_REPORTS = (
    "QA-CORE-ARCHITECTURE.md",
    "QA-WEB-SAAS-PROFILE.md",
    "QA-VALIDATORS.md",
    "QA-AGENT-ROLE-CONTRACTS.md",
    "QA-EXAMPLE-PROJECT.md",
    "QA-RELEASE-INTEGRITY.md",
    "QA-BUILD-READINESS.md",
)


@dataclass(frozen=True)
class QAEvidence:
    area_status: Mapping[str, str]
    commands: tuple[str, ...]
    independent_review: bool
    self_review: bool
    provider_integration: bool
    limitations: tuple[str, ...] = ()


def _performed(value: bool) -> str:
    return "PERFORMED" if value else "NOT PERFORMED"


def _load_traceability(path: Path) -> list[dict[str, object]]:
    raw = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(raw, dict) or not isinstance(raw.get("acceptance"), list):
        raise ValueError(f"invalid acceptance traceability: {path}")
    rows: list[dict[str, object]] = []
    for row in raw["acceptance"]:
        if not isinstance(row, dict):
            raise ValueError(f"invalid acceptance traceability row: {row!r}")
        rows.append(row)
    return rows


def _render_report(
    report_name: str,
    rows: list[dict[str, object]],
    evidence: QAEvidence,
) -> str:
    title = report_name.removesuffix(".md").replace("QA-", "QA — ").replace("-", " ")
    lines = [f"# {title}", "", "Generated from structured release evidence.", ""]
    matching = [row for row in rows if row.get("report") == report_name]
    for row in matching:
        area = str(row["id"])
        status = evidence.area_status.get(area, "NOT VERIFIED")
        lines.append(f"- {area}: {status}")
        refs = row.get("evidence", [])
        if isinstance(refs, list):
            for ref in refs:
                lines.append(f"  - evidence: `{ref}`")
    if evidence.commands:
        lines.extend(["", "## Verification commands", ""])
        for command in evidence.commands:
            lines.append(f"- `{command}`")
    if evidence.limitations and report_name in {"QA-BUILD-READINESS.md", "QA-RELEASE-INTEGRITY.md"}:
        lines.extend(["", "## Environment limitations", ""])
        lines.extend(f"- {item}" for item in evidence.limitations)
    if report_name == "QA-BUILD-READINESS.md":
        lines.extend(
            [
                "",
                "## Assurance disclosure",
                "",
                f"Independent senior review: {_performed(evidence.independent_review)}",
                f"Self-review: {_performed(evidence.self_review)}",
                f"AI-provider execution integration: {_performed(evidence.provider_integration)}",
                "Runtime target-project validation: NOT PERFORMED",
                "Production target-project validation: NOT PERFORMED",
            ]
        )
    return "\n".join(lines).rstrip() + "\n"


def generate_qa_reports(
    output_root: Path,
    *,
    traceability: Path,
    evidence: QAEvidence,
) -> tuple[Path, ...]:
    rows = _load_traceability(traceability)
    output_root.mkdir(parents=True, exist_ok=True)
    outputs: list[Path] = []
    for report_name in QA_REPORTS:
        path = output_root / report_name
        path.write_text(_render_report(report_name, rows, evidence), encoding="utf-8")
        outputs.append(path)
    return tuple(outputs)
