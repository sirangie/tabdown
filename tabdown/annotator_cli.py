"""CLI commands for the annotator feature."""

from __future__ import annotations

import argparse
import json
import sys

from tabdown.annotator import AnnotationOptions, annotate_session
from tabdown.exporter import load_session_from_file
from tabdown.renderer import render_session_to_file


def cmd_annotate(args: argparse.Namespace) -> None:
    """Load a session, apply annotations from a JSON map, render output."""
    try:
        session = load_session_from_file(args.input, fmt=getattr(args, "format", None))
    except Exception as exc:  # noqa: BLE001
        print(f"[error] could not load session: {exc}", file=sys.stderr)
        sys.exit(1)

    try:
        with open(args.annotations, encoding="utf-8") as fh:
            raw: dict = json.load(fh)
    except Exception as exc:  # noqa: BLE001
        print(f"[error] could not load annotations file: {exc}", file=sys.stderr)
        sys.exit(1)

    if not isinstance(raw, dict):
        print("[error] annotations file must be a JSON object mapping url -> note", file=sys.stderr)
        sys.exit(1)

    opts = AnnotationOptions(
        overwrite=not args.no_overwrite,
        prefix=args.prefix or "",
    )

    result = annotate_session(session, raw, opts)
    print(
        f"Annotated {result.annotated_count} tab(s), "
        f"skipped {result.skipped_count} tab(s)."
    )

    if args.output:
        render_session_to_file(result.session, args.output)
        print(f"Output written to {args.output}")
    else:
        from tabdown.renderer import render_session
        print(render_session(result.session))


def build_annotator_parser(sub: argparse._SubParsersAction) -> None:  # type: ignore[type-arg]
    p = sub.add_parser("annotate", help="Attach notes to tabs by URL")
    p.add_argument("input", help="Session file (Chrome/Firefox JSON)")
    p.add_argument("annotations", help="JSON file mapping URL -> note string")
    p.add_argument("-o", "--output", help="Write rendered markdown to this file")
    p.add_argument("--format", choices=["chrome", "firefox"], default=None)
    p.add_argument("--no-overwrite", action="store_true", help="Skip tabs that already have an annotation")
    p.add_argument("--prefix", default="", help="Prefix prepended to every annotation")
    p.set_defaults(func=cmd_annotate)
