"""Keyword highlighting for tab sessions — mark tabs matching search terms."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional

from tabdown.parser import Tab, TabSession


@dataclass
class HighlightOptions:
    keywords: List[str] = field(default_factory=list)
    case_sensitive: bool = False
    match_url: bool = True
    match_title: bool = True


@dataclass
class HighlightResult:
    session: TabSession
    matched_tabs: List[Tab] = field(default_factory=list)
    total_tabs: int = 0

    @property
    def match_count(self) -> int:
        return len(self.matched_tabs)


def _tab_matches(tab: Tab, opts: HighlightOptions) -> bool:
    """Return True if any keyword matches the tab's title or URL."""
    if not opts.keywords:
        return False

    keywords = (
        opts.keywords if opts.case_sensitive else [k.lower() for k in opts.keywords]
    )

    candidates: List[str] = []
    if opts.match_title and tab.title:
        candidates.append(tab.title if opts.case_sensitive else tab.title.lower())
    if opts.match_url:
        candidates.append(tab.url if opts.case_sensitive else tab.url.lower())

    return any(kw in candidate for kw in keywords for candidate in candidates)


def highlight_session(
    session: TabSession, opts: Optional[HighlightOptions] = None
) -> HighlightResult:
    """Filter a session down to tabs that match any keyword in opts."""
    if opts is None:
        opts = HighlightOptions()

    all_tabs = list(session.tabs)
    matched: List[Tab] = [tab for tab in all_tabs if _tab_matches(tab, opts)]

    filtered = TabSession(name=session.name)
    for tab in matched:
        filtered.add_tab(tab)

    return HighlightResult(
        session=filtered,
        matched_tabs=matched,
        total_tabs=len(all_tabs),
    )
