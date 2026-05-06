"""Tests for tabdown.deduplicator."""
import pytest

from tabdown.parser import Tab, TabSession
from tabdown.deduplicator import (
    DedupeOptions,
    DedupeStrategy,
    dedupe_session,
    dedupe_tabs,
)


def make_tab(url: str, title: str = "Page") -> Tab:
    return Tab(title=title, url=url)


def make_session(*tabs: Tab) -> TabSession:
    s = TabSession(name="test")
    for t in tabs:
        s.add_tab(t)
    return s


def test_no_duplicates_unchanged():
    tabs = [make_tab("https://a.com"), make_tab("https://b.com")]
    result = dedupe_tabs(tabs)
    assert len(result) == 2


def test_exact_url_deduplication():
    tabs = [
        make_tab("https://a.com"),
        make_tab("https://a.com"),
        make_tab("https://b.com"),
    ]
    result = dedupe_tabs(tabs)
    assert len(result) == 2
    assert result[0].url == "https://a.com"
    assert result[1].url == "https://b.com"


def test_keep_last():
    tabs = [
        make_tab("https://a.com", "First"),
        make_tab("https://a.com", "Last"),
    ]
    opts = DedupeOptions(keep="last")
    result = dedupe_tabs(tabs, opts)
    assert len(result) == 1
    assert result[0].title == "Last"


def test_normalized_url_strips_trailing_slash():
    tabs = [
        make_tab("https://a.com/"),
        make_tab("https://a.com"),
    ]
    opts = DedupeOptions(strategy=DedupeStrategy.NORMALIZED_URL)
    result = dedupe_tabs(tabs, opts)
    assert len(result) == 1


def test_normalized_url_strips_fragment():
    tabs = [
        make_tab("https://a.com/page#section1"),
        make_tab("https://a.com/page#section2"),
    ]
    opts = DedupeOptions(strategy=DedupeStrategy.NORMALIZED_URL)
    result = dedupe_tabs(tabs, opts)
    assert len(result) == 1


def test_dedupe_session_returns_count():
    t1 = make_tab("https://dup.com")
    t2 = make_tab("https://dup.com")
    t3 = make_tab("https://unique.com")
    session = make_session(t1, t2, t3)
    new_session, removed = dedupe_session(session)
    assert removed == 1
    assert len(new_session.tabs) == 2


def test_dedupe_session_preserves_original():
    t1 = make_tab("https://dup.com")
    t2 = make_tab("https://dup.com")
    session = make_session(t1, t2)
    _, _ = dedupe_session(session)
    assert len(session.tabs) == 2  # original untouched
