"""Filtering utilities for tab sessions."""

from dataclasses import dataclass, field
from typing import Optional
from urllib.parse import urlparse

from tabdown.parser import Tab, TabSession


@dataclass
class FilterOptions:
    """Options for filtering tabs in a session."""
    exclude_groups: list[str] = field(default_factory=list)
    include_groups: list[str] = field(default_factory=list)
    exclude_domains: list[str] = field(default_factory=list)
    title_contains: Optional[str] = None
    ungrouped_only: bool = False


def _extract_domain(url: str) -> str:
    """Extract the domain from a URL."""
    try:
        return urlparse(url).netloc
    except Exception:
        return ""


def filter_tab(tab: Tab, opts: FilterOptions) -> bool:
    """Return True if the tab should be kept given the filter options."""
    # Group inclusion filter
    if opts.include_groups and tab.group not in opts.include_groups:
        return False

    # Group exclusion filter
    if opts.exclude_groups and tab.group in opts.exclude_groups:
        return False

    # Ungrouped-only filter
    if opts.ungrouped_only and tab.group is not None:
        return False

    # Domain exclusion filter
    if opts.exclude_domains:
        domain = _extract_domain(tab.url)
        if any(domain.endswith(d) for d in opts.exclude_domains):
            return False

    # Title substring filter
    if opts.title_contains and opts.title_contains.lower() not in tab.title.lower():
        return False

    return True


def filter_session(session: TabSession, opts: FilterOptions) -> TabSession:
    """Return a new TabSession containing only tabs that pass the filter."""
    filtered = TabSession(name=session.name)
    for tab in session.tabs:
        if filter_tab(tab, opts):
            filtered.add_tab(tab)
    return filtered
