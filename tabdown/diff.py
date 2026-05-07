"""Session diffing — compare two tab sessions and report what changed."""

from dataclasses import dataclass, field
from typing import List, Set, Tuple

from tabdown.parser import Tab, TabSession


@dataclass
class SessionDiff:
    """Result of comparing two tab sessions."""

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

    def summary_lines(self) -> List[str]:
        """Return a human-readable summary of the diff."""
        lines = [
            f"Added:     {self.added_count}",
            f"Removed:   {self.removed_count}",
            f"Unchanged: {self.unchanged_count}",
        ]
        if self.added:
            lines.append("\nNew tabs:")
            for tab in self.added:
                lines.append(f"  + [{tab.title}]({tab.url})")
        if self.removed:
            lines.append("\nRemoved tabs:")
            for tab in self.removed:
                lines.append(f"  - [{tab.title}]({tab.url})")
        return lines

    def __str__(self) -> str:
        return "\n".join(self.summary_lines())


def _url_set(session: TabSession) -> Set[str]:
    """Collect all URLs from a session into a set."""
    urls: Set[str] = set()
    for tab in session.ungrouped_tabs:
        urls.add(tab.url)
    for tabs in session.groups.values():
        for tab in tabs:
            urls.add(tab.url)
    return urls


def _all_tabs(session: TabSession) -> List[Tab]:
    """Flatten all tabs from a session into a single list."""
    tabs: List[Tab] = list(session.ungrouped_tabs)
    for group_tabs in session.groups.values():
        tabs.extend(group_tabs)
    return tabs


def diff_sessions(old: TabSession, new: TabSession) -> SessionDiff:
    """Compare two sessions and return a SessionDiff describing the changes.

    Comparison is URL-based — a tab is considered the same if its URL appears
    in both sessions, regardless of title or group membership.

    Args:
        old: The baseline session (e.g. a saved snapshot).
        new: The current / updated session.

    Returns:
        A SessionDiff with added, removed, and unchanged tab lists.
    """
    old_urls = _url_set(old)
    new_urls = _url_set(new)

    added_urls = new_urls - old_urls
    removed_urls = old_urls - new_urls
    common_urls = old_urls & new_urls

    # Build result lists preserving Tab objects from the relevant session
    added: List[Tab] = [t for t in _all_tabs(new) if t.url in added_urls]
    removed: List[Tab] = [t for t in _all_tabs(old) if t.url in removed_urls]
    unchanged: List[Tab] = [t for t in _all_tabs(new) if t.url in common_urls]

    return SessionDiff(added=added, removed=removed, unchanged=unchanged)
