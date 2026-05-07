"""Archive multiple snapshots into a single zip bundle for export/backup."""

from __future__ import annotations

import json
import zipfile
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import List, Optional

from tabdown.snapshot import SnapshotMeta, list_snapshots, load_snapshot
from tabdown.renderer import render_session


class ArchiveError(Exception):
    pass


@dataclass
class ArchiveManifest:
    created_at: str
    snapshot_count: int
    snapshot_ids: List[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "created_at": self.created_at,
            "snapshot_count": self.snapshot_count,
            "snapshot_ids": self.snapshot_ids,
        }


def _build_manifest(metas: List[SnapshotMeta]) -> ArchiveManifest:
    return ArchiveManifest(
        created_at=datetime.utcnow().isoformat(),
        snapshot_count=len(metas),
        snapshot_ids=[m.snapshot_id for m in metas],
    )


def archive_snapshots(
    snapshot_dir: Path,
    output_path: Path,
    snapshot_ids: Optional[List[str]] = None,
    include_markdown: bool = True,
) -> ArchiveManifest:
    """Bundle snapshots from snapshot_dir into a zip at output_path.

    If snapshot_ids is None, all available snapshots are included.
    When include_markdown is True, a rendered .md file is added per snapshot.
    """
    metas = list_snapshots(snapshot_dir)
    if not metas:
        raise ArchiveError(f"No snapshots found in {snapshot_dir}")

    if snapshot_ids is not None:
        id_set = set(snapshot_ids)
        metas = [m for m in metas if m.snapshot_id in id_set]
        if not metas:
            raise ArchiveError("None of the requested snapshot IDs were found")

    manifest = _build_manifest(metas)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(output_path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("manifest.json", json.dumps(manifest.to_dict(), indent=2))

        for meta in metas:
            snap_file = snapshot_dir / f"{meta.snapshot_id}.json"
            if not snap_file.exists():
                continue
            zf.write(snap_file, arcname=f"snapshots/{meta.snapshot_id}.json")

            if include_markdown:
                session = load_snapshot(snapshot_dir, meta.snapshot_id)
                md_content = render_session(session)
                zf.writestr(f"markdown/{meta.snapshot_id}.md", md_content)

    return manifest
