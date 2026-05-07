"""Tests for tabdown.summarizer."""

import pytest

from tabdown.parser import Tab, TabSession
from tabdown.summarizer import SummaryOptions, summarize_session, summarize_session_to_file


def make_tab(title: str, url: str, group: str | None = None) -> Tab:
    return Tab(title=title, url=url, group=group)


def make_session(name: str = "My Session") -> TabSession:
    session = TabSession(name=name)
    session.add_tab(make_tab("GitHub", "https://github.com", group="Code"))
    session.add_tab(make_tab("PyPI", "https://pypi.org", group="Code"))
    session.add_tab(make_tab("Reddit", "https://reddit.com"))
    session.add_tab(make_tab("Hacker News", "https://news.ycombinator.com"))
    return session


def test_summary_contains_session_name():
    session = make_session("Work Tabs")
    result = summarize_session(session)
    assert "# Work Tabs" in result


def test_summary_contains_group_header():
    session = make_session()
    result = summarize_session(session)
    assert "## Code" in result


def test_summary_contains_tab_links():
    session = make_session()
    result = summarize_session(session)
    assert "[GitHub](https://github.com)" in result
    assert "[PyPI](https://pypi.org)" in result


def test_summary_ungrouped_section():
    session = make_session()
    result = summarize_session(session)
    assert "## Ungrouped" in result
    assert "[Reddit](https://reddit.com)" in result


def test_summary_hide_ungrouped():
    session = make_session()
    opts = SummaryOptions(include_ungrouped=False)
    result = summarize_session(session, opts)
    assert "Ungrouped" not in result
    assert "Reddit" not in result


def test_summary_truncates_tabs():
    session = TabSession(name="Big")
    for i in range(10):
        session.add_tab(make_tab(f"Tab {i}", f"https://example.com/{i}", group="All"))
    opts = SummaryOptions(max_tabs_per_group=3)
    result = summarize_session(session, opts)
    assert "…and 7 more" in result


def test_summary_no_truncation_when_under_limit():
    session = make_session()
    opts = SummaryOptions(max_tabs_per_group=10)
    result = summarize_session(session, opts)
    assert "more" not in result


def test_summary_includes_stats_by_default():
    session = make_session()
    result = summarize_session(session)
    # Stats lines are prefixed with '>'
    assert any(line.startswith(">") for line in result.splitlines())


def test_summary_excludes_stats_when_disabled():
    session = make_session()
    opts = SummaryOptions(include_stats=False)
    result = summarize_session(session, opts)
    assert ">" not in result


def test_summary_custom_header_prefix():
    session = make_session()
    opts = SummaryOptions(header_prefix="###")
    result = summarize_session(session, opts)
    assert "### Code" in result


def test_summarize_to_file(tmp_path):
    session = make_session("Saved Session")
    out = tmp_path / "summary.md"
    summarize_session_to_file(session, str(out))
    content = out.read_text(encoding="utf-8")
    assert "# Saved Session" in content
    assert "[GitHub](https://github.com)" in content
