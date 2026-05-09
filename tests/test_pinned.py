"""Tests for tabdown.pinned module."""

import pytest

from tabdown.parser import Tab, TabSession
from tabdown.pinned import (
    PinnedOptions,
    PinnedResult,
    extract_pinned,
    pinned_to_session,
    strip_pinned,
)


def make_tab(title: str, url: str, group: str = None, pinned: bool = False) -> Tab:
    return Tab(title=title, url=url, group=group, pinned=pinned)


def make_session(name: str = "Test Session") -> TabSession:
    s = TabSession(name=name)
    s.add_tab(make_tab("GitHub", "https://github.com", pinned=True))
    s.add_tab(make_tab("Docs", "https://docs.python.org", group="Dev", pinned=True))
    s.add_tab(make_tab("Reddit", "https://reddit.com"))
    s.add_tab(make_tab("YouTube", "https://youtube.com"))
    return s


def test_extract_pinned_counts():
    session = make_session()
    result = extract_pinned(session)
    assert result.pinned_count == 2
    assert result.unpinned_count == 2


def test_extract_pinned_correct_tabs():
    session = make_session()
    result = extract_pinned(session)
    urls = [t.url for t in result.pinned]
    assert "https://github.com" in urls
    assert "https://docs.python.org" in urls


def test_extract_unpinned_correct_tabs():
    session = make_session()
    result = extract_pinned(session)
    urls = [t.url for t in result.unpinned]
    assert "https://reddit.com" in urls
    assert "https://youtube.com" in urls


def test_no_pinned_tabs():
    session = TabSession(name="Empty Pins")
    session.add_tab(make_tab("Reddit", "https://reddit.com"))
    result = extract_pinned(session)
    assert result.pinned_count == 0
    assert result.unpinned_count == 1


def test_pinned_to_session_name_default():
    session = make_session("My Session")
    pinned_session = pinned_to_session(session)
    assert pinned_session.name == "My Session (pinned)"


def test_pinned_to_session_name_override():
    session = make_session()
    opts = PinnedOptions(session_name="Bookmarks")
    pinned_session = pinned_to_session(session, opts)
    assert pinned_session.name == "Bookmarks"


def test_pinned_to_session_tab_count():
    session = make_session()
    pinned_session = pinned_to_session(session)
    assert len(pinned_session.tabs) == 2


def test_pinned_to_session_preserves_groups():
    session = make_session()
    pinned_session = pinned_to_session(session)
    groups = [t.group for t in pinned_session.tabs]
    assert "Dev" in groups


def test_pinned_to_session_strips_groups_when_requested():
    session = make_session()
    opts = PinnedOptions(include_groups=False)
    pinned_session = pinned_to_session(session, opts)
    for tab in pinned_session.tabs:
        assert tab.group is None


def test_strip_pinned_removes_pinned():
    session = make_session()
    stripped = strip_pinned(session)
    for tab in stripped.tabs:
        assert not tab.pinned


def test_strip_pinned_preserves_name():
    session = make_session("Keep Name")
    stripped = strip_pinned(session)
    assert stripped.name == "Keep Name"


def test_strip_pinned_count():
    session = make_session()
    stripped = strip_pinned(session)
    assert len(stripped.tabs) == 2
