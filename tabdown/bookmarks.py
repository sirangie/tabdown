"""Import browser bookmarks (HTML export) as a TabSession."""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path
from html.parser import HTMLParser
from typing import List, Optional

from tabdown.parser import Tab, TabSession


class BookmarkError(Exception):
    """Raised when a bookmark file cannot be parsed."""


@dataclass
class _BookmarkParser(HTMLParser):
    tabs: List[Tab] = field(default_factory=list)
    _current_group: Optional[str] = field(default=None, repr=False)
    _current_href: Optional[str] = field(default=None, repr=False)
    _reading_title: bool = field(default=False, repr=False)
    _reading_folder: bool = field(default=False, repr=False)

    def handle_starttag(self, tag: str, attrs):
        attr_dict = dict(attrs)
        if tag == "a" and "href" in attr_dict:
            href = attr_dict["href"]
            if href.startswith("http://") or href.startswith("https://"):
                self._current_href = href
                self._reading_title = True
        elif tag == "h3":
            self._reading_folder = True

    def handle_endtag(self, tag: str):
        if tag == "a":
            self._reading_title = False
            self._current_href = None
        elif tag == "h3":
            self._reading_folder = False
        elif tag == "dl":
            self._current_group = None

    def handle_data(self, data: str):
        data = data.strip()
        if not data:
            return
        if self._reading_folder:
            self._current_group = data
            self._reading_folder = False
        elif self._reading_title and self._current_href:
            self.tabs.append(
                Tab(title=data, url=self._current_href, group=self._current_group)
            )
            self._reading_title = False


def load_bookmarks(path: str | Path, session_name: Optional[str] = None) -> TabSession:
    """Parse a Netscape-format HTML bookmarks file into a TabSession."""
    p = Path(path)
    if not p.exists():
        raise BookmarkError(f"File not found: {path}")
    html = p.read_text(encoding="utf-8", errors="replace")
    if "<!DOCTYPE NETSCAPE-Bookmark-file" not in html and "<DL>" not in html.upper():
        raise BookmarkError("File does not appear to be a Netscape bookmark export.")
    parser = _BookmarkParser()
    parser.feed(html)
    name = session_name or p.stem
    session = TabSession(name=name)
    for tab in parser.tabs:
        session.add_tab(tab)
    return session
