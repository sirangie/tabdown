"""Export tab sessions from various browser formats (JSON exports)."""

import json
from pathlib import Path
from typing import Union

from tabdown.parser import Tab, TabSession


class ExportError(Exception):
    """Raised when a browser export file cannot be parsed."""


def _parse_chrome_tabs(data: dict) -> TabSession:
    """Parse a Chrome/Chromium session export dict into a TabSession."""
    session = TabSession(name=data.get("name", "Chrome Session"))
    for window in data.get("windows", []):
        for tab_data in window.get("tabs", []):
            entry = tab_data.get("entries", [{}])[-1]
            url = entry.get("url", "")
            title = entry.get("title", tab_data.get("title", ""))
            group = tab_data.get("groupTitle") or tab_data.get("group")
            if url:
                session.add_tab(Tab(url=url, title=title, group=group))
    return session


def _parse_firefox_tabs(data: dict) -> TabSession:
    """Parse a Firefox session export dict into a TabSession."""
    session = TabSession(name=data.get("name", "Firefox Session"))
    for window in data.get("windows", []):
        for tab_data in window.get("tabs", []):
            entries = tab_data.get("entries", [])
            if not entries:
                continue
            entry = entries[-1]
            url = entry.get("url", "")
            title = entry.get("title", "")
            if url:
                session.add_tab(Tab(url=url, title=title))
    return session


def load_session_from_file(path: Union[str, Path], browser: str = "auto") -> TabSession:
    """Load a TabSession from a browser JSON export file.

    Args:
        path: Path to the JSON export file.
        browser: One of 'chrome', 'firefox', or 'auto' (detect by structure).

    Returns:
        A populated TabSession instance.
    """
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"Export file not found: {path}")

    with open(path, "r", encoding="utf-8") as f:
        try:
            data = json.load(f)
        except json.JSONDecodeError as e:
            raise ExportError(f"Invalid JSON in export file: {e}") from e

    if browser == "auto":
        if "windows" in data and any(
            "entries" in t
            for w in data.get("windows", [])
            for t in w.get("tabs", [])
        ):
            browser = "firefox" if "selectedWindow" in data else "chrome"
        else:
            raise ExportError("Cannot auto-detect browser format.")

    if browser == "chrome":
        return _parse_chrome_tabs(data)
    elif browser == "firefox":
        return _parse_firefox_tabs(data)
    else:
        raise ExportError(f"Unsupported browser format: {browser}")
