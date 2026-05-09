"""Tests for tabdown.pinned_cli module."""

import argparse
import sys
from io import StringIO
from unittest.mock import MagicMock, patch

import pytest

from tabdown.parser import Tab, TabSession
from tabdown.pinned_cli import cmd_pinned_list, cmd_pinned_export, build_pinned_parser


def make_session() -> TabSession:
    s = TabSession(name="CLI Test")
    s.add_tab(Tab(title="GitHub", url="https://github.com", pinned=True))
    s.add_tab(Tab(title="Docs", url="https://docs.python.org", group="Dev", pinned=True))
    s.add_tab(Tab(title="Reddit", url="https://reddit.com"))
    return s


class FakeArgs:
    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)


def test_cmd_pinned_list_prints_pinned(capsys):
    with patch("tabdown.pinned_cli.load_session_from_file", return_value=make_session()):
        args = FakeArgs(input="fake.json")
        cmd_pinned_list(args)
    captured = capsys.readouterr()
    assert "GitHub" in captured.out
    assert "Docs" in captured.out
    assert "Reddit" not in captured.out


def test_cmd_pinned_list_no_pinned(capsys):
    session = TabSession(name="No Pins")
    session.add_tab(Tab(title="Reddit", url="https://reddit.com"))
    with patch("tabdown.pinned_cli.load_session_from_file", return_value=session):
        args = FakeArgs(input="fake.json")
        cmd_pinned_list(args)
    captured = capsys.readouterr()
    assert "No pinned tabs found" in captured.out


def test_cmd_pinned_list_load_error(capsys):
    with patch("tabdown.pinned_cli.load_session_from_file", side_effect=Exception("bad file")):
        args = FakeArgs(input="bad.json")
        with pytest.raises(SystemExit):
            cmd_pinned_list(args)
    captured = capsys.readouterr()
    assert "Error" in captured.err


def test_cmd_pinned_export_stdout(capsys):
    with patch("tabdown.pinned_cli.load_session_from_file", return_value=make_session()):
        args = FakeArgs(input="fake.json", output=None, name=None, no_groups=False)
        cmd_pinned_export(args)
    captured = capsys.readouterr()
    assert "GitHub" in captured.out


def test_cmd_pinned_export_to_file(tmp_path, capsys):
    out_file = str(tmp_path / "pinned.md")
    with patch("tabdown.pinned_cli.load_session_from_file", return_value=make_session()):
        args = FakeArgs(input="fake.json", output=out_file, name=None, no_groups=False)
        cmd_pinned_export(args)
    captured = capsys.readouterr()
    assert "written to" in captured.out
    with open(out_file) as f:
        content = f.read()
    assert "GitHub" in content


def test_cmd_pinned_export_custom_name(capsys):
    with patch("tabdown.pinned_cli.load_session_from_file", return_value=make_session()):
        args = FakeArgs(input="fake.json", output=None, name="My Pins", no_groups=False)
        cmd_pinned_export(args)
    captured = capsys.readouterr()
    assert "My Pins" in captured.out


def test_build_pinned_parser_registers_subcommands():
    parser = argparse.ArgumentParser()
    subs = parser.add_subparsers(dest="cmd")
    build_pinned_parser(subs)
    args = parser.parse_args(["pinned", "list", "fake.json"])
    assert args.input == "fake.json"
