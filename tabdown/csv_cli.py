"""CLI commands for CSV export."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from tabdown.exporter import load_session_from_file
from tabdown.exporter_csv import CsvExportError, CsvExportOptions, export_session_to_csv_file, export_session_to_csv_string


def cmd_csv_export(args: argparse.Namespace) -> None:
    session = load_session_from_file(Path(args.input), fmt=getattr(args, "format", None))
    options = CsvExportOptions(
        include_group=not args.no_group,
        include_pinned=not args.no_pinned,
        include_notes=not args.no_notes,
        delimiter=args.delimiter,
    )
    if args.output:
        try:
            export_session_to_csv_file(session, Path(args.output), options)
            print(f"CSV written to {args.output}")
        except CsvExportError as exc:
            print(f"Error: {exc}", file=sys.stderr)
            sys.exit(1)
    else:
        print(export_session_to_csv_string(session, options), end="")


def build_csv_parser(subparsers: argparse._SubParsersAction) -> argparse.ArgumentParser:  # type: ignore[type-arg]
    p = subparsers.add_parser("csv", help="Export session tabs to CSV")
    p.add_argument("input", help="Path to session JSON file")
    p.add_argument("-o", "--output", default="", help="Output CSV file (default: stdout)")
    p.add_argument("--format", choices=["chrome", "firefox"], default=None)
    p.add_argument("--no-group", action="store_true", help="Omit group column")
    p.add_argument("--no-pinned", action="store_true", help="Omit pinned column")
    p.add_argument("--no-notes", action="store_true", help="Omit notes column")
    p.add_argument("--delimiter", default=",", help="CSV delimiter (default: comma)")
    p.set_defaults(func=cmd_csv_export)
    return p
