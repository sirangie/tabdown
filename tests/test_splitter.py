"""Tests for tabdown.splitter."""
from __future__ import annotations

import pytest

from tabdown.parser import Tab, TabSession
from tabdown.splitter import SplitBy, SplitOptions, SplitResult, split_session


def make_tab(title: str, url: str, group: str | None = None, pinned: bool = False) -> Tab:
    return Tab(title=title, url=url, group=group, pinned=pinned)


def make_session(name: str = "Test", tabs: list[Tab] | None = None) -> TabSession:
    s = TabSession(name=name)
    for t in (tabs or []):
        s.add_tab(t)
    return s


# --- split by group ---

def test_split_by_group_creates_one_session_per_group():
    tabs = [
        make_tab("A", "https://a.com", group="work"),
        make_tab("B", "https://b.com", group="work"),
        make_tab("C", "https://c.com", group="personal"),
    ]
    session = make_session(tabs=tabs)
    result = split_session(session, SplitOptions(by=SplitBy.GROUP))
    assert result.session_count == 2
    names = {s.name for s in result.sessions}
    assert any("work" in n for n in names)
    assert any("personal" in n for n in names)


def test_split_by_group_ungrouped_tabs_go_to_ungrouped_bucket():
    tabs = [
        make_tab("A", "https://a.com", group=None),
        make_tab("B", "https://b.com", group="work"),
    ]
    session = make_session(tabs=tabs)
    result = split_session(session, SplitOptions(by=SplitBy.GROUP))
    names = {s.name for s in result.sessions}
    assert any("ungrouped" in n for n in names)


def test_split_by_group_total_tabs_preserved():
    tabs = [make_tab(f"T{i}", f"https://t{i}.com", group="g") for i in range(5)]
    session = make_session(tabs=tabs)
    result = split_session(session, SplitOptions(by=SplitBy.GROUP))
    assert result.total_tabs == 5


# --- split by domain ---

def test_split_by_domain_groups_same_domain():
    tabs = [
        make_tab("G1", "https://github.com/a"),
        make_tab("G2", "https://github.com/b"),
        make_tab("SO", "https://stackoverflow.com/q/1"),
    ]
    session = make_session(tabs=tabs)
    result = split_session(session, SplitOptions(by=SplitBy.DOMAIN))
    assert result.session_count == 2
    assert result.total_tabs == 3


def test_split_by_domain_uses_prefix():
    tabs = [make_tab("X", "https://example.com")]
    session = make_session(name="MySess", tabs=tabs)
    result = split_session(session, SplitOptions(by=SplitBy.DOMAIN, name_prefix="Prefix"))
    assert all(s.name.startswith("Prefix") for s in result.sessions)


# --- split by count ---

def test_split_by_count_chunks_correctly():
    tabs = [make_tab(f"T{i}", f"https://t{i}.com") for i in range(25)]
    session = make_session(tabs=tabs)
    result = split_session(session, SplitOptions(by=SplitBy.COUNT, chunk_size=10))
    assert result.session_count == 3
    assert len(result.sessions[0].tabs) == 10
    assert len(result.sessions[1].tabs) == 10
    assert len(result.sessions[2].tabs) == 5


def test_split_by_count_chunk_size_1():
    tabs = [make_tab(f"T{i}", f"https://t{i}.com") for i in range(3)]
    session = make_session(tabs=tabs)
    result = split_session(session, SplitOptions(by=SplitBy.COUNT, chunk_size=1))
    assert result.session_count == 3


def test_split_empty_session_returns_no_sessions():
    session = make_session(tabs=[])
    result = split_session(session, SplitOptions(by=SplitBy.COUNT, chunk_size=5))
    assert result.session_count == 0
    assert result.total_tabs == 0


def test_split_result_session_count_and_total_tabs():
    tabs = [make_tab(f"T{i}", f"https://t{i}.com", group="g") for i in range(4)]
    session = make_session(tabs=tabs)
    result = split_session(session)
    assert isinstance(result, SplitResult)
    assert result.total_tabs == 4
