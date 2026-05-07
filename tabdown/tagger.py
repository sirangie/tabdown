"""Automatic tag suggestion for tabs based on URL and title heuristics."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Sequence
from urllib.parse import urlparse

from tabdown.parser import Tab, TabSession

# Keyword → tag mappings checked against title and domain
_KEYWORD_TAGS: list[tuple[list[str], str]] = [
    (["github", "gitlab", "bitbucket"], "code"),
    (["stackoverflow", "stackexchange"], "qa"),
    (["docs", "documentation", "api", "reference"], "docs"),
    (["youtube", "vimeo", "twitch"], "video"),
    (["twitter", "x.com", "reddit", "linkedin", "mastodon"], "social"),
    (["arxiv", "scholar", "pubmed", "researchgate"], "research"),
    (["medium", "substack", "dev.to", "hashnode", "blog"], "article"),
    (["wikipedia"], "wiki"),
    (["news", "bbc", "cnn", "reuters", "theguardian"], "news"),
    (["figma", "dribbble", "behance", "canva"], "design"),
    (["localhost", "127.0.0.1", "0.0.0.0"], "local"),
]


@dataclass
class TagOptions:
    max_tags: int = 5
    include_group_as_tag: bool = True
    lowercase: bool = True


def suggest_tags(tab: Tab, options: TagOptions | None = None) -> list[str]:
    """Return a list of suggested tags for a single tab."""
    if options is None:
        options = TagOptions()

    tags: set[str] = set()

    try:
        parsed = urlparse(tab.url)
        domain = (parsed.netloc or "").lower().removeprefix("www.")
    except Exception:
        domain = ""

    title_lower = tab.title.lower() if tab.title else ""
    haystack = f"{domain} {title_lower}"

    for keywords, tag in _KEYWORD_TAGS:
        if any(kw in haystack for kw in keywords):
            tags.add(tag)

    if options.include_group_as_tag and tab.group:
        group_tag = tab.group.strip().lower().replace(" ", "-")
        if group_tag:
            tags.add(group_tag)

    result = sorted(tags)[: options.max_tags]
    if not options.lowercase:
        result = [t.upper() for t in result]
    return result


def tag_session(
    session: TabSession,
    options: TagOptions | None = None,
) -> dict[str, list[str]]:
    """Return a mapping of tab URL → suggested tags for every tab in the session."""
    return {tab.url: suggest_tags(tab, options) for tab in session.tabs}
