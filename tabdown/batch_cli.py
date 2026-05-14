"""CLI commands for batch exporting tab session files."""
from __future__ import annotations

import argparse
import sys

from tabdown.exporter_batch import BatchExportError, BatchExportOptions, batch_export


def cmd_batch_export(args: argparse.Namespace) -> None:
    if not args.inputs:
        print("No input files provided.", file=sys.stderr)
        sys.exit(1)

    options = BatchExportOptions(
        output_dir=args.output_dir,
        overwrite=args.overwrite,
        stop_on_error=args.stop_on_error,
        suffix=args.suffix,
    )

    try:
        result = batch_export(args.inputs, options)
    except BatchExportError as exc:
        print(f"Batch export aborted: {exc}", file=sys.stderr)
        sys.exit(1)

    print(result.summary())

    if result.failure_count > 0 and not args.stop_on_error:
        sys.exit(2)


def build_batch_parser(subparsers: argparse._SubParsersAction) -> argparse.ArgumentParser:  # noqa: SLF001
    p = subparsers.add_parser(
        "batch-export",
        help="Export multiple session files to markdown in one pass",
    )
    p.add_argument("inputs", nargs="+", metavar="FILE", help="Input session JSON files")
    p.add_argument(
        "-o", "--output-dir", default=".", help="Directory for output markdown files"
    )
    p.add_argument(
        "--overwrite", action="store_true", help="Overwrite existing output files"
    )
    p.add_argument(
        "--stop-on-error",
        action="store_true",
        help="Abort immediately on first failure",
    )
    p.add_argument(
        "--suffix", default=".md", help="File suffix for output files (default: .md)"
    )
    p.set_defaults(func=cmd_batch_export)
    return p
