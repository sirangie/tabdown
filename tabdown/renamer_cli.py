"""CLI commands for the renamer module."""
from __future__ import annotations

import argparse
import sys

from tabdown.exporter import load_session_from_file
from tabdown.renamer import RenameOptions, RenameRule, rename_session
from tabdown.renderer import render_session


def cmd_rename(args: argparse.Namespace) -> None:
    try:
        session = load_session_from_file(args.input)
    except Exception as exc:
        print(f"Error loading session: {exc}", file=sys.stderr)
        sys.exit(1)

    rules: list[RenameRule] = []
    for raw in args.rule or []:
        parts = raw.split(":", 3)
        if len(parts) < 2:
            print(f"Invalid rule format '{raw}'. Expected pattern:replacement[:field]",
                  file=sys.stderr)
            sys.exit(1)
        pattern, replacement = parts[0], parts[1]
        field = parts[2] if len(parts) > 2 else "title"
        rules.append(RenameRule(pattern=pattern, replacement=replacement, field=field))

    if not rules:
        print("No rename rules provided. Use --rule PATTERN:REPLACEMENT[:FIELD]",
              file=sys.stderr)
        sys.exit(1)

    options = RenameOptions(rules=rules, stop_on_first_match=not args.apply_all)
    result = rename_session(session, options)

    if args.output:
        from tabdown.renderer import render_session_to_file
        render_session_to_file(result.session, args.output)
        print(f"Renamed {result.renamed_count} tab(s). Output written to {args.output}")
    else:
        print(render_session(result.session))
        print(f"\n# Renamed {result.renamed_count} tab(s).")


def build_renamer_parser(subparsers: argparse._SubParsersAction) -> None:
    p = subparsers.add_parser("rename", help="Rename tab titles or groups using regex rules")
    p.add_argument("input", help="Input session file (JSON)")
    p.add_argument("-o", "--output", help="Output markdown file (default: stdout)")
    p.add_argument(
        "--rule",
        action="append",
        metavar="PATTERN:REPLACEMENT[:FIELD]",
        help="Rename rule (field: title|url|group, default: title). Repeatable.",
    )
    p.add_argument(
        "--apply-all",
        action="store_true",
        default=False,
        help="Apply all matching rules instead of stopping at first match",
    )
    p.set_defaults(func=cmd_rename)
