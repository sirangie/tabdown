"""Tests for tabdown.highlighter."""

from __future__ import annotations

import pytest

from tabdown.highlighter import HighlightOptions, highlight_session, _tab_matches
from tabdown.parser import Tab, TabSession


def make_tab(title: str, url: str, group: str | None = None, pinned: bool = False) -> Tab:
    return Tab(title=title, url=url, group=group, pinned=pinned)


def make_session(*tabs: Tab, name: str = "Test Session") -> TabSession:
    s = TabSession(name=name)
    for t in tabs:
        s.add_tab(t)
    return s


# --- _tab_matches ---

def test_tab_matches_title():
    tab = make_tab("Python Docs", "https://docs.python.org")
    opts = HighlightOptions(keywords=["python"], match_url=False)
    assert _tab_matches(tab, opts)


def test_tab_matches_url():
    tab = make_tab("Docs", "https://docs.python.org")
    opts = HighlightOptions(keywords=["python"], match_title=False)
    assert _tab_matches(tab, opts)


def test_tab_no_match():
    tab = make_tab("GitHub", "https://github.com")
    opts = HighlightOptions(keywords=["python"])
    assert not _tab_matches(tab, opts)


def test_tab_matches_case_insensitive_by_default():
    tab = make_tab("PYTHON Tutorial", "https://example.com")
    opts = HighlightOptions(keywords=["python"])
    assert _tab_matches(tab, opts)


def test_tab_no_match_case_sensitive():
    tab = make_tab("PYTHON Tutorial", "https://example.com")
    opts = HighlightOptions(keywords=["python"], case_sensitive=True)
    assert not _tab_matches(tab, opts)


def test_tab_match_case_sensitive():
    tab = make_tab("Python Tutorial", "https://example.com")
    opts = HighlightOptions(keywords=["Python"], case_sensitive=True)
    assert _tab_matches(tab, opts)


def test_no_keywords_never_matches():
    tab = make_tab("Anything", "https://example.com")
    opts = HighlightOptions(keywords=[])
    assert not _tab_matches(tab, opts)


# --- highlight_session ---

def test_highlight_returns_only_matching_tabs():
    t1 = make_tab("Python Docs", "https://docs.python.org")
    t2 = make_tab("GitHub", "https://github.com")
    t3 = make_tab("PyPI", "https://pypi.org")
    session = make_session(t1, t2, t3)

    opts = HighlightOptions(keywords=["python", "pypi"])
    result = highlight_session(session, opts)

    assert result.match_count == 2
    assert result.total_tabs == 3


def test_highlight_empty_keywords_returns_no_matches():
    t1 = make_tab("Python Docs", "https://docs.python.org")
    session = make_session(t1)

    result = highlight_session(session, HighlightOptions(keywords=[]))
    assert result.match_count == 0
    assert result.total_tabs == 1


def test_highlight_session_name_preserved():
    session = make_session(make_tab("Python", "https://python.org"), name="My Session")
    result = highlight_session(session, HighlightOptions(keywords=["python"]))
    assert result.session.name == "My Session"


def test_highlight_all_match():
    tabs = [make_tab(f"Python {i}", f"https://python.org/{i}") for i in range(5)]
    session = make_session(*tabs)
    result = highlight_session(session, HighlightOptions(keywords=["python"]))
    assert result.match_count == 5


def test_highlight_default_opts_no_matches():
    session = make_session(make_tab("Anything", "https://example.com"))
    result = highlight_session(session)
    assert result.match_count == 0
