"""Annotator: attach user notes/annotations to tabs in a session."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional

from tabdown.parser import Tab, TabSession


@dataclass
class AnnotationOptions:
    """Options controlling how annotations are applied."""
    overwrite: bool = True  # overwrite existing annotation if present
    prefix: str = ""        # optional prefix prepended to every annotation


@dataclass
class AnnotationResult:
    """Result of an annotation pass over a session."""
    session: TabSession
    annotated: List[Tab] = field(default_factory=list)
    skipped: List[Tab] = field(default_factory=list)

    @property
    def annotated_count(self) -> int:
        return len(self.annotated)

    @property
    def skipped_count(self) -> int:
        return len(self.skipped)


def annotate_tab(
    tab: Tab,
    note: str,
    options: Optional[AnnotationOptions] = None,
) -> Tab:
    """Return a copy of *tab* with *note* stored in its metadata."""
    options = options or AnnotationOptions()
    full_note = f"{options.prefix}{note}" if options.prefix else note
    existing = (tab.metadata or {}).get("annotation", "")
    if existing and not options.overwrite:
        return tab
    new_meta = dict(tab.metadata or {})
    new_meta["annotation"] = full_note
    return Tab(
        url=tab.url,
        title=tab.title,
        group=tab.group,
        pinned=tab.pinned,
        metadata=new_meta,
    )


def annotate_session(
    session: TabSession,
    annotations: Dict[str, str],
    options: Optional[AnnotationOptions] = None,
) -> AnnotationResult:
    """Apply *annotations* (url -> note) to matching tabs in *session*.

    Tabs whose URL is not in *annotations* are left unchanged.
    """
    options = options or AnnotationOptions()
    new_session = TabSession(name=session.name)
    result = AnnotationResult(session=new_session)

    for tab in session.tabs:
        if tab.url in annotations:
            updated = annotate_tab(tab, annotations[tab.url], options)
            new_session.add_tab(updated)
            result.annotated.append(updated)
        else:
            new_session.add_tab(tab)
            result.skipped.append(tab)

    return result
