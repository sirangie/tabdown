"""CLI commands for archiving snapshots."""

from __future__ import annotations

import argparse
from pathlib import Path

from tabdown.archiver import ArchiveError, archive_snapshots


def cmd_archive_create(args: argparse.Namespace) -> None:
    snapshot_dir = Path(args.snapshot_dir)
    output_path = Path(args.output)
    ids = args.ids if args.ids else None
    no_markdown = getattr(args, "no_markdown", False)

    try:
        manifest = archive_snapshots(
            snapshot_dir=snapshot_dir,
            output_path=output_path,
            snapshot_ids=ids,
            include_markdown=not no_markdown,
        )
        print(f"Archived {manifest.snapshot_count} snapshot(s) to {output_path}")
        for sid in manifest.snapshot_ids:
            print(f"  - {sid}")
    except ArchiveError as exc:
        print(f"Archive error: {exc}")
        raise SystemExit(1)


def build_archive_parser(subparsers: argparse._SubParsersAction) -> None:  # type: ignore[type-arg]
    p = subparsers.add_parser("archive", help="Archive snapshots into a zip bundle")
    sub = p.add_subparsers(dest="archive_cmd")

    create_p = sub.add_parser("create", help="Create a zip archive of snapshots")
    create_p.add_argument(
        "--snapshot-dir",
        default=".tabdown_snapshots",
        help="Directory containing snapshot files (default: .tabdown_snapshots)",
    )
    create_p.add_argument(
        "--output",
        required=True,
        help="Output zip file path",
    )
    create_p.add_argument(
        "--ids",
        nargs="*",
        metavar="ID",
        help="Specific snapshot IDs to include (default: all)",
    )
    create_p.add_argument(
        "--no-markdown",
        action="store_true",
        help="Skip generating markdown files inside the archive",
    )
    create_p.set_defaults(func=cmd_archive_create)
