"""Batch export multiple tab session files to markdown in one pass."""
from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional

from tabdown.exporter import load_session_from_file
from tabdown.renderer import render_session


class BatchExportError(Exception):
    """Raised when a batch export operation fails."""


@dataclass
class BatchExportOptions:
    output_dir: str = "."
    overwrite: bool = False
    stop_on_error: bool = False
    suffix: str = ".md"


@dataclass
class BatchExportResult:
    succeeded: List[str] = field(default_factory=list)
    failed: List[tuple] = field(default_factory=list)  # (path, reason)

    @property
    def success_count(self) -> int:
        return len(self.succeeded)

    @property
    def failure_count(self) -> int:
        return len(self.failed)

    def summary(self) -> str:
        lines = [f"Exported: {self.success_count}  Failed: {self.failure_count}"]
        for path, reason in self.failed:
            lines.append(f"  FAIL {path}: {reason}")
        return "\n".join(lines)


def batch_export(
    input_paths: List[str],
    options: Optional[BatchExportOptions] = None,
) -> BatchExportResult:
    """Export each input file to a markdown file in output_dir."""
    if options is None:
        options = BatchExportOptions()

    out_dir = Path(options.output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    result = BatchExportResult()

    for src in input_paths:
        src_path = Path(src)
        dest = out_dir / (src_path.stem + options.suffix)

        if dest.exists() and not options.overwrite:
            msg = f"destination {dest} already exists (use overwrite=True)"
            result.failed.append((src, msg))
            if options.stop_on_error:
                raise BatchExportError(msg)
            continue

        try:
            session = load_session_from_file(str(src_path))
            markdown = render_session(session)
            dest.write_text(markdown, encoding="utf-8")
            result.succeeded.append(str(dest))
        except Exception as exc:  # noqa: BLE001
            msg = str(exc)
            result.failed.append((src, msg))
            if options.stop_on_error:
                raise BatchExportError(f"Failed to export {src}: {msg}") from exc

    return result
