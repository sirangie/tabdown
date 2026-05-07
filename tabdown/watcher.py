"""Watch a session file for changes and re-render on update."""

from __future__ import annotations

import time
import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable, Optional

from tabdown.exporter import load_session_from_file
from tabdown.renderer import render_session_to_file


class WatchError(Exception):
    """Raised when the watcher encounters a fatal error."""


@dataclass
class WatchOptions:
    input_path: Path
    output_path: Path
    poll_interval: float = 1.0
    max_iterations: Optional[int] = None  # None = run forever; used in tests
    on_change: Callable[[Path], None] = field(default=lambda p: None)
    on_error: Callable[[Exception], None] = field(default=lambda e: None)


def _get_mtime(path: Path) -> float:
    try:
        return path.stat().st_mtime
    except FileNotFoundError:
        return 0.0


def _render(options: WatchOptions) -> None:
    session = load_session_from_file(str(options.input_path))
    render_session_to_file(session, str(options.output_path))


def watch_session(options: WatchOptions) -> None:
    """Poll *input_path* and re-render to *output_path* whenever it changes.

    Blocks until *max_iterations* cycles have been completed (or forever when
    *max_iterations* is ``None``).
    """
    if not options.input_path.exists():
        raise WatchError(f"Input file not found: {options.input_path}")

    last_mtime = 0.0
    iterations = 0

    while True:
        current_mtime = _get_mtime(options.input_path)

        if current_mtime != last_mtime:
            try:
                _render(options)
                last_mtime = current_mtime
                options.on_change(options.input_path)
            except Exception as exc:  # noqa: BLE001
                options.on_error(exc)

        iterations += 1
        if options.max_iterations is not None and iterations >= options.max_iterations:
            break

        time.sleep(options.poll_interval)
