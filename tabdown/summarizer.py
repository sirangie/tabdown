"""Generate plain-text or markdown summaries of a TabSession."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

from tabdown.parser import TabSession
from tabdown.stats import compute_stats


@dataclass
class SummaryOptions:
    max_tabs_per_group: int = 5
    include_stats: bool = True
    include_ungrouped: bool = True
    header_prefix: str = "##"


def _truncate(items: list, limit: int) -> tuple[list, int]:
    """Return (truncated_list, omitted_count)."""
    if len(items) <= limit:
        return items, 0
    return items[:limit], len(items) - limit


def summarize_session(session: TabSession, options: Optional[SummaryOptions] = None) -> str:
    """Return a markdown summary string for *session*."""
    if options is None:
        options = SummaryOptions()

    lines: list[str] = []
    prefix = options.header_prefix

    lines.append(f"# {session.name}")
    lines.append("")

    if options.include_stats:
        stats = compute_stats(session)
        for stat_line in stats.summary_lines():
            lines.append(f"> {stat_line}")
        lines.append("")

    # Grouped tabs
    for group_name, tabs in session.groups.items():
        lines.append(f"{prefix} {group_name}")
        visible, omitted = _truncate(tabs, options.max_tabs_per_group)
        for tab in visible:
            lines.append(f"- [{tab.title}]({tab.url})")
        if omitted:
            lines.append(f"- *…and {omitted} more*")
        lines.append("")

    # Ungrouped tabs
    if options.include_ungrouped and session.ungrouped_tabs:
        lines.append(f"{prefix} Ungrouped")
        visible, omitted = _truncate(session.ungrouped_tabs, options.max_tabs_per_group)
        for tab in visible:
            lines.append(f"- [{tab.title}]({tab.url})")
        if omitted:
            lines.append(f"- *…and {omitted} more*")
        lines.append("")

    return "\n".join(lines).rstrip() + "\n"


def summarize_session_to_file(session: TabSession, path: str, options: Optional[SummaryOptions] = None) -> None:
    """Write the markdown summary of *session* to *path*."""
    content = summarize_session(session, options)
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(content)
