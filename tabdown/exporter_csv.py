"""Export tab sessions to CSV format."""
from __future__ import annotations

import csv
import io
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional

from tabdown.parser import TabSession


class CsvExportError(Exception):
    """Raised when CSV export fails."""


@dataclass
class CsvExportOptions:
    include_group: bool = True
    include_pinned: bool = True
    include_notes: bool = True
    delimiter: str = ","
    quotechar: str = '"'


def _session_to_rows(session: TabSession, options: CsvExportOptions) -> List[dict]:
    """Convert a session's tabs to a list of row dicts."""
    rows: List[dict] = []
    for tab in session.all_tabs:
        row: dict = {"title": tab.title, "url": tab.url}
        if options.include_group:
            row["group"] = tab.group or ""
        if options.include_pinned:
            row["pinned"] = str(tab.pinned).lower()
        if options.include_notes:
            row["notes"] = getattr(tab, "notes", "") or ""
        rows.append(row)
    return rows


def export_session_to_csv_string(session: TabSession, options: Optional[CsvExportOptions] = None) -> str:
    """Return CSV content as a string."""
    if options is None:
        options = CsvExportOptions()
    rows = _session_to_rows(session, options)
    if not rows:
        return ""
    fieldnames = list(rows[0].keys())
    buf = io.StringIO()
    writer = csv.DictWriter(
        buf,
        fieldnames=fieldnames,
        delimiter=options.delimiter,
        quotechar=options.quotechar,
        quoting=csv.QUOTE_MINIMAL,
    )
    writer.writeheader()
    writer.writerows(rows)
    return buf.getvalue()


def export_session_to_csv_file(session: TabSession, path: Path, options: Optional[CsvExportOptions] = None) -> None:
    """Write CSV content to a file."""
    content = export_session_to_csv_string(session, options)
    try:
        path.write_text(content, encoding="utf-8")
    except OSError as exc:
        raise CsvExportError(f"Cannot write CSV to {path}: {exc}") from exc
