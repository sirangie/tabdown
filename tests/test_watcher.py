"""Tests for tabdown.watcher."""

from __future__ import annotations

import json
import time
from pathlib import Path

import pytest

from tabdown.watcher import WatchError, WatchOptions, watch_session


CHROME_SAMPLE = {
    "browser": "chrome",
    "session_name": "Watch Test",
    "tabs": [
        {"title": "Example", "url": "https://example.com", "group": None}
    ],
}


def _write_sample(path: Path) -> None:
    path.write_text(json.dumps(CHROME_SAMPLE))


def test_watch_missing_file_raises(tmp_path):
    opts = WatchOptions(
        input_path=tmp_path / "missing.json",
        output_path=tmp_path / "out.md",
        max_iterations=1,
    )
    with pytest.raises(WatchError, match="Input file not found"):
        watch_session(opts)


def test_watch_renders_on_first_run(tmp_path):
    src = tmp_path / "session.json"
    out = tmp_path / "session.md"
    _write_sample(src)

    opts = WatchOptions(
        input_path=src,
        output_path=out,
        poll_interval=0,
        max_iterations=1,
    )
    watch_session(opts)

    assert out.exists()
    content = out.read_text()
    assert "Watch Test" in content
    assert "Example" in content


def test_watch_calls_on_change_callback(tmp_path):
    src = tmp_path / "session.json"
    out = tmp_path / "session.md"
    _write_sample(src)

    changed_paths: list[Path] = []

    opts = WatchOptions(
        input_path=src,
        output_path=out,
        poll_interval=0,
        max_iterations=1,
        on_change=changed_paths.append,
    )
    watch_session(opts)

    assert changed_paths == [src]


def test_watch_on_error_callback_called_on_bad_file(tmp_path):
    src = tmp_path / "bad.json"
    out = tmp_path / "out.md"
    src.write_text("not valid json")

    errors: list[Exception] = []

    opts = WatchOptions(
        input_path=src,
        output_path=out,
        poll_interval=0,
        max_iterations=1,
        on_error=errors.append,
    )
    watch_session(opts)  # should not raise

    assert len(errors) == 1


def test_watch_rerenders_when_file_changes(tmp_path):
    src = tmp_path / "session.json"
    out = tmp_path / "session.md"
    _write_sample(src)

    change_count = 0

    def count_change(_: Path) -> None:
        nonlocal change_count
        change_count += 1

    # First pass — initial render
    opts = WatchOptions(
        input_path=src,
        output_path=out,
        poll_interval=0,
        max_iterations=1,
        on_change=count_change,
    )
    watch_session(opts)
    assert change_count == 1

    # Modify the file (force mtime change)
    time.sleep(0.01)
    updated = dict(CHROME_SAMPLE, session_name="Updated Session")
    src.write_text(json.dumps(updated))

    opts2 = WatchOptions(
        input_path=src,
        output_path=out,
        poll_interval=0,
        max_iterations=1,
        on_change=count_change,
    )
    watch_session(opts2)
    assert change_count == 2
    assert "Updated Session" in out.read_text()
