"""Diff two tab sessions to find added, removed, and unchanged tabs."""

from dataclasses import dataclass, field
from typing import List, Set
from tabdown.parser import Tab, TabSession


@dataclass
class SessionDiff:
    added: List[Tab] = field(default_factory=list)
    removed: List[Tab] = field(default_factory=list)
    unchanged: List[Tab] = field(default_factory=list)

    @property
    def added_count(self) -> int:
        return len(self.added)

    @property
    def removed_count(self) -> int:
        return len(self.removed)

    @property
    def unchanged_count(self) -> int:
        return len(self.unchanged)

    @property
    def has_changes(self) -> bool:
        return bool(self.added or self.removed)

    def summary(self) -> str:
        parts = []
        if self.added:
            parts.append(f"+{self.added_count} added")
        if self.removed:
            parts.append(f"-{self.removed_count} removed")
        if self.unchanged:
            parts.append(f"{self.unchanged_count} unchanged")
        return ", ".join(parts) if parts else "no changes"

    def __str__(self) -> str:
        lines = [f"SessionDiff: {self.summary()}"]
        for tab in self.added:
            lines.append(f"  + [{tab.group or 'ungrouped'}] {tab.title} <{tab.url}>")
        for tab in self.removed:
            lines.append(f"  - [{tab.group or 'ungrouped'}] {tab.title} <{tab.url}>")
        return "\n".join(lines)


def _url_set(session: TabSession) -> Set[str]:
    return {tab.url for tab in session.tabs}


def diff_sessions(old: TabSession, new: TabSession) -> SessionDiff:
    """Compare two sessions and return a SessionDiff."""
    old_urls = _url_set(old)
    new_urls = _url_set(new)

    added_urls = new_urls - old_urls
    removed_urls = old_urls - new_urls
    unchanged_urls = old_urls & new_urls

    added = [t for t in new.tabs if t.url in added_urls]
    removed = [t for t in old.tabs if t.url in removed_urls]
    unchanged = [t for t in old.tabs if t.url in unchanged_urls]

    return SessionDiff(added=added, removed=removed, unchanged=unchanged)
