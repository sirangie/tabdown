"""Tests for snapshot CLI subcommands."""

import json
from pathlib import Path
from unittest.mock import patch

import pytest

from tabdown.parser import Tab, TabSession
from tabdown.snapshot import save_snapshot
from tabdown.snapshot_cli import (
    cmd_snapshot_delete,
    cmd_snapshot_list,
    cmd_snapshot_restore,
    cmd_snapshot_save,
)


def make_session() -> TabSession:
    s = TabSession(name="CLI Test")
    s.add_tab(Tab(title="Example", url="https://example.com"))
    s.add_tab(Tab(title="Docs", url="https://docs.python.org", group="Python"))
    return s


class FakeArgs:
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)


def test_cmd_snapshot_save(tmp_path):
    session = make_session()
    chrome_file = tmp_path / "tabs.json"
    # write a minimal chrome-format file
    chrome_data = {
        "browser": "chrome",
        "tabs": [
            {"title": "Example", "url": "https://example.com", "group": None}
        ],
    }
    chrome_file.write_text(json.dumps(chrome_data))
    args = FakeArgs(
        input=str(chrome_file),
        name="test_snap",
        format="chrome",
        snapshot_dir=str(tmp_path / "snaps"),
    )
    with patch("tabdown.snapshot_cli.load_session_from_file", return_value=session):
        result = cmd_snapshot_save(args)
    assert result == 0
    snaps = list((tmp_path / "snaps").glob("*.json"))
    assert len(snaps) == 1


def test_cmd_snapshot_save_error(tmp_path):
    args = FakeArgs(
        input="nonexistent.json",
        name="fail",
        format=None,
        snapshot_dir=str(tmp_path),
    )
    result = cmd_snapshot_save(args)
    assert result == 1


def test_cmd_snapshot_list_empty(tmp_path, capsys):
    args = FakeArgs(snapshot_dir=str(tmp_path))
    result = cmd_snapshot_list(args)
    assert result == 0
    captured = capsys.readouterr()
    assert "No snapshots found" in captured.out


def test_cmd_snapshot_list_with_entries(tmp_path, capsys):
    session = make_session()
    save_snapshot(session, "snap_one", snapshot_dir=tmp_path)
    args = FakeArgs(snapshot_dir=str(tmp_path))
    result = cmd_snapshot_list(args)
    assert result == 0
    captured = capsys.readouterr()
    assert "snap_one" in captured.out


def test_cmd_snapshot_restore(tmp_path):
    session = make_session()
    snap_path = save_snapshot(session, "restore_me", snapshot_dir=tmp_path)
    out_file = tmp_path / "out.md"
    args = FakeArgs(snapshot=str(snap_path), output=str(out_file))
    result = cmd_snapshot_restore(args)
    assert result == 0
    assert out_file.exists()
    content = out_file.read_text()
    assert "Example" in content


def test_cmd_snapshot_restore_missing(tmp_path):
    args = FakeArgs(snapshot=str(tmp_path / "ghost.json"), output=str(tmp_path / "out.md"))
    result = cmd_snapshot_restore(args)
    assert result == 1


def test_cmd_snapshot_delete(tmp_path):
    session = make_session()
    snap_path = save_snapshot(session, "to_del", snapshot_dir=tmp_path)
    args = FakeArgs(snapshot=str(snap_path))
    result = cmd_snapshot_delete(args)
    assert result == 0
    assert not snap_path.exists()


def test_cmd_snapshot_delete_missing(tmp_path):
    args = FakeArgs(snapshot=str(tmp_path / "nope.json"))
    result = cmd_snapshot_delete(args)
    assert result == 1
