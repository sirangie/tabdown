"""Tests for tabdown.stats module."""
import pytest
from tabdown.parser import Tab, TabSession
from tabdown.stats import compute_stats, SessionStats, _extract_domain


def make_tab(title: str, url: str, group: str | None = None) -> Tab:
    return Tab(title=title, url=url, group=group)


def make_session(*tabs: Tab) -> TabSession:
    session = TabSession()
    for tab in tabs:
        session.add_tab(tab)
    return session


def test_extract_domain_basic():
    assert _extract_domain("https://www.github.com/user/repo") == "github.com"


def test_extract_domain_no_www():
    assert _extract_domain("https://example.com/page") == "example.com"


def test_extract_domain_with_port():
    assert _extract_domain("http://localhost:8080/path") == "localhost"


def test_extract_domain_invalid():
    assert _extract_domain("not-a-url") == "unknown"


def test_empty_session_stats():
    session = TabSession()
    stats = compute_stats(session)
    assert stats.total_tabs == 0
    assert stats.total_groups == 0
    assert stats.ungrouped_count == 0
    assert stats.tabs_per_group == {}
    assert stats.domain_counts == {}


def test_ungrouped_tabs_counted():
    session = make_session(
        make_tab("A", "https://alpha.com/"),
        make_tab("B", "https://beta.com/"),
    )
    stats = compute_stats(session)
    assert stats.total_tabs == 2
    assert stats.ungrouped_count == 2
    assert stats.total_groups == 0


def test_grouped_tabs_counted():
    session = make_session(
        make_tab("A", "https://alpha.com/", group="Work"),
        make_tab("B", "https://beta.com/", group="Work"),
        make_tab("C", "https://gamma.com/", group="Fun"),
    )
    stats = compute_stats(session)
    assert stats.total_tabs == 3
    assert stats.total_groups == 2
    assert stats.ungrouped_count == 0
    assert stats.tabs_per_group["Work"] == 2
    assert stats.tabs_per_group["Fun"] == 1


def test_domain_counts():
    session = make_session(
        make_tab("A", "https://github.com/a"),
        make_tab("B", "https://github.com/b"),
        make_tab("C", "https://example.com/"),
    )
    stats = compute_stats(session)
    assert stats.domain_counts["github.com"] == 2
    assert stats.domain_counts["example.com"] == 1


def test_top_domains_ordering():
    session = make_session(
        make_tab("1", "https://a.com/"),
        make_tab("2", "https://a.com/page"),
        make_tab("3", "https://a.com/other"),
        make_tab("4", "https://b.com/"),
        make_tab("5", "https://b.com/x"),
        make_tab("6", "https://c.com/"),
    )
    stats = compute_stats(session, top_n=2)
    assert stats.top_domains[0] == ("a.com", 3)
    assert stats.top_domains[1] == ("b.com", 2)
    assert len(stats.top_domains) == 2


def test_summary_lines_contains_key_info():
    session = make_session(
        make_tab("A", "https://example.com/", group="G1"),
        make_tab("B", "https://example.com/b"),
    )
    stats = compute_stats(session)
    summary = str(stats)
    assert "Total tabs" in summary
    assert "G1" in summary
    assert "example.com" in summary
