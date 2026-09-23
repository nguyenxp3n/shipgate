from __future__ import annotations


def _status(value: bool) -> str:
    return "PERFORMED" if value else "NOT PERFORMED"


def render_assurance_summary(*, independent_audit: bool, self_review: bool) -> str:
    lines = (
        "Static specification validation: PASS",
        "Autonomous coding-agent handoff: PASS",
        "Runtime implementation validation: NOT PERFORMED",
        "Production validation: NOT PERFORMED",
        f"Independent audit: {_status(independent_audit)}",
        f"Self-review: {_status(self_review)}",
    )
    return "\n".join(lines) + "\n"
