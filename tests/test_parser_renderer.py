"""Tests for the parser and renderer modules."""

import pytest
from tabdown.parser import Tab, TabSession, parse_session
from tabdown.renderer import render_tab, render_session


# --- Tab tests ---

def test_tab_valid():
    tab = Tab(title="GitHub", url="https://github.com")
    assert tab.title == "GitHub"
    assert tab.url == "https://github.com"


def test_tab_invalid_url():
    with pytest.raises(ValueError):
        Tab(title="Bad", url="not-a-url")


def test_tab_with_group():
    tab = Tab(title="Docs", url="https://docs.python.org", group="Python")
    assert tab.group == "Python"


# --- Session tests ---

def test_session_grouping():
    session = TabSession(name="Work")
    session.add_tab(Tab(title="A", url="https://a.com", group="Tools"))
    session.add_tab(Tab(title="B", url="https://b.com"))
    assert len(session.groups["Tools"]) == 1
    assert len(session.ungrouped_tabs) == 1


def test_parse_session_basic():
    data = {
        "name": "My Session",
        "tabs": [
            {"title": "Google", "url": "https://google.com"},
            {"title": "Lobsters", "url": "https://lobste.rs", "group": "Reading"},
        ]
    }
    session = parse_session(data)
    assert session.name == "My Session"
    assert len(session.tabs) == 2
    assert "Reading" in session.groups


def test_parse_session_skips_invalid_urls():
    data = {
        "tabs": [
            {"title": "Bad", "url": "not-valid"},
            {"title": "Good", "url": "https://example.com"},
        ]
    }
    session = parse_session(data)
    assert len(session.tabs) == 1


# --- Renderer tests ---

def test_render_tab():
    tab = Tab(title="Python", url="https://python.org")
    assert render_tab(tab) == "- [Python](https://python.org)"


def test_render_session_no_groups():
    session = TabSession(name="Simple")
    session.add_tab(Tab(title="X", url="https://x.com"))
    md = render_session(session)
    assert "# Simple" in md
    assert "- [X](https://x.com)" in md
    assert "## Other" not in md


def test_render_session_with_groups():
    session = TabSession(name="Research")
    session.add_tab(Tab(title="Paper", url="https://arxiv.org", group="Science"))
    session.add_tab(Tab(title="News", url="https://news.ycombinator.com"))
    md = render_session(session)
    assert "## Science" in md
    assert "## Other" in md
    assert md.endswith("\n")
