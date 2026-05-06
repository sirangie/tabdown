"""Deduplication utilities — remove duplicate tabs from a session."""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import List, Set

from tabdown.parser import Tab, TabSession


class DedupeStrategy(str, Enum):
    EXACT_URL = "exact_url"       # identical URLs
    NORMALIZED_URL = "normalized"  # strip trailing slash & fragment


@dataclass
class DedupeOptions:
    strategy: DedupeStrategy = DedupeStrategy.EXACT_URL
    keep: str = "first"  # "first" or "last"


def _normalize_url(url: str) -> str:
    url = url.rstrip("/")
    if "#" in url:
        url = url[: url.index("#")]
    return url.lower()


def dedupe_tabs(tabs: List[Tab], options: DedupeOptions | None = None) -> List[Tab]:
    """Return a deduplicated list of tabs."""
    if options is None:
        options = DedupeOptions()

    seen: Set[str] = set()
    result: List[Tab] = []

    ordered = tabs if options.keep == "first" else list(reversed(tabs))

    for tab in ordered:
        key = (
            _normalize_url(tab.url)
            if options.strategy == DedupeStrategy.NORMALIZED_URL
            else tab.url.lower()
        )
        if key not in seen:
            seen.add(key)
            result.append(tab)

    if options.keep == "last":
        result.reverse()

    return result


def dedupe_session(
    session: TabSession, options: DedupeOptions | None = None
) -> tuple[TabSession, int]:
    """Return a deduplicated TabSession and the number of removed tabs."""
    original = list(session.tabs.values())
    deduped = dedupe_tabs(original, options)
    removed = len(original) - len(deduped)

    new_session = TabSession(name=session.name)
    for tab in deduped:
        new_session.add_tab(tab)

    return new_session, removed
