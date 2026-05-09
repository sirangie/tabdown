"""CLI commands for pinned tab operations."""

import argparse
import sys

from tabdown.exporter import load_session_from_file
from tabdown.pinned import PinnedOptions, extract_pinned, pinned_to_session, strip_pinned
from tabdown.renderer import render_session, render_session_to_file


def cmd_pinned_list(args: argparse.Namespace) -> None:
    """List pinned tabs from a session file."""
    try:
        session = load_session_from_file(args.input)
    except Exception as exc:
        print(f"Error loading session: {exc}", file=sys.stderr)
        sys.exit(1)

    result = extract_pinned(session)
    if not result.pinned:
        print("No pinned tabs found.")
        return

    print(f"Pinned tabs ({result.pinned_count}):")
    for tab in result.pinned:
        group_label = f" [{tab.group}]" if tab.group else ""
        print(f"  {tab.title}{group_label} — {tab.url}")


def cmd_pinned_export(args: argparse.Namespace) -> None:
    """Export only pinned tabs to markdown."""
    try:
        session = load_session_from_file(args.input)
    except Exception as exc:
        print(f"Error loading session: {exc}", file=sys.stderr)
        sys.exit(1)

    opts = PinnedOptions(
        include_groups=not args.no_groups,
        session_name=args.name or None,
    )
    pinned_session = pinned_to_session(session, opts)

    if args.output:
        render_session_to_file(pinned_session, args.output)
        print(f"Pinned session written to {args.output}")
    else:
        print(render_session(pinned_session))


def build_pinned_parser(subparsers: argparse._SubParsersAction) -> None:
    pinned_p = subparsers.add_parser("pinned", help="Work with pinned tabs")
    pinned_sub = pinned_p.add_subparsers(dest="pinned_cmd")

    # list
    list_p = pinned_sub.add_parser("list", help="List pinned tabs")
    list_p.add_argument("input", help="Session file (Chrome/Firefox JSON)")
    list_p.set_defaults(func=cmd_pinned_list)

    # export
    export_p = pinned_sub.add_parser("export", help="Export pinned tabs to markdown")
    export_p.add_argument("input", help="Session file")
    export_p.add_argument("-o", "--output", help="Output markdown file")
    export_p.add_argument("--name", help="Override session name")
    export_p.add_argument("--no-groups", action="store_true", help="Strip group info")
    export_p.set_defaults(func=cmd_pinned_export)
