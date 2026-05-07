"""Tests for tabdown.diff module."""

import pytest
from tabdown.parser import Tab, TabSession
from tabdown.diff import SessionDiff, diff_sessions


def make_tab(title: str, url: str, group: str = None) -> Tab:
    return Tab(title=title, url=url, group=group)


def make_session(name: str, tabs) -> TabSession:
    s = TabSession(name=name)
    for t in tabs:
        s.add_tab(t)
    return s


def test_identical_sessions_no_changes():
    tabs = [make_tab("Google", "https://google.com"), make_tab("GitHub", "https://github.com")]
    old = make_session("old", tabs)
    new = make_session("new", tabs)
    diff = diff_sessions(old, new)
    assert not diff.has_changes
    assert diff.added_count == 0
    assert diff.removed_count == 0
    assert diff.unchanged_count == 2


def test_added_tabs():
    old = make_session("old", [make_tab("Google", "https://google.com")])
    new = make_session("new", [
        make_tab("Google", "https://google.com"),
        make_tab("GitHub", "https://github.com"),
    ])
    diff = diff_sessions(old, new)
    assert diff.has_changes
    assert diff.added_count == 1
    assert diff.added[0].url == "https://github.com"
    assert diff.removed_count == 0


def test_removed_tabs():
    old = make_session("old", [
        make_tab("Google", "https://google.com"),
        make_tab("GitHub", "https://github.com"),
    ])
    new = make_session("new", [make_tab("Google", "https://google.com")])
    diff = diff_sessions(old, new)
    assert diff.has_changes
    assert diff.removed_count == 1
    assert diff.removed[0].url == "https://github.com"
    assert diff.added_count == 0


def test_mixed_changes():
    old = make_session("old", [
        make_tab("Google", "https://google.com"),
        make_tab("Old Site", "https://old.example.com"),
    ])
    new = make_session("new", [
        make_tab("Google", "https://google.com"),
        make_tab("New Site", "https://new.example.com"),
    ])
    diff = diff_sessions(old, new)
    assert diff.has_changes
    assert diff.added_count == 1
    assert diff.removed_count == 1
    assert diff.unchanged_count == 1


def test_empty_sessions():
    old = make_session("old", [])
    new = make_session("new", [])
    diff = diff_sessions(old, new)
    assert not diff.has_changes
    assert diff.summary() == "no changes"


def test_summary_string():
    old = make_session("old", [make_tab("A", "https://a.com")])
    new = make_session("new", [make_tab("B", "https://b.com")])
    diff = diff_sessions(old, new)
    summary = diff.summary()
    assert "+1 added" in summary
    assert "-1 removed" in summary


def test_str_representation():
    old = make_session("old", [make_tab("A", "https://a.com", group="work")])
    new = make_session("new", [make_tab("B", "https://b.com")])
    diff = diff_sessions(old, new)
    text = str(diff)
    assert "SessionDiff" in text
    assert "+" in text
    assert "-" in text
