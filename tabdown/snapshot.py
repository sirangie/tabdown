"""Snapshot management: save and load named tab session snapshots."""

from __future__ import annotations

import json
import os
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from tabdown.parser import Tab, TabSession

DEFAULT_SNAPSHOT_DIR = Path.home() / ".tabdown" / "snapshots"


class SnapshotError(Exception):
    pass


@dataclass
class SnapshotMeta:
    name: str
    created_at: str
    tab_count: int
    group_count: int
    path: str


def _session_to_dict(session: TabSession) -> dict:
    return {
        "name": session.name,
        "tabs": [
            {"title": t.title, "url": t.url, "group": t.group}
            for t in session.tabs
        ],
    }


def _session_from_dict(data: dict) -> TabSession:
    session = TabSession(name=data.get("name", "Restored Session"))
    for t in data.get("tabs", []):
        session.add_tab(Tab(title=t["title"], url=t["url"], group=t.get("group")))
    return session


def save_snapshot(
    session: TabSession,
    name: str,
    snapshot_dir: Path = DEFAULT_SNAPSHOT_DIR,
) -> Path:
    snapshot_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    safe_name = name.replace(" ", "_").lower()
    filename = f"{safe_name}_{timestamp}.json"
    filepath = snapshot_dir / filename

    payload = {
        "meta": {
            "name": name,
            "created_at": timestamp,
            "tab_count": len(session.tabs),
            "group_count": len(session.groups),
        },
        "session": _session_to_dict(session),
    }
    filepath.write_text(json.dumps(payload, indent=2))
    return filepath


def load_snapshot(filepath: Path) -> TabSession:
    if not filepath.exists():
        raise SnapshotError(f"Snapshot not found: {filepath}")
    data = json.loads(filepath.read_text())
    return _session_from_dict(data["session"])


def list_snapshots(snapshot_dir: Path = DEFAULT_SNAPSHOT_DIR) -> list[SnapshotMeta]:
    if not snapshot_dir.exists():
        return []
    results = []
    for f in sorted(snapshot_dir.glob("*.json")):
        try:
            data = json.loads(f.read_text())
            meta = data["meta"]
            results.append(
                SnapshotMeta(
                    name=meta["name"],
                    created_at=meta["created_at"],
                    tab_count=meta["tab_count"],
                    group_count=meta["group_count"],
                    path=str(f),
                )
            )
        except Exception:
            continue
    return results


def delete_snapshot(filepath: Path) -> None:
    if not filepath.exists():
        raise SnapshotError(f"Snapshot not found: {filepath}")
    filepath.unlink()
