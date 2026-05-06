"""Sorting utilities for tab sessions."""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import List, Optional
from urllib.parse import urlparse

from tabdown.parser import Tab, TabSession


class SortKey(str, Enum):
    TITLE = "title"
    URL = "url"
    DOMAIN = "domain"
    GROUP = "group"


class SortOrder(str, Enum):
    ASC = "asc"
    DESC = "desc"


@dataclass
class SortOptions:
    key: SortKey = SortKey.TITLE
    order: SortOrder = SortOrder.ASC
    group_first: bool = True  # keep group members together


def _tab_sort_key(tab: Tab, key: SortKey) -> str:
    if key == SortKey.TITLE:
        return (tab.title or "").lower()
    if key == SortKey.URL:
        return tab.url.lower()
    if key == SortKey.DOMAIN:
        parsed = urlparse(tab.url)
        return parsed.netloc.lower()
    if key == SortKey.GROUP:
        return (tab.group or "").lower()
    return ""


def sort_tabs(tabs: List[Tab], options: Optional[SortOptions] = None) -> List[Tab]:
    """Return a sorted copy of the tab list."""
    if options is None:
        options = SortOptions()

    reverse = options.order == SortOrder.DESC

    if options.group_first:
        # Sort within each group, preserving group clusters
        groups: dict[str, List[Tab]] = {}
        for tab in tabs:
            g = tab.group or ""
            groups.setdefault(g, []).append(tab)

        sorted_groups = sorted(
            groups.keys(),
            key=lambda g: g.lower() if g else "\xff",  # ungrouped last
            reverse=reverse,
        )

        result: List[Tab] = []
        for g in sorted_groups:
            result.extend(
                sorted(groups[g], key=lambda t: _tab_sort_key(t, options.key), reverse=reverse)
            )
        return result

    return sorted(tabs, key=lambda t: _tab_sort_key(t, options.key), reverse=reverse)


def sort_session(session: TabSession, options: Optional[SortOptions] = None) -> TabSession:
    """Return a new TabSession with tabs sorted according to options."""
    sorted_tab_list = sort_tabs(list(session.tabs.values()), options)
    new_session = TabSession(name=session.name)
    for tab in sorted_tab_list:
        new_session.add_tab(tab)
    return new_session
