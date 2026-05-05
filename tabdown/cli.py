"""Command-line interface for tabdown."""

import argparse
import sys
from pathlib import Path

from tabdown.exporter import load_session_from_file, ExportError
from tabdown.renderer import render_session, render_session_to_file


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="tabdown",
        description="Convert browser tab sessions to structured markdown.",
    )
    parser.add_argument(
        "input",
        type=Path,
        help="Path to browser JSON export file.",
    )
    parser.add_argument(
        "-o", "--output",
        type=Path,
        default=None,
        help="Output markdown file path. Prints to stdout if omitted.",
    )
    parser.add_argument(
        "-b", "--browser",
        choices=["chrome", "firefox", "auto"],
        default="auto",
        help="Browser format of the export file (default: auto).",
    )
    return parser


def main(argv=None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    try:
        session = load_session_from_file(args.input, browser=args.browser)
    except FileNotFoundError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
    except ExportError as e:
        print(f"Export error: {e}", file=sys.stderr)
        return 1

    if args.output:
        render_session_to_file(session, args.output)
        print(f"Written to {args.output}")
    else:
        print(render_session(session))

    return 0


if __name__ == "__main__":
    sys.exit(main())
