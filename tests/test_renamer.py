"""Tests for tabdown.renamer."""
from __future__ import annotations

import pytest

from tabdown.parser import Tab, TabSession
from tabdown.renamer import (
    RenameOptions,
    RenameResult,
    RenameRule,
    rename_session,
    rename_tab,
)


def make_tab(title: str, url: str = "https://example.com", group: str | None = None) -> Tab:
    return Tab(url=url, title=title, group=group)


def make_session(*tabs: Tab, name: str = "Test") -> TabSession:
    s = TabSession(name=name)
    for t in tabs:
        s.add_tab(t)
    return s


# --- RenameRule ---

def test_rename_rule_matches_title():
    rule = RenameRule(pattern=r"GitHub", replacement="GH")
    tab = make_tab("GitHub - Home")
    assert rule.matches(tab)


def test_rename_rule_no_match():
    rule = RenameRule(pattern=r"GitHub", replacement="GH")
    tab = make_tab("Stack Overflow")
    assert not rule.matches(tab)


def test_rename_rule_applies_substitution():
    rule = RenameRule(pattern=r"GitHub", replacement="GH")
    tab = make_tab("GitHub - Explore")
    new_tab, changed = rename_tab(tab, RenameOptions(rules=[rule]))
    assert new_tab.title == "GH - Explore"
    assert changed


def test_rename_rule_group_field():
    rule = RenameRule(pattern=r"work", replacement="Work", field="group")
    tab = make_tab("Jira", group="work stuff")
    new_tab, changed = rename_tab(tab, RenameOptions(rules=[rule]))
    assert new_tab.group == "Work stuff"
    assert changed


def test_rename_rule_url_field_does_not_rename_title():
    rule = RenameRule(pattern=r"github", replacement="gh", field="url")
    tab = make_tab("GitHub", url="https://github.com")
    # url field rename doesn't mutate title, just returns same tab
    new_tab, changed = rename_tab(tab, RenameOptions(rules=[rule]))
    assert new_tab.title == "GitHub"  # title unchanged
    assert changed  # rule matched


# --- rename_tab ---

def test_rename_tab_stop_on_first_match():
    rules = [
        RenameRule(pattern=r"Python", replacement="Py"),
        RenameRule(pattern=r"Py", replacement="NOPE"),
    ]
    tab = make_tab("Python Docs")
    new_tab, _ = rename_tab(tab, RenameOptions(rules=rules, stop_on_first_match=True))
    assert new_tab.title == "Py Docs"


def test_rename_tab_apply_all():
    rules = [
        RenameRule(pattern=r"Python", replacement="Py"),
        RenameRule(pattern=r"Py Docs", replacement="Py Documentation"),
    ]
    tab = make_tab("Python Docs")
    new_tab, _ = rename_tab(tab, RenameOptions(rules=rules, stop_on_first_match=False))
    assert new_tab.title == "Py Documentation"


# --- rename_session ---

def test_rename_session_counts_renamed():
    tabs = [
        make_tab("GitHub Issues"),
        make_tab("GitHub PRs"),
        make_tab("Stack Overflow"),
    ]
    session = make_session(*tabs)
    rule = RenameRule(pattern=r"GitHub", replacement="GH")
    result = rename_session(session, RenameOptions(rules=[rule]))
    assert result.renamed_count == 2


def test_rename_session_preserves_unmatched_tabs():
    tabs = [make_tab("Stack Overflow"), make_tab("Reddit")]
    session = make_session(*tabs)
    rule = RenameRule(pattern=r"GitHub", replacement="GH")
    result = rename_session(session, RenameOptions(rules=[rule]))
    assert result.renamed_count == 0
    titles = [t.title for t in result.session.tabs]
    assert titles == ["Stack Overflow", "Reddit"]


def test_rename_session_preserves_name():
    session = make_session(make_tab("Test"), name="My Session")
    rule = RenameRule(pattern=r"Test", replacement="Demo")
    result = rename_session(session, RenameOptions(rules=[rule]))
    assert result.session.name == "My Session"
