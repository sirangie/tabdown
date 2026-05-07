"""Tests for tabdown.tagger."""

import pytest

from tabdown.parser import Tab, TabSession
from tabdown.tagger import TagOptions, suggest_tags, tag_session


def make_tab(
    url: str = "https://example.com",
    title: str = "Example",
    group: str | None = None,
) -> Tab:
    return Tab(url=url, title=title, group=group)


def make_session(tabs: list[Tab], name: str = "Test") -> TabSession:
    s = TabSession(name=name)
    for t in tabs:
        s.add_tab(t)
    return s


def test_github_gets_code_tag():
    tab = make_tab(url="https://github.com/user/repo", title="Some Repo")
    tags = suggest_tags(tab)
    assert "code" in tags


def test_stackoverflow_gets_qa_tag():
    tab = make_tab(url="https://stackoverflow.com/questions/123", title="How to do X")
    tags = suggest_tags(tab)
    assert "qa" in tags


def test_youtube_gets_video_tag():
    tab = make_tab(url="https://www.youtube.com/watch?v=abc", title="Cool Video")
    tags = suggest_tags(tab)
    assert "video" in tags


def test_wikipedia_gets_wiki_tag():
    tab = make_tab(url="https://en.wikipedia.org/wiki/Python", title="Python - Wikipedia")
    tags = suggest_tags(tab)
    assert "wiki" in tags


def test_localhost_gets_local_tag():
    tab = make_tab(url="http://localhost:8080/app", title="Local Dev")
    tags = suggest_tags(tab)
    assert "local" in tags


def test_group_included_as_tag_by_default():
    tab = make_tab(url="https://example.com", title="Page", group="Work Stuff")
    tags = suggest_tags(tab)
    assert "work-stuff" in tags


def test_group_excluded_when_option_disabled():
    tab = make_tab(url="https://example.com", title="Page", group="Work Stuff")
    opts = TagOptions(include_group_as_tag=False)
    tags = suggest_tags(tab, opts)
    assert "work-stuff" not in tags


def test_max_tags_respected():
    # A tab that would match many keywords
    tab = make_tab(
        url="https://github.com",
        title="docs api reference stackoverflow",
        group="research",
    )
    opts = TagOptions(max_tags=2)
    tags = suggest_tags(tab, opts)
    assert len(tags) <= 2


def test_no_match_returns_empty_or_group_only():
    tab = make_tab(url="https://randomsite.xyz", title="Nothing special")
    opts = TagOptions(include_group_as_tag=False)
    tags = suggest_tags(tab, opts)
    assert tags == []


def test_tag_session_returns_url_mapping():
    tabs = [
        make_tab(url="https://github.com/x", title="Repo"),
        make_tab(url="https://youtube.com/watch", title="Vid"),
    ]
    session = make_session(tabs)
    mapping = tag_session(session)
    assert "https://github.com/x" in mapping
    assert "code" in mapping["https://github.com/x"]
    assert "video" in mapping["https://youtube.com/watch"]


def test_tag_session_empty_session():
    session = make_session([])
    mapping = tag_session(session)
    assert mapping == {}
