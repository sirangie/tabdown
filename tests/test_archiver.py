"""Tests for tabdown.archiver and archive_cli."""

from __future__ import annotations

import json
import zipfile
from pathlib import Path

import pytest

from tabdown.parser import Tab, TabSession
from tabdown.snapshot import save_snapshot
from tabdown.archiver import ArchiveError, archive_snapshots


def make_session(name: str = "Test Session") -> TabSession:
    session = TabSession(name=name)
    session.add_tab(Tab(title="Example", url="https://example.com"))
    session.add_tab(Tab(title="GitHub", url="https://github.com"))
    return session


def test_archive_creates_zip(tmp_path: Path) -> None:
    snap_dir = tmp_path / "snaps"
    snap_dir.mkdir()
    save_snapshot(snap_dir, make_session("S1"), snapshot_id="snap-001")
    save_snapshot(snap_dir, make_session("S2"), snapshot_id="snap-002")

    out = tmp_path / "archive.zip"
    manifest = archive_snapshots(snap_dir, out)

    assert out.exists()
    assert manifest.snapshot_count == 2
    assert set(manifest.snapshot_ids) == {"snap-001", "snap-002"}


def test_archive_contains_manifest(tmp_path: Path) -> None:
    snap_dir = tmp_path / "snaps"
    snap_dir.mkdir()
    save_snapshot(snap_dir, make_session(), snapshot_id="snap-abc")

    out = tmp_path / "out.zip"
    archive_snapshots(snap_dir, out)

    with zipfile.ZipFile(out) as zf:
        names = zf.namelist()
        assert "manifest.json" in names
        manifest_data = json.loads(zf.read("manifest.json"))
        assert manifest_data["snapshot_count"] == 1
        assert "snap-abc" in manifest_data["snapshot_ids"]


def test_archive_includes_markdown_by_default(tmp_path: Path) -> None:
    snap_dir = tmp_path / "snaps"
    snap_dir.mkdir()
    save_snapshot(snap_dir, make_session(), snapshot_id="snap-md")

    out = tmp_path / "out.zip"
    archive_snapshots(snap_dir, out, include_markdown=True)

    with zipfile.ZipFile(out) as zf:
        names = zf.namelist()
        assert "markdown/snap-md.md" in names
        md = zf.read("markdown/snap-md.md").decode()
        assert "Example" in md


def test_archive_no_markdown_flag(tmp_path: Path) -> None:
    snap_dir = tmp_path / "snaps"
    snap_dir.mkdir()
    save_snapshot(snap_dir, make_session(), snapshot_id="snap-nomd")

    out = tmp_path / "out.zip"
    archive_snapshots(snap_dir, out, include_markdown=False)

    with zipfile.ZipFile(out) as zf:
        names = zf.namelist()
        assert not any(n.startswith("markdown/") for n in names)


def test_archive_filter_by_ids(tmp_path: Path) -> None:
    snap_dir = tmp_path / "snaps"
    snap_dir.mkdir()
    save_snapshot(snap_dir, make_session("A"), snapshot_id="id-a")
    save_snapshot(snap_dir, make_session("B"), snapshot_id="id-b")
    save_snapshot(snap_dir, make_session("C"), snapshot_id="id-c")

    out = tmp_path / "out.zip"
    manifest = archive_snapshots(snap_dir, out, snapshot_ids=["id-a", "id-c"])

    assert manifest.snapshot_count == 2
    assert set(manifest.snapshot_ids) == {"id-a", "id-c"}


def test_archive_raises_when_no_snapshots(tmp_path: Path) -> None:
    snap_dir = tmp_path / "empty"
    snap_dir.mkdir()
    out = tmp_path / "out.zip"

    with pytest.raises(ArchiveError, match="No snapshots found"):
        archive_snapshots(snap_dir, out)


def test_archive_raises_for_unknown_ids(tmp_path: Path) -> None:
    snap_dir = tmp_path / "snaps"
    snap_dir.mkdir()
    save_snapshot(snap_dir, make_session(), snapshot_id="real-id")
    out = tmp_path / "out.zip"

    with pytest.raises(ArchiveError, match="None of the requested"):
        archive_snapshots(snap_dir, out, snapshot_ids=["ghost-id"])
