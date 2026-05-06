"""Tests for tabdown.merger."""

import pytest

from tabdown.parser import Tab, TabSession
from tabdown.deduplicator import DedupeOptions, DedupeStrategy
from tabdown.merger import MergeOptions, merge_sessions, _prefix_group


def make_tab(url: str, title: str = "Page", group: str = None) -> Tab:
    return Tab(url=url, title=title, group=group)


def make_session(name: str, tabs) -> TabSession:
    s = TabSession(name=name)
    for t in tabs:
        s.add_tab(t)
    return s


def test_merge_two_sessions_combines_tabs():
    s1 = make_session("Work", [make_tab("https://a.com"), make_tab("https://b.com")])
    s2 = make_session("Home", [make_tab("https://c.com")])
    result = merge_sessions([s1, s2], MergeOptions(dedupe=False))
    assert result.final_tab_count == 3
    assert result.source_count == 2


def test_merge_uses_combined_name():
    s1 = make_session("A", [make_tab("https://x.com")])
    s2 = make_session("B", [make_tab("https://y.com")])
    result = merge_sessions([s1, s2], MergeOptions(combined_name="Custom", dedupe=False))
    assert result.session.name == "Custom"


def test_merge_auto_name_from_sessions():
    s1 = make_session("Alpha", [make_tab("https://x.com")])
    s2 = make_session("Beta", [make_tab("https://y.com")])
    result = merge_sessions([s1, s2], MergeOptions(dedupe=False))
    assert "Alpha" in result.session.name
    assert "Beta" in result.session.name


def test_merge_deduplicates_by_default():
    shared_url = "https://shared.com"
    s1 = make_session("S1", [make_tab(shared_url), make_tab("https://a.com")])
    s2 = make_session("S2", [make_tab(shared_url), make_tab("https://b.com")])
    result = merge_sessions([s1, s2])
    assert result.final_tab_count == 3
    assert result.removed_count == 1


def test_merge_dedupe_disabled_keeps_duplicates():
    shared_url = "https://dup.com"
    s1 = make_session("S1", [make_tab(shared_url)])
    s2 = make_session("S2", [make_tab(shared_url)])
    result = merge_sessions([s1, s2], MergeOptions(dedupe=False))
    assert result.final_tab_count == 2
    assert result.removed_count == 0


def test_merge_empty_list_raises():
    with pytest.raises(ValueError, match="empty"):
        merge_sessions([])


def test_merge_single_session_passthrough():
    s = make_session("Solo", [make_tab("https://only.com")])
    result = merge_sessions([s], MergeOptions(dedupe=False))
    assert result.final_tab_count == 1
    assert result.source_count == 1


def test_preserve_groups_prefixes_group_name():
    tab = make_tab("https://x.com", group="Research")
    prefixed = _prefix_group(tab, "Work")
    assert prefixed.group == "Work/Research"
    assert prefixed.url == tab.url


def test_preserve_groups_none_group_unchanged():
    tab = make_tab("https://x.com", group=None)
    result = _prefix_group(tab, "Work")
    assert result.group is None


def test_merge_original_count_tracked():
    s1 = make_session("S1", [make_tab("https://a.com"), make_tab("https://b.com")])
    s2 = make_session("S2", [make_tab("https://c.com")])
    result = merge_sessions([s1, s2], MergeOptions(dedupe=False))
    assert result.original_tab_count == 3
