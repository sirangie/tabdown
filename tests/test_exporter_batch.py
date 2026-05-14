"""Tests for batch export functionality."""
from __future__ import annotations

import json
import os
from pathlib import Path

import pytest

from tabdown.exporter_batch import (
    BatchExportError,
    BatchExportOptions,
    BatchExportResult,
    batch_export,
)


def _write_chrome_session(path: Path, name: str = "Test") -> None:
    data = {
        "type": "chrome",
        "session_name": name,
        "tabs": [
            {"title": "Example", "url": "https://example.com", "group": None, "pinned": False}
        ],
    }
    path.write_text(json.dumps(data), encoding="utf-8")


def test_batch_export_single_file(tmp_path):
    src = tmp_path / "session.json"
    _write_chrome_session(src)
    out_dir = tmp_path / "out"

    result = batch_export([str(src)], BatchExportOptions(output_dir=str(out_dir)))

    assert result.success_count == 1
    assert result.failure_count == 0
    assert (out_dir / "session.md").exists()


def test_batch_export_multiple_files(tmp_path):
    srcs = []
    for i in range(3):
        p = tmp_path / f"s{i}.json"
        _write_chrome_session(p, name=f"Session {i}")
        srcs.append(str(p))

    out_dir = tmp_path / "out"
    result = batch_export(srcs, BatchExportOptions(output_dir=str(out_dir)))

    assert result.success_count == 3
    assert result.failure_count == 0


def test_batch_export_skips_existing_without_overwrite(tmp_path):
    src = tmp_path / "session.json"
    _write_chrome_session(src)
    out_dir = tmp_path / "out"
    out_dir.mkdir()
    (out_dir / "session.md").write_text("existing", encoding="utf-8")

    result = batch_export([str(src)], BatchExportOptions(output_dir=str(out_dir), overwrite=False))

    assert result.failure_count == 1
    assert "already exists" in result.failed[0][1]
    assert (out_dir / "session.md").read_text() == "existing"


def test_batch_export_overwrites_when_flag_set(tmp_path):
    src = tmp_path / "session.json"
    _write_chrome_session(src)
    out_dir = tmp_path / "out"
    out_dir.mkdir()
    (out_dir / "session.md").write_text("old content", encoding="utf-8")

    result = batch_export([str(src)], BatchExportOptions(output_dir=str(out_dir), overwrite=True))

    assert result.success_count == 1
    content = (out_dir / "session.md").read_text()
    assert content != "old content"


def test_batch_export_bad_file_recorded_in_failures(tmp_path):
    bad = tmp_path / "bad.json"
    bad.write_text("not valid json", encoding="utf-8")
    out_dir = tmp_path / "out"

    result = batch_export([str(bad)], BatchExportOptions(output_dir=str(out_dir)))

    assert result.failure_count == 1
    assert result.success_count == 0


def test_batch_export_stop_on_error_raises(tmp_path):
    bad = tmp_path / "bad.json"
    bad.write_text("not valid json", encoding="utf-8")
    out_dir = tmp_path / "out"

    with pytest.raises(BatchExportError):
        batch_export(
            [str(bad)],
            BatchExportOptions(output_dir=str(out_dir), stop_on_error=True),
        )


def test_batch_export_summary_string(tmp_path):
    src = tmp_path / "ok.json"
    _write_chrome_session(src)
    bad = tmp_path / "bad.json"
    bad.write_text("nope", encoding="utf-8")
    out_dir = tmp_path / "out"

    result = batch_export([str(src), str(bad)], BatchExportOptions(output_dir=str(out_dir)))

    summary = result.summary()
    assert "Exported: 1" in summary
    assert "Failed: 1" in summary
