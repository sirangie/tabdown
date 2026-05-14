"""CLI commands for the session splitter."""
from __future__ import annotations

import argparse
import sys

from tabdown.exporter import load_session_from_file
from tabdown.renderer import render_session
from tabdown.splitter import SplitBy, SplitOptions, split_session


def cmd_split(args: argparse.Namespace) -> None:
    try:
        session = load_session_from_file(args.input, fmt=getattr(args, "format", None))
    except Exception as exc:
        print(f"error: {exc}", file=sys.stderr)
        sys.exit(1)

    opts = SplitOptions(
        by=SplitBy(args.by),
        chunk_size=args.chunk_size,
        name_prefix=args.prefix or "",
    )

    result = split_session(session, opts)

    if args.summary:
        print(f"Split into {result.session_count} session(s), {result.total_tabs} tab(s) total.")
        for s in result.sessions:
            print(f"  [{len(s.tabs):>3} tabs] {s.name}")
        return

    for s in result.sessions:
        print(f"\n## {s.name}\n")
        print(render_session(s))


def build_splitter_parser(subparsers: argparse._SubParsersAction) -> None:  # type: ignore[type-arg]
    p = subparsers.add_parser("split", help="Split a session into multiple sessions")
    p.add_argument("input", help="Path to the session file")
    p.add_argument(
        "--by",
        choices=[e.value for e in SplitBy],
        default=SplitBy.GROUP.value,
        help="Dimension to split on (default: group)",
    )
    p.add_argument(
        "--chunk-size",
        type=int,
        default=10,
        dest="chunk_size",
        help="Tabs per chunk when splitting by count (default: 10)",
    )
    p.add_argument("--prefix", default="", help="Name prefix for generated sessions")
    p.add_argument("--format", default=None, help="Force input format (chrome/firefox)")
    p.add_argument("--summary", action="store_true", help="Print summary instead of markdown")
    p.set_defaults(func=cmd_split)
