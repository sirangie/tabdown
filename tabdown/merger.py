"""Merge multiple TabSessions into one, with optional deduplication."""

from dataclasses import dataclass, field
from typing import List, Optional

from tabdown.parser import Tab, TabSession
from tabdown.deduplicator import DedupeOptions, dedupe_session


@dataclass
class MergeOptions:
    """Options controlling how sessions are merged."""
    dedupe: bool = True
    dedupe_options: DedupeOptions = field(default_factory=DedupeOptions)
    combined_name: Optional[str] = None
    preserve_groups: bool = True


@dataclass
class MergeResult:
    session: TabSession
    source_count: int
    original_tab_count: int
    final_tab_count: int

    @property
    def removed_count(self) -> int:
        return self.original_tab_count - self.final_tab_count


def _prefix_group(tab: Tab, prefix: str) -> Tab:
    """Return a copy of tab with group name prefixed to avoid collisions."""
    if tab.group is None:
        return tab
    return Tab(
        url=tab.url,
        title=tab.title,
        group=f"{prefix}/{tab.group}",
    )


def merge_sessions(
    sessions: List[TabSession],
    options: Optional[MergeOptions] = None,
) -> MergeResult:
    """Merge a list of TabSessions into a single TabSession.

    Args:
        sessions: Non-empty list of sessions to merge.
        options: Merge behaviour configuration.

    Returns:
        A MergeResult containing the merged session and bookkeeping info.

    Raises:
        ValueError: If sessions list is empty.
    """
    if not sessions:
        raise ValueError("Cannot merge an empty list of sessions.")

    opts = options or MergeOptions()
    name = opts.combined_name or " + ".join(s.name for s in sessions if s.name)
    merged = TabSession(name=name or "Merged Session")

    original_count = 0
    for session in sessions:
        all_tabs = list(session.tabs.values())
        original_count += len(all_tabs)
        for tab in all_tabs:
            if opts.preserve_groups and len(sessions) > 1 and session.name:
                tab = _prefix_group(tab, session.name)
            merged.add_tab(tab)

    if opts.dedupe:
        merged = dedupe_session(merged, opts.dedupe_options)

    all_final = list(merged.tabs.values())
    return MergeResult(
        session=merged,
        source_count=len(sessions),
        original_tab_count=original_count,
        final_tab_count=len(all_final),
    )
