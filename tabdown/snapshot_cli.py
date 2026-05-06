"""CLI subcommands for snapshot management."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from tabdown.exporter import load_session_from_file
from tabdown.snapshot import (
    DEFAULT_SNAPSHOT_DIR,
    SnapshotError,
    delete_snapshot,
    list_snapshots,
    load_snapshot,
    save_snapshot,
)
from tabdown.renderer import render_session_to_file


def cmd_snapshot_save(args: argparse.Namespace) -> int:
    try:
        session = load_session_from_file(Path(args.input), fmt=args.format)
        path = save_snapshot(session, args.name, snapshot_dir=Path(args.snapshot_dir))
        print(f"Snapshot saved: {path}")
        return 0
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


def cmd_snapshot_list(args: argparse.Namespace) -> int:
    snapshots = list_snapshots(snapshot_dir=Path(args.snapshot_dir))
    if not snapshots:
        print("No snapshots found.")
        return 0
    print(f"{'Name':<30} {'Created':<18} {'Tabs':>5} {'Groups':>7}")
    print("-" * 65)
    for s in snapshots:
        print(f"{s.name:<30} {s.created_at:<18} {s.tab_count:>5} {s.group_count:>7}")
    return 0


def cmd_snapshot_restore(args: argparse.Namespace) -> int:
    try:
        session = load_snapshot(Path(args.snapshot))
        out = Path(args.output)
        render_session_to_file(session, out)
        print(f"Restored snapshot to: {out}")
        return 0
    except SnapshotError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


def cmd_snapshot_delete(args: argparse.Namespace) -> int:
    try:
        delete_snapshot(Path(args.snapshot))
        print(f"Deleted: {args.snapshot}")
        return 0
    except SnapshotError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


def build_snapshot_parser(subparsers) -> None:
    p = subparsers.add_parser("snapshot", help="Manage tab session snapshots")
    sp = p.add_subparsers(dest="snapshot_cmd", required=True)

    save_p = sp.add_parser("save", help="Save a session as a snapshot")
    save_p.add_argument("input", help="Input session file")
    save_p.add_argument("name", help="Snapshot name")
    save_p.add_argument("--format", default=None, choices=["chrome", "firefox"])
    save_p.add_argument("--snapshot-dir", default=str(DEFAULT_SNAPSHOT_DIR))

    list_p = sp.add_parser("list", help="List saved snapshots")
    list_p.add_argument("--snapshot-dir", default=str(DEFAULT_SNAPSHOT_DIR))

    restore_p = sp.add_parser("restore", help="Restore snapshot to markdown")
    restore_p.add_argument("snapshot", help="Path to snapshot file")
    restore_p.add_argument("output", help="Output markdown file")

    del_p = sp.add_parser("delete", help="Delete a snapshot")
    del_p.add_argument("snapshot", help="Path to snapshot file")


SNAPSHOT_CMDS = {
    "save": cmd_snapshot_save,
    "list": cmd_snapshot_list,
    "restore": cmd_snapshot_restore,
    "delete": cmd_snapshot_delete,
}
