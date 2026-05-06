"""Tests for snapshot save/load/list/delete."""

import json
from pathlib import Path

import pytest

from tabdown.parser import Tab, TabSession
from tabdown.snapshot import (
    SnapshotError,
    delete_snapshot,
    list_snapshots,
    load_snapshot,
    save_snapshot,
)


def make_session(name="Test Session") -> TabSession:
    s = TabSession(name=name)
    s.add_tab(Tab(title="Google", url="https://google.com"))
    s.add_tab(Tab(title="GitHub", url="https://github.com", group="Dev"))
    s.add_tab(Tab(title="Lobsters", url="https://lobste.rs", group="Dev"))
    return s


def test_save_creates_file(tmp_path):
    session = make_session()
    path = save_snapshot(session, "my snapshot", snapshot_dir=tmp_path)
    assert path.exists()
    assert path.suffix == ".json"
    assert "my_snapshot" in path.name


def test_save_file_contains_expected_data(tmp_path):
    session = make_session()
    path = save_snapshot(session, "archive", snapshot_dir=tmp_path)
    data = json.loads(path.read_text())
    assert data["meta"]["name"] == "archive"
    assert data["meta"]["tab_count"] == 3
    assert data["meta"]["group_count"] == 1
    assert len(data["session"]["tabs"]) == 3


def test_load_snapshot_restores_session(tmp_path):
    session = make_session("Original")
    path = save_snapshot(session, "restore_test", snapshot_dir=tmp_path)
    restored = load_snapshot(path)
    assert len(restored.tabs) == 3
    titles = [t.title for t in restored.tabs]
    assert "Google" in titles
    assert "GitHub" in titles


def test_load_snapshot_preserves_groups(tmp_path):
    session = make_session()
    path = save_snapshot(session, "groups_test", snapshot_dir=tmp_path)
    restored = load_snapshot(path)
    dev_tabs = [t for t in restored.tabs if t.group == "Dev"]
    assert len(dev_tabs) == 2


def test_load_snapshot_missing_file_raises(tmp_path):
    with pytest.raises(SnapshotError, match="not found"):
        load_snapshot(tmp_path / "nonexistent.json")


def test_list_snapshots_empty_dir(tmp_path):
    results = list_snapshots(snapshot_dir=tmp_path)
    assert results == []


def test_list_snapshots_returns_metadata(tmp_path):
    s1 = make_session("Session A")
    s2 = make_session("Session B")
    save_snapshot(s1, "snap_a", snapshot_dir=tmp_path)
    save_snapshot(s2, "snap_b", snapshot_dir=tmp_path)
    results = list_snapshots(snapshot_dir=tmp_path)
    assert len(results) == 2
    names = {r.name for r in results}
    assert "snap_a" in names
    assert "snap_b" in names


def test_list_snapshots_nonexistent_dir(tmp_path):
    results = list_snapshots(snapshot_dir=tmp_path / "missing")
    assert results == []


def test_delete_snapshot(tmp_path):
    session = make_session()
    path = save_snapshot(session, "to_delete", snapshot_dir=tmp_path)
    assert path.exists()
    delete_snapshot(path)
    assert not path.exists()


def test_delete_snapshot_missing_raises(tmp_path):
    with pytest.raises(SnapshotError, match="not found"):
        delete_snapshot(tmp_path / "ghost.json")
