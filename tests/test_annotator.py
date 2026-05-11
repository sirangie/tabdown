"""Tests for tabdown.annotator."""

from __future__ import annotations

import pytest

from tabdown.annotator import AnnotationOptions, annotate_session, annotate_tab
from tabdown.parser import Tab, TabSession


def make_tab(url: str, title: str = "Tab", group: str | None = None, meta: dict | None = None) -> Tab:
    return Tab(url=url, title=title, group=group, metadata=meta or {})


def make_session(tabs: list[Tab], name: str = "Test Session") -> TabSession:
    s = TabSession(name=name)
    for t in tabs:
        s.add_tab(t)
    return s


# --- annotate_tab ---

def test_annotate_tab_sets_note():
    tab = make_tab("https://example.com")
    result = annotate_tab(tab, "my note")
    assert result.metadata["annotation"] == "my note"


def test_annotate_tab_with_prefix():
    tab = make_tab("https://example.com")
    opts = AnnotationOptions(prefix="NOTE: ")
    result = annotate_tab(tab, "check this", opts)
    assert result.metadata["annotation"] == "NOTE: check this"


def test_annotate_tab_overwrite_true():
    tab = make_tab("https://example.com", meta={"annotation": "old"})
    opts = AnnotationOptions(overwrite=True)
    result = annotate_tab(tab, "new", opts)
    assert result.metadata["annotation"] == "new"


def test_annotate_tab_overwrite_false_skips():
    tab = make_tab("https://example.com", meta={"annotation": "keep"})
    opts = AnnotationOptions(overwrite=False)
    result = annotate_tab(tab, "ignored", opts)
    assert result.metadata["annotation"] == "keep"


def test_annotate_tab_preserves_other_metadata():
    tab = make_tab("https://example.com", meta={"tags": ["code"]})
    result = annotate_tab(tab, "note")
    assert result.metadata["tags"] == ["code"]
    assert result.metadata["annotation"] == "note"


def test_annotate_tab_does_not_mutate_original():
    tab = make_tab("https://example.com")
    annotate_tab(tab, "note")
    assert "annotation" not in (tab.metadata or {})


# --- annotate_session ---

def test_annotate_session_applies_matching_urls():
    tabs = [make_tab("https://a.com"), make_tab("https://b.com")]
    session = make_session(tabs)
    result = annotate_session(session, {"https://a.com": "hello"})
    annotated_urls = [t.url for t in result.annotated]
    assert "https://a.com" in annotated_urls
    assert result.annotated_count == 1


def test_annotate_session_skips_non_matching():
    tabs = [make_tab("https://a.com"), make_tab("https://b.com")]
    session = make_session(tabs)
    result = annotate_session(session, {"https://a.com": "hello"})
    assert result.skipped_count == 1
    assert result.skipped[0].url == "https://b.com"


def test_annotate_session_empty_annotations():
    tabs = [make_tab("https://a.com")]
    session = make_session(tabs)
    result = annotate_session(session, {})
    assert result.annotated_count == 0
    assert result.skipped_count == 1


def test_annotate_session_preserves_session_name():
    session = make_session([], name="My Session")
    result = annotate_session(session, {})
    assert result.session.name == "My Session"


def test_annotate_session_all_tabs_annotated():
    tabs = [make_tab("https://a.com"), make_tab("https://b.com")]
    session = make_session(tabs)
    anns = {"https://a.com": "note a", "https://b.com": "note b"}
    result = annotate_session(session, anns)
    assert result.annotated_count == 2
    assert result.skipped_count == 0
