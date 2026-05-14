"""Split a TabSession into multiple sessions by group, domain, or count."""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import List

from tabdown.parser import Tab, TabSession


class SplitBy(str, Enum):
    GROUP = "group"
    DOMAIN = "domain"
    COUNT = "count"


@dataclass
class SplitOptions:
    by: SplitBy = SplitBy.GROUP
    chunk_size: int = 10  # used when by=COUNT
    name_prefix: str = ""


@dataclass
class SplitResult:
    sessions: List[TabSession] = field(default_factory=list)

    @property
    def session_count(self) -> int:
        return len(self.sessions)

    @property
    def total_tabs(self) -> int:
        return sum(len(s.tabs) for s in self.sessions)


def _extract_domain(url: str) -> str:
    try:
        from urllib.parse import urlparse
        host = urlparse(url).netloc
        return host.lstrip("www.") if host else "unknown"
    except Exception:
        return "unknown"


def split_session(session: TabSession, opts: SplitOptions | None = None) -> SplitResult:
    """Split *session* into multiple sessions according to *opts*."""
    if opts is None:
        opts = SplitOptions()

    prefix = opts.name_prefix or session.name

    if opts.by == SplitBy.GROUP:
        buckets: dict[str, list[Tab]] = {}
        for tab in session.tabs:
            key = tab.group or "ungrouped"
            buckets.setdefault(key, []).append(tab)
        sessions = []
        for group_name, tabs in buckets.items():
            s = TabSession(name=f"{prefix} — {group_name}")
            for t in tabs:
                s.add_tab(t)
            sessions.append(s)
        return SplitResult(sessions=sessions)

    if opts.by == SplitBy.DOMAIN:
        buckets2: dict[str, list[Tab]] = {}
        for tab in session.tabs:
            key = _extract_domain(tab.url)
            buckets2.setdefault(key, []).append(tab)
        sessions2 = []
        for domain, tabs in buckets2.items():
            s = TabSession(name=f"{prefix} — {domain}")
            for t in tabs:
                s.add_tab(t)
            sessions2.append(s)
        return SplitResult(sessions=sessions2)

    # SplitBy.COUNT
    size = max(1, opts.chunk_size)
    chunks = [session.tabs[i:i + size] for i in range(0, len(session.tabs), size)]
    sessions3 = []
    for idx, chunk in enumerate(chunks, start=1):
        s = TabSession(name=f"{prefix} — part {idx}")
        for t in chunk:
            s.add_tab(t)
        sessions3.append(s)
    return SplitResult(sessions=sessions3)
