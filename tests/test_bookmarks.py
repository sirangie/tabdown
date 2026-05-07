"""Tests for tabdown.bookmarks bookmark importer."""
from pathlib import Path
import pytest

from tabdown.bookmarks import load_bookmarks, BookmarkError

SAMPLE = Path("tabdown/formats/bookmarks_sample.html")


def test_load_sample_returns_session():
    session = load_bookmarks(SAMPLE)
    assert session.name == "bookmarks_sample"
    all_tabs = list(session.ungrouped_tabs()) + [
        t for tabs in session.groups.values() for t in tabs
    ]
    assert len(all_tabs) == 6


def test_groups_are_detected():
    session = load_bookmarks(SAMPLE)
    assert "Development" in session.groups
    assert "News" in session.groups
    assert len(session.groups["Development"]) == 3
    assert len(session.groups["News"]) == 2


def test_ungrouped_tabs():
    session = load_bookmarks(SAMPLE)
    ungrouped = list(session.ungrouped_tabs())
    assert len(ungrouped) == 1
    assert ungrouped[0].url == "https://example.com"


def test_tab_titles_and_urls():
    session = load_bookmarks(SAMPLE)
    dev_tabs = session.groups["Development"]
    urls = [t.url for t in dev_tabs]
    titles = [t.title for t in dev_tabs]
    assert "https://github.com" in urls
    assert "GitHub" in titles


def test_custom_session_name():
    session = load_bookmarks(SAMPLE, session_name="My Bookmarks")
    assert session.name == "My Bookmarks"


def test_missing_file_raises():
    with pytest.raises(BookmarkError, match="File not found"):
        load_bookmarks("nonexistent_file.html")


def test_invalid_file_raises(tmp_path):
    bad = tmp_path / "bad.html"
    bad.write_text("<html><body><p>Not a bookmark file</p></body></html>")
    with pytest.raises(BookmarkError, match="does not appear"):
        load_bookmarks(bad)


def test_non_http_links_skipped(tmp_path):
    html = """<!DOCTYPE NETSCAPE-Bookmark-file-1>
<DL><p>
  <DT><A HREF="javascript:void(0)">JS Link</A>
  <DT><A HREF="ftp://files.example.com">FTP Link</A>
  <DT><A HREF="https://valid.com">Valid</A>
</DL>"""
    f = tmp_path / "bm.html"
    f.write_text(html)
    session = load_bookmarks(f)
    all_tabs = list(session.ungrouped_tabs())
    assert len(all_tabs) == 1
    assert all_tabs[0].url == "https://valid.com"
