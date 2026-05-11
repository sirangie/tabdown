"""CLI commands for the grouper module."""
from __future__ import annotations

import argparse
import sys

from tabdown.exporter import load_session_from_file
from tabdown.grouper import GroupBy, GrouperOptions, group_session
from tabdown.renderer import render_session


def cmd_group(args: argparse.Namespace) -> None:
    try:
        session = load_session_from_file(args.input, fmt=getattr(args, "format", None))
    except Exception as exc:
        print(f"Error loading session: {exc}", file=sys.stderr)
        sys.exit(1)

    by = GroupBy(args.by)
    keywords = args.keywords or []
    opts = GrouperOptions(
        by=by,
        keywords=keywords,
        fallback_group=args.fallback_group,
        strip_www=not args.keep_www,
    )

    result = group_session(session, opts)

    if args.stats:
        print(f"Groups created: {result.group_count}")
        for gname, urls in result.group_map.items():
            print(f"  {gname}: {len(urls)} tab(s)")
        print()

    md = render_session(result.session)
    if args.output:
        try:
            with open(args.output, "w", encoding="utf-8") as fh:
                fh.write(md)
            print(f"Written to {args.output}")
        except OSError as exc:
            print(f"Error writing output: {exc}", file=sys.stderr)
            sys.exit(1)
    else:
        print(md)


def build_grouper_parser(subparsers: argparse._SubParsersAction) -> None:  # type: ignore[type-arg]
    p = subparsers.add_parser("group", help="Re-group tabs by domain or keyword")
    p.add_argument("input", help="Path to session file (Chrome/Firefox JSON or bookmark HTML)")
    p.add_argument("-o", "--output", help="Output markdown file (default: stdout)")
    p.add_argument(
        "--by",
        choices=[e.value for e in GroupBy],
        default=GroupBy.DOMAIN.value,
        help="Grouping strategy (default: domain)",
    )
    p.add_argument(
        "--keywords",
        nargs="*",
        metavar="KW",
        help="Keywords for keyword-based grouping",
    )
    p.add_argument(
        "--fallback-group",
        default="Other",
        help="Group name for unmatched tabs when using keyword strategy",
    )
    p.add_argument("--keep-www", action="store_true", help="Do not strip www. prefix from domains")
    p.add_argument("--stats", action="store_true", help="Print grouping statistics before output")
    p.add_argument("--format", choices=["chrome", "firefox"], help="Force input format")
    p.set_defaults(func=cmd_group)
