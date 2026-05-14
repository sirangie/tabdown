"""CLI command for scoring and ranking tabs in a session."""
from __future__ import annotations

import argparse
from typing import List

from tabdown.exporter import load_session_from_file
from tabdown.scorer import ScoreOptions, score_session


def cmd_score(args: argparse.Namespace) -> None:
    try:
        session = load_session_from_file(args.input)
    except Exception as exc:  # pragma: no cover
        print(f"Error loading session: {exc}")
        return

    keywords: List[str] = args.keywords or []
    options = ScoreOptions(
        keywords=keywords,
        boost_pinned=not args.no_pinned_boost,
        boost_grouped=args.grouped_boost,
        keyword_weight=args.keyword_weight,
    )

    results = score_session(session, options)

    if not results:
        print("No tabs found.")
        return

    print(f"Scores for session: {session.name}")
    print("-" * 50)
    for ranked in results:
        group_label = f" [{ranked.tab.group}]" if ranked.tab.group else ""
        print(f"  {ranked.score:6.2f}  {ranked.tab.title}{group_label}")
        print(f"          {ranked.tab.url}")


def build_scorer_parser(subparsers: argparse._SubParsersAction) -> None:
    p = subparsers.add_parser("score", help="Score and rank tabs by relevance")
    p.add_argument("input", help="Path to session JSON file")
    p.add_argument(
        "--keywords", nargs="*", metavar="KW", help="Keywords to boost score"
    )
    p.add_argument(
        "--no-pinned-boost", action="store_true", help="Disable bonus for pinned tabs"
    )
    p.add_argument(
        "--grouped-boost", action="store_true", help="Add bonus for grouped tabs"
    )
    p.add_argument(
        "--keyword-weight",
        type=float,
        default=2.0,
        metavar="W",
        help="Score weight per keyword hit (default: 2.0)",
    )
    p.set_defaults(func=cmd_score)
