"""CLI commands for template-based rendering."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from tabdown.exporter import load_session_from_file
from tabdown.templater import (
    TemplateError,
    TemplateOptions,
    load_template_options,
    render_session_with_template,
)


def cmd_template_render(args: argparse.Namespace) -> None:
    try:
        session = load_session_from_file(Path(args.input), fmt=getattr(args, "format", None))
    except Exception as exc:
        print(f"Error loading session: {exc}", file=sys.stderr)
        sys.exit(1)

    if args.template_file:
        try:
            opts = load_template_options(Path(args.template_file))
        except TemplateError as exc:
            print(f"Template error: {exc}", file=sys.stderr)
            sys.exit(1)
    else:
        opts = TemplateOptions(
            tab_template=args.tab_template,
            group_header=args.group_header,
            session_header=args.session_header,
            include_stats=args.include_stats,
        )

    output = render_session_with_template(session, opts)

    if args.output:
        Path(args.output).write_text(output, encoding="utf-8")
        print(f"Written to {args.output}")
    else:
        print(output, end="")


def build_template_parser(subparsers: argparse._SubParsersAction) -> None:
    p = subparsers.add_parser("template", help="Render session using a custom template")
    p.add_argument("input", help="Input session JSON file")
    p.add_argument("-o", "--output", help="Output markdown file (default: stdout)")
    p.add_argument("-t", "--template-file", help="Path to .tpl options file")
    p.add_argument("--format", choices=["chrome", "firefox"], default=None)
    p.add_argument(
        "--tab-template",
        default="- [{title}]({url})",
        help="Template for each tab line",
    )
    p.add_argument(
        "--group-header",
        default="### {group}",
        help="Template for group headers",
    )
    p.add_argument(
        "--session-header",
        default="# {name}",
        help="Template for session header",
    )
    p.add_argument(
        "--include-stats",
        action="store_true",
        help="Include tab count in output",
    )
    p.set_defaults(func=cmd_template_render)
