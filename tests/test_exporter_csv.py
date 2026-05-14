"""Tests for CSV export functionality."""
from __future__ import annotations

import csv
import io
from pathlib import Path

import pytest

from tabdown.exporter_csv import (
    CsvExportError,
    CsvExportOptions,
    export_session_to_csv_file,
    export_session_to_csv_string,
)
from tabdown.parser import Tab, TabSession


def make_tab(title: str, url: str, group: str | None = None, pinned: bool = False) -> Tab:
    return Tab(title=title, url=url, group=group, pinned=pinned)


def make_session(name: str = "Test", tabs: list[Tab] | None = None) -> TabSession:
    session = TabSession(name=name)
    for tab in tabs or []:
        session.add_tab(tab)
    return session


def parse_csv(content: str) -> list[dict]:
    reader = csv.DictReader(io.StringIO(content))
    return list(reader)


def test_csv_has_header_row():
    session = make_session(tabs=[make_tab("GitHub", "https://github.com")])
    content = export_session_to_csv_string(session)
    assert "title" in content
    assert "url" in content


def test_csv_contains_tab_data():
    session = make_session(tabs=[
        make_tab("GitHub", "https://github.com", group="Dev"),
    ])
    rows = parse_csv(export_session_to_csv_string(session))
    assert len(rows) == 1
    assert rows[0]["title"] == "GitHub"
    assert rows[0]["url"] == "https://github.com"
    assert rows[0]["group"] == "Dev"


def test_csv_pinned_column():
    session = make_session(tabs=[make_tab("Gmail", "https://mail.google.com", pinned=True)])
    rows = parse_csv(export_session_to_csv_string(session))
    assert rows[0]["pinned"] == "true"


def test_csv_no_group_column():
    session = make_session(tabs=[make_tab("X", "https://x.com")])
    options = CsvExportOptions(include_group=False)
    content = export_session_to_csv_string(session, options)
    rows = parse_csv(content)
    assert "group" not in rows[0]


def test_csv_tab_delimiter():
    session = make_session(tabs=[make_tab("A", "https://a.com"), make_tab("B", "https://b.com")])
    options = CsvExportOptions(delimiter=";")
    content = export_session_to_csv_string(session, options)
    assert ";" in content


def test_csv_empty_session_returns_empty_string():
    session = make_session()
    content = export_session_to_csv_string(session)
    assert content == ""


def test_csv_multiple_tabs_row_count():
    tabs = [make_tab(f"Tab {i}", f"https://example.com/{i}") for i in range(5)]
    session = make_session(tabs=tabs)
    rows = parse_csv(export_session_to_csv_string(session))
    assert len(rows) == 5


def test_csv_write_to_file(tmp_path: Path):
    session = make_session(tabs=[make_tab("GitHub", "https://github.com")])
    out = tmp_path / "tabs.csv"
    export_session_to_csv_file(session, out)
    assert out.exists()
    rows = parse_csv(out.read_text(encoding="utf-8"))
    assert rows[0]["title"] == "GitHub"


def test_csv_write_to_file_error(tmp_path: Path):
    session = make_session(tabs=[make_tab("X", "https://x.com")])
    bad_path = tmp_path / "nonexistent_dir" / "tabs.csv"
    with pytest.raises(CsvExportError):
        export_session_to_csv_file(session, bad_path)


def test_csv_ungrouped_tab_has_empty_group():
    session = make_session(tabs=[make_tab("Solo", "https://solo.com", group=None)])
    rows = parse_csv(export_session_to_csv_string(session))
    assert rows[0]["group"] == ""
