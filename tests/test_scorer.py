"""Tests for tabdown.scorer."""
from __future__ import annotations

import pytest

from tabdown.parser import Tab, TabSession
from tabdown.scorer import ScoreOptions, ScoredTab, score_tab, score_session


def make_tab(
    title: str = "Tab",
    url: str = "https://example.com",
    group: str | None = None,
    pinned: bool = False,
) -> Tab:
    t = Tab(title=title, url=url, group=group)
    t.pinned = pinned
    return t


def make_session(tabs, name="Test Session") -> TabSession:
    session = TabSession(name=name)
    for t in tabs:
        session.add_tab(t)
    return session


def test_score_no_keywords_zero():
    tab = make_tab("Python Docs", "https://docs.python.org")
    result = score_tab(tab, ScoreOptions())
    assert result.score == 0.0
    assert result.tab is tab


def test_score_keyword_match_title():
    tab = make_tab("Python Tutorial", "https://example.com")
    opts = ScoreOptions(keywords=["python"], keyword_weight=2.0)
    result = score_tab(tab, opts)
    assert result.score == 2.0


def test_score_keyword_match_url():
    tab = make_tab("Some Page", "https://github.com/python/cpython")
    opts = ScoreOptions(keywords=["python"], keyword_weight=3.0)
    result = score_tab(tab, opts)
    assert result.score == 3.0


def test_score_multiple_keywords():
    tab = make_tab("Python GitHub Repo", "https://github.com/python")
    opts = ScoreOptions(keywords=["python", "github"], keyword_weight=1.0)
    result = score_tab(tab, opts)
    assert result.score == 2.0


def test_score_pinned_bonus():
    tab = make_tab(pinned=True)
    opts = ScoreOptions(boost_pinned=True, pinned_bonus=1.5)
    result = score_tab(tab, opts)
    assert result.score == 1.5


def test_score_pinned_no_boost():
    tab = make_tab(pinned=True)
    opts = ScoreOptions(boost_pinned=False)
    result = score_tab(tab, opts)
    assert result.score == 0.0


def test_score_grouped_bonus():
    tab = make_tab(group="Work")
    opts = ScoreOptions(boost_grouped=True, grouped_bonus=0.5)
    result = score_tab(tab, opts)
    assert result.score == 0.5


def test_score_session_sorted_descending():
    tabs = [
        make_tab("Python Docs", "https://docs.python.org"),
        make_tab("Python GitHub", "https://github.com/python"),
        make_tab("Random Page", "https://random.org"),
    ]
    session = make_session(tabs)
    opts = ScoreOptions(keywords=["python"], keyword_weight=2.0)
    results = score_session(session, opts)
    scores = [r.score for r in results]
    assert scores == sorted(scores, reverse=True)


def test_score_session_includes_grouped_tabs():
    t1 = make_tab("Ungrouped", "https://a.com")
    t2 = make_tab("Grouped", "https://b.com", group="Work")
    session = make_session([t1, t2])
    results = score_session(session, ScoreOptions())
    titles = {r.tab.title for r in results}
    assert "Ungrouped" in titles
    assert "Grouped" in titles


def test_score_session_default_options():
    tabs = [make_tab(f"Tab {i}") for i in range(3)]
    session = make_session(tabs)
    results = score_session(session)
    assert len(results) == 3


def test_scored_tab_ordering():
    a = ScoredTab(tab=make_tab(), score=1.0)
    b = ScoredTab(tab=make_tab(), score=3.0)
    assert a < b
