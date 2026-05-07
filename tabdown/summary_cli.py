"""CLI sub-commands for generating session summaries."""

from __future__ import annotations

import argparse
import sys

from tabdown.exporter import load_session_from_file
from tabdown.snapshot import load_snapshot
from tabdown.summarizer import SummaryOptions, summarize_session, summarize_session_to_file


def cmd_summary(args: argparse.Namespace) -> None:
    """Generate a markdown summary from a tab export or snapshot file."""
    try:
        if args.snapshot:
            session = load_snapshot(args.input)
        else:
            session = load_session_from_file(args.input, fmt=getattr(args, "format", None))
    except Exception as exc:  # noqa: BLE001
        print(f"error: could not load session — {exc}", file=sys.stderr)
        sys.exit(1)

    options = SummaryOptions(
        max_tabs_per_group=args.max_tabs,
        include_stats=not args.no_stats,
        include_ungrouped=not args.no_ungrouped,
        header_prefix=args.header_level * "#",
    )

    if args.output:
        summarize_session_to_file(session, args.output, options)
        print(f"Summary written to {args.output}")
    else:
        print(summarize_session(session, options), end="")


def build_summary_parser(subparsers: argparse._SubParsersAction) -> None:  # type: ignore[type-arg]
    p = subparsers.add_parser("summary", help="Generate a markdown summary of a tab session")
    p.add_argument("input", help="Path to a Chrome/Firefox JSON export or a .snapshot.json file")
    p.add_argument("-o", "--output", metavar="FILE", help="Write summary to FILE instead of stdout")
    p.add_argument(
        "--format",
        choices=["chrome", "firefox"],
        default=None,
        help="Force input format (auto-detected by default)",
    )
    p.add_argument(
        "--snapshot",
        action="store_true",
        help="Treat input as a tabdown snapshot file",
    )
    p.add_argument(
        "--max-tabs",
        type=int,
        default=5,
        metavar="N",
        help="Maximum tabs shown per group before truncation (default: 5)",
    )
    p.add_argument("--no-stats", action="store_true", help="Omit session statistics block")
    p.add_argument("--no-ungrouped", action="store_true", help="Omit the Ungrouped section")
    p.add_argument(
        "--header-level",
        type=int,
        default=2,
        choices=range(1, 7),
        metavar="N",
        help="Markdown heading level for group headers (1-6, default: 2)",
    )
    p.set_defaults(func=cmd_summary)
