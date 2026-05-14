"""Tests for CSV export CLI commands."""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from tabdown.csv_cli import cmd_csv_export


def make_chrome_file(tmp_path: Path) -> Path:
    data = {
        "browser": "chrome",
        "created": "2024-01-01T00:00:00",
        "tabs": [
            {"title": "GitHub", "url": "https://github.com", "group": "Dev", "pinned": False},
            {"title": "YouTube", "url": "https://youtube.com", "group": "Media", "pinned": False},
        ],
    }
    p = tmp_path / "session.json"
    p.write_text(json.dumps(data), encoding="utf-8")
    return p


class FakeArgs:
    def __init__(self, **kwargs):
        self.format = None
        self.no_group = False
        self.no_pinned = False
        self.no_notes = False
        self.delimiter = ","
        self.output = ""
        for k, v in kwargs.items():
            setattr(self, k, v)


def test_csv_export_prints_to_stdout(tmp_path, capsys):
    inp = make_chrome_file(tmp_path)
    args = FakeArgs(input=str(inp))
    cmd_csv_export(args)
    captured = capsys.readouterr()
    assert "GitHub" in captured.out
    assert "YouTube" in captured.out


def test_csv_export_writes_file(tmp_path, capsys):
    inp = make_chrome_file(tmp_path)
    out = tmp_path / "out.csv"
    args = FakeArgs(input=str(inp), output=str(out))
    cmd_csv_export(args)
    assert out.exists()
    content = out.read_text(encoding="utf-8")
    assert "GitHub" in content
    captured = capsys.readouterr()
    assert "CSV written to" in captured.out


def test_csv_export_no_group_column(tmp_path, capsys):
    inp = make_chrome_file(tmp_path)
    args = FakeArgs(input=str(inp), no_group=True)
    cmd_csv_export(args)
    captured = capsys.readouterr()
    assert "group" not in captured.out


def test_csv_export_semicolon_delimiter(tmp_path, capsys):
    inp = make_chrome_file(tmp_path)
    args = FakeArgs(input=str(inp), delimiter=";")
    cmd_csv_export(args)
    captured = capsys.readouterr()
    assert ";" in captured.out


def test_csv_export_bad_output_exits(tmp_path):
    inp = make_chrome_file(tmp_path)
    bad_out = tmp_path / "ghost" / "out.csv"
    args = FakeArgs(input=str(inp), output=str(bad_out))
    with pytest.raises(SystemExit):
        cmd_csv_export(args)
