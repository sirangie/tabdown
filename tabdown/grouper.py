"""Group tabs by domain, keyword, or custom rules."""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional
from urllib.parse import urlparse

from tabdown.parser import Tab, TabSession


class GroupBy(str, Enum):
    DOMAIN = "domain"
    KEYWORD = "keyword"
    EXISTING = "existing"


@dataclass
class GrouperOptions:
    by: GroupBy = GroupBy.DOMAIN
    keywords: List[str] = field(default_factory=list)
    fallback_group: str = "Other"
    strip_www: bool = True


@dataclass
class GrouperResult:
    session: TabSession
    group_map: Dict[str, List[str]]  # group name -> list of urls

    @property
    def group_count(self) -> int:
        return len(self.group_map)


def _extract_domain(url: str, strip_www: bool = True) -> str:
    try:
        host = urlparse(url).hostname or ""
        if strip_www and host.startswith("www."):
            host = host[4:]
        return host or "unknown"
    except Exception:
        return "unknown"


def _group_by_domain(tabs: List[Tab], options: GrouperOptions) -> Dict[str, List[Tab]]:
    groups: Dict[str, List[Tab]] = {}
    for tab in tabs:
        domain = _extract_domain(tab.url, options.strip_www)
        groups.setdefault(domain, []).append(tab)
    return groups


def _group_by_keyword(tabs: List[Tab], options: GrouperOptions) -> Dict[str, List[Tab]]:
    groups: Dict[str, List[Tab]] = {}
    for tab in tabs:
        matched = False
        combined = f"{tab.title} {tab.url}".lower()
        for kw in options.keywords:
            if kw.lower() in combined:
                groups.setdefault(kw, []).append(tab)
                matched = True
                break
        if not matched:
            groups.setdefault(options.fallback_group, []).append(tab)
    return groups


def group_session(session: TabSession, options: Optional[GrouperOptions] = None) -> GrouperResult:
    """Re-group tabs in a session according to GrouperOptions."""
    opts = options or GrouperOptions()

    if opts.by == GroupBy.EXISTING:
        # Keep existing groups, just return as-is
        new_session = TabSession(name=session.name)
        for tab in session.all_tabs:
            new_session.add_tab(tab)
        group_map = {g: [t.url for t in tabs] for g, tabs in new_session.groups.items()}
        return GrouperResult(session=new_session, group_map=group_map)

    all_tabs = session.all_tabs
    if opts.by == GroupBy.DOMAIN:
        raw_groups = _group_by_domain(all_tabs, opts)
    else:
        raw_groups = _group_by_keyword(all_tabs, opts)

    new_session = TabSession(name=session.name)
    group_map: Dict[str, List[str]] = {}
    for group_name, tabs in raw_groups.items():
        for tab in tabs:
            regrouped = Tab(url=tab.url, title=tab.title, group=group_name, pinned=tab.pinned)
            new_session.add_tab(regrouped)
        group_map[group_name] = [t.url for t in tabs]

    return GrouperResult(session=new_session, group_map=group_map)
