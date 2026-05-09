"""CLI commands for keyword highlighting of tab sessions."""

from __future__ import annotations

import argparse
import sys

from tabdown.exporter import load_session_from_file
from tabdown.highlighter import HighlightOptions, highlight_session
from tabdown.renderer import render_session


def cmd_highlight(args: argparse.Namespace) -> None:
    try:
        session = load_session_from_file(args.input)
    except Exception as exc:  # noqa: BLE001
        print(f"Error loading session: {exc}", file=sys.stderr)
        sys.exit(1)

    opts = HighlightOptions(
        keywords=args.keywords,
        case_sensitive=args.case_sensitive,
        match_url=not args.title_only,
        match_title=not args.url_only,
    )

    result = highlight_session(session, opts)

    if args.stats:
        print(
            f"Matched {result.match_count} / {result.total_tabs} tabs",
            file=sys.stderr,
        )

    if result.match_count == 0:
        print("No tabs matched.", file=sys.stderr)
        return

    output = render_session(result.session)

    if args.output:
        with open(args.output, "w", encoding="utf-8") as fh:
            fh.write(output)
        print(f"Wrote {args.output}")
    else:
        print(output)


def build_highlight_parser(sub: argparse._SubParsersAction) -> None:  # type: ignore[type-arg]
    p = sub.add_parser("highlight", help="Find tabs matching keywords")
    p.add_argument("input", help="Session file (Chrome/Firefox JSON)")
    p.add_argument("keywords", nargs="+", help="Keywords to search for")
    p.add_argument("-o", "--output", help="Write markdown to file")
    p.add_argument("--case-sensitive", action="store_true", default=False)
    p.add_argument("--title-only", action="store_true", default=False)
    p.add_argument("--url-only", action="store_true", default=False)
    p.add_argument("--stats", action="store_true", default=False)
    p.set_defaults(func=cmd_highlight)
