"""Session statistics and summary reporting."""
from dataclasses import dataclass, field
from collections import Counter
from typing import Dict, List

from tabdown.parser import TabSession


@dataclass
class SessionStats:
    total_tabs: int = 0
    total_groups: int = 0
    ungrouped_count: int = 0
    tabs_per_group: Dict[str, int] = field(default_factory=dict)
    domain_counts: Dict[str, int] = field(default_factory=dict)
    top_domains: List[tuple] = field(default_factory=list)

    def summary_lines(self) -> List[str]:
        lines = [
            f"Total tabs    : {self.total_tabs}",
            f"Groups        : {self.total_groups}",
            f"Ungrouped     : {self.ungrouped_count}",
        ]
        if self.tabs_per_group:
            lines.append("Tabs per group:")
            for group, count in sorted(self.tabs_per_group.items()):
                lines.append(f"  {group}: {count}")
        if self.top_domains:
            lines.append("Top domains:")
            for domain, count in self.top_domains:
                lines.append(f"  {domain}: {count}")
        return lines

    def __str__(self) -> str:
        return "\n".join(self.summary_lines())


def _extract_domain(url: str) -> str:
    """Best-effort domain extraction without external deps."""
    try:
        host = url.split("//", 1)[1].split("/")[0]
        # strip port and leading www.
        host = host.split(":")[0]
        if host.startswith("www."):
            host = host[4:]
        return host
    except (IndexError, AttributeError):
        return "unknown"


def compute_stats(session: TabSession, top_n: int = 5) -> SessionStats:
    """Compute statistics for a TabSession."""
    all_tabs = list(session.ungrouped_tabs)
    for tabs in session.groups.values():
        all_tabs.extend(tabs)

    domain_counter: Counter = Counter()
    for tab in all_tabs:
        domain_counter[_extract_domain(tab.url)] += 1

    tabs_per_group = {group: len(tabs) for group, tabs in session.groups.items()}

    return SessionStats(
        total_tabs=len(all_tabs),
        total_groups=len(session.groups),
        ungrouped_count=len(session.ungrouped_tabs),
        tabs_per_group=tabs_per_group,
        domain_counts=dict(domain_counter),
        top_domains=domain_counter.most_common(top_n),
    )
