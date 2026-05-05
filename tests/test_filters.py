"""Tests for tabdown.filters module."""

import pytest

from tabdown.filters import FilterOptions, filter_session, filter_tab
from tabdown.parser import Tab, TabSession


def make_tab(title: str, url: str, group: str | None = None) -> Tab:
    return Tab(title=title, url=url, group=group)


def make_session(*tabs: Tab) -> TabSession:
    session = TabSession(name="Test Session")
    for tab in tabs:
        session.add_tab(tab)
    return session


def test_no_filters_keeps_all_tabs():
    session = make_session(
        make_tab("Google", "https://google.com"),
        make_tab("GitHub", "https://github.com", group="Dev"),
    )
    result = filter_session(session, FilterOptions())
    assert len(result.tabs) == 2


def test_exclude_groups():
    session = make_session(
        make_tab("Google", "https://google.com"),
        make_tab("GitHub", "https://github.com", group="Dev"),
        make_tab("Jira", "https://jira.example.com", group="Work"),
    )
    opts = FilterOptions(exclude_groups=["Dev"])
    result = filter_session(session, opts)
    assert all(t.group != "Dev" for t in result.tabs)
    assert len(result.tabs) == 2


def test_include_groups():
    session = make_session(
        make_tab("Google", "https://google.com"),
        make_tab("GitHub", "https://github.com", group="Dev"),
        make_tab("Jira", "https://jira.example.com", group="Work"),
    )
    opts = FilterOptions(include_groups=["Dev"])
    result = filter_session(session, opts)
    assert len(result.tabs) == 1
    assert result.tabs[0].group == "Dev"


def test_ungrouped_only():
    session = make_session(
        make_tab("Google", "https://google.com"),
        make_tab("GitHub", "https://github.com", group="Dev"),
    )
    opts = FilterOptions(ungrouped_only=True)
    result = filter_session(session, opts)
    assert len(result.tabs) == 1
    assert result.tabs[0].title == "Google"


def test_exclude_domains():
    session = make_session(
        make_tab("Google", "https://google.com"),
        make_tab("Ads", "https://ads.google.com"),
        make_tab("GitHub", "https://github.com"),
    )
    opts = FilterOptions(exclude_domains=["google.com"])
    result = filter_session(session, opts)
    assert len(result.tabs) == 1
    assert result.tabs[0].title == "GitHub"


def test_title_contains():
    session = make_session(
        make_tab("Python Docs", "https://docs.python.org"),
        make_tab("GitHub", "https://github.com"),
        make_tab("Python Package Index", "https://pypi.org"),
    )
    opts = FilterOptions(title_contains="python")
    result = filter_session(session, opts)
    assert len(result.tabs) == 2


def test_session_name_preserved():
    session = TabSession(name="My Tabs")
    session.add_tab(make_tab("Google", "https://google.com"))
    result = filter_session(session, FilterOptions())
    assert result.name == "My Tabs"
