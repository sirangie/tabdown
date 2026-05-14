"""CLI commands for exporting sessions to various output formats."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from tabdown.exporter import ExportError, load_session_from_file
from tabdown.renderer import render_session, render_session_to_file
from tabdown.summarizer import summarize_session_to_file, SummaryOptions


def cmd_export(args: argparse.Namespace) -> int:
    """Export a browser session file to markdown or summary output."""
    try:
        session = load_session_from_file(args.input, fmt=getattr(args, "format", None))
    except ExportError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    if args.output:
        out_path = Path(args.output)
        if args.summary:
            opts = SummaryOptions(
                max_url_length=getattr(args, "max_url_length", 80),
                include_stats=not getattr(args, "no_stats", False),
            )
            summarize_session_to_file(session, out_path, opts)
        else:
            render_session_to_file(session, out_path)
        print(f"exported to {out_path}")
    else:
        if args.summary:
            from tabdown.summarizer import summarize_session
            opts = SummaryOptions(
                max_url_length=getattr(args, "max_url_length", 80),
                include_stats=not getattr(args, "no_stats", False),
            )
            print(summarize_session(session, opts))
        else:
            print(render_session(session))

    return 0


def build_export_parser(sub: argparse._SubParsersAction) -> argparse.ArgumentParser:  # type: ignore[type-arg]
    p = sub.add_parser("export", help="export a browser session to markdown")
    p.add_argument("input", help="path to chrome/firefox JSON or bookmarks HTML")
    p.add_argument("-o", "--output", metavar="FILE", help="write output to FILE instead of stdout")
    p.add_argument("-f", "--format", choices=["chrome", "firefox", "bookmarks"],
                   help="force input format (auto-detected if omitted)")
    p.add_argument("--summary", action="store_true", help="produce a summary instead of full markdown")
    p.add_argument("--max-url-length", type=int, default=80, metavar="N",
                   help="truncate URLs longer than N chars in summary (default: 80)")
    p.add_argument("--no-stats", action="store_true", help="omit stats block from summary")
    p.set_defaults(func=cmd_export)
    return p
