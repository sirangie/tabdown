"""Tests for tabdown.templater."""
from __future__ import annotations

from pathlib import Path

import pytest

from tabdown.parser import Tab, TabSession
from tabdown.templater import (
    TemplateError,
    TemplateOptions,
    load_template_options,
    render_session_with_template,
    render_tab_with_template,
)


def make_tab(title: str, url: str, group: str | None = None) -> Tab:
    return Tab(title=title, url=url, group=group)


def make_session(name: str = "Test Session") -> TabSession:
    s = TabSession(name=name)
    s.add_tab(make_tab("Google", "https://google.com"))
    s.add_tab(make_tab("GitHub", "https://github.com", group="Dev"))
    s.add_tab(make_tab("PyPI", "https://pypi.org", group="Dev"))
    return s


def test_render_tab_default_template():
    tab = make_tab("Example", "https://example.com")
    opts = TemplateOptions()
    result = render_tab_with_template(tab, opts)
    assert result == "- [Example](https://example.com)"


def test_render_tab_custom_template():
    tab = make_tab("Example", "https://example.com", group="Work")
    opts = TemplateOptions(tab_template="* {title} <{url}> [{group}]")
    result = render_tab_with_template(tab, opts)
    assert result == "* Example <https://example.com> [Work]"


def test_render_session_header():
    session = make_session("My Tabs")
    opts = TemplateOptions()
    result = render_session_with_template(session, opts)
    assert result.startswith("# My Tabs")


def test_render_session_group_header():
    session = make_session()
    opts = TemplateOptions()
    result = render_session_with_template(session, opts)
    assert "### Dev" in result


def test_render_session_contains_tabs():
    session = make_session()
    opts = TemplateOptions()
    result = render_session_with_template(session, opts)
    assert "[Google](https://google.com)" in result
    assert "[GitHub](https://github.com)" in result


def test_render_session_custom_group_header():
    session = make_session()
    opts = TemplateOptions(group_header="## Group: {group}")
    result = render_session_with_template(session, opts)
    assert "## Group: Dev" in result


def test_render_session_include_stats():
    session = make_session()
    opts = TemplateOptions(include_stats=True)
    result = render_session_with_template(session, opts)
    assert "Total tabs: 3" in result


def test_render_session_no_stats_by_default():
    session = make_session()
    opts = TemplateOptions()
    result = render_session_with_template(session, opts)
    assert "Total tabs" not in result


def test_load_template_options_from_file(tmp_path: Path):
    tpl = tmp_path / "custom.tpl"
    tpl.write_text(
        "tab_template = * {title} -> {url}\n"
        "group_header = ## {group}\n"
        "session_header = ## {name}\n"
        "include_stats = true\n",
        encoding="utf-8",
    )
    opts = load_template_options(tpl)
    assert opts.tab_template == "* {title} -> {url}"
    assert opts.group_header == "## {group}"
    assert opts.session_header == "## {name}"
    assert opts.include_stats is True


def test_load_template_options_missing_file(tmp_path: Path):
    with pytest.raises(TemplateError, match="not found"):
        load_template_options(tmp_path / "nonexistent.tpl")


def test_load_template_options_ignores_comments(tmp_path: Path):
    tpl = tmp_path / "commented.tpl"
    tpl.write_text("# this is a comment\ntab_template = - {title}\n", encoding="utf-8")
    opts = load_template_options(tpl)
    assert opts.tab_template == "- {title}"
    assert opts.group_header == "### {group}"  # default unchanged
