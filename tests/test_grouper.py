"""Tests for tabdown.grouper."""
from __future__ import annotations

import pytest

from tabdown.grouper import GroupBy, GrouperOptions, group_session, _extract_domain
from tabdown.parser import Tab, TabSession


def make_tab(url: str, title: str = "Page", group: str | None = None, pinned: bool = False) -> Tab:
    return Tab(url=url, title=title, group=group, pinned=pinned)


def make_session(name: str = "Test", tabs: list[Tab] | None = None) -> TabSession:
    s = TabSession(name=name)
    for t in (tabs or []):
        s.add_tab(t)
    return s


# --- _extract_domain ---

def test_extract_domain_strips_www():
    assert _extract_domain("https://www.github.com/foo") == "github.com"


def test_extract_domain_keeps_www_when_disabled():
    assert _extract_domain("https://www.github.com/foo", strip_www=False) == "www.github.com"


def test_extract_domain_invalid_url():
    assert _extract_domain("not-a-url") == "unknown"


# --- group_session by domain ---

def test_group_by_domain_basic():
    tabs = [
        make_tab("https://github.com/a", "A"),
        make_tab("https://github.com/b", "B"),
        make_tab("https://stackoverflow.com/q/1", "Q1"),
    ]
    session = make_session(tabs=tabs)
    result = group_session(session, GrouperOptions(by=GroupBy.DOMAIN))
    assert "github.com" in result.group_map
    assert "stackoverflow.com" in result.group_map
    assert len(result.group_map["github.com"]) == 2
    assert len(result.group_map["stackoverflow.com"]) == 1


def test_group_by_domain_group_count():
    tabs = [
        make_tab("https://news.ycombinator.com/", "HN"),
        make_tab("https://reddit.com/r/python", "Reddit"),
        make_tab("https://reddit.com/r/vim", "Vim"),
    ]
    session = make_session(tabs=tabs)
    result = group_session(session, GrouperOptions(by=GroupBy.DOMAIN))
    assert result.group_count == 2


# --- group_session by keyword ---

def test_group_by_keyword_matches_title():
    tabs = [
        make_tab("https://example.com/1", "Python tutorial"),
        make_tab("https://example.com/2", "JavaScript guide"),
        make_tab("https://example.com/3", "Python advanced"),
    ]
    session = make_session(tabs=tabs)
    opts = GrouperOptions(by=GroupBy.KEYWORD, keywords=["python", "javascript"])
    result = group_session(session, opts)
    assert len(result.group_map["python"]) == 2
    assert len(result.group_map["javascript"]) == 1


def test_group_by_keyword_fallback_group():
    tabs = [
        make_tab("https://example.com/1", "Some random page"),
    ]
    session = make_session(tabs=tabs)
    opts = GrouperOptions(by=GroupBy.KEYWORD, keywords=["python"], fallback_group="Misc")
    result = group_session(session, opts)
    assert "Misc" in result.group_map


def test_group_by_keyword_matches_url():
    tabs = [
        make_tab("https://github.com/python/cpython", "cpython"),
    ]
    session = make_session(tabs=tabs)
    opts = GrouperOptions(by=GroupBy.KEYWORD, keywords=["github"])
    result = group_session(session, opts)
    assert "github" in result.group_map


# --- group_session by existing ---

def test_group_by_existing_preserves_groups():
    tabs = [
        make_tab("https://a.com", group="Work"),
        make_tab("https://b.com", group="Personal"),
    ]
    session = make_session(tabs=tabs)
    result = group_session(session, GrouperOptions(by=GroupBy.EXISTING))
    groups = result.session.groups
    assert "Work" in groups
    assert "Personal" in groups


# --- session name preserved ---

def test_group_session_preserves_name():
    session = make_session(name="My Session")
    result = group_session(session)
    assert result.session.name == "My Session"
