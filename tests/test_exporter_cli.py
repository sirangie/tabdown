"""Tests for tabdown.exporter_cli."""

from __future__ import annotations

import json
import textwrap
from pathlib import Path
from types import SimpleNamespace

import pytest

from tabdown.exporter_cli import cmd_export


CHROME_DATA = {
    "type": "chrome",
    "name": "Work",
    "tabs": [
        {"title": "GitHub", "url": "https://github.com", "group": None, "pinned": False},
        {"title": "Docs", "url": "https://docs.python.org", "group": "Python", "pinned": False},
    ],
}


@pytest.fixture()
def chrome_file(tmp_path: Path) -> Path:
    p = tmp_path / "session.json"
    p.write_text(json.dumps(CHROME_DATA))
    return p


class FakeArgs(SimpleNamespace):
    format: str | None = None
    output: str | None = None
    summary: bool = False
    max_url_length: int = 80
    no_stats: bool = False


def test_export_prints_markdown(chrome_file: Path, capsys):
    args = FakeArgs(input=str(chrome_file))
    rc = cmd_export(args)
    assert rc == 0
    out = capsys.readouterr().out
    assert "GitHub" in out
    assert "https://github.com" in out


def test_export_to_file(chrome_file: Path, tmp_path: Path):
    out_file = tmp_path / "output.md"
    args = FakeArgs(input=str(chrome_file), output=str(out_file))
    rc = cmd_export(args)
    assert rc == 0
    assert out_file.exists()
    content = out_file.read_text()
    assert "GitHub" in content


def test_export_summary_stdout(chrome_file: Path, capsys):
    args = FakeArgs(input=str(chrome_file), summary=True)
    rc = cmd_export(args)
    assert rc == 0
    out = capsys.readouterr().out
    assert "Work" in out or "GitHub" in out


def test_export_summary_to_file(chrome_file: Path, tmp_path: Path):
    out_file = tmp_path / "summary.md"
    args = FakeArgs(input=str(chrome_file), output=str(out_file), summary=True)
    rc = cmd_export(args)
    assert rc == 0
    assert out_file.exists()


def test_export_missing_file_returns_error(tmp_path: Path, capsys):
    args = FakeArgs(input=str(tmp_path / "nope.json"))
    rc = cmd_export(args)
    assert rc == 1
    err = capsys.readouterr().err
    assert "error" in err.lower()


def test_export_forced_format(chrome_file: Path, capsys):
    args = FakeArgs(input=str(chrome_file), format="chrome")
    rc = cmd_export(args)
    assert rc == 0
    out = capsys.readouterr().out
    assert "GitHub" in out
