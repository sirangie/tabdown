"""Extract and manage pinned tabs from a session."""

from dataclasses import dataclass, field
from typing import List, Optional

from tabdown.parser import Tab, TabSession


@dataclass
class PinnedOptions:
    """Options controlling pinned tab extraction."""
    include_groups: bool = True  # keep group info on pinned tabs
    session_name: Optional[str] = None  # override name for pinned-only session


@dataclass
class PinnedResult:
    """Result of extracting pinned tabs."""
    pinned: List[Tab] = field(default_factory=list)
    unpinned: List[Tab] = field(default_factory=list)

    @property
    def pinned_count(self) -> int:
        return len(self.pinned)

    @property
    def unpinned_count(self) -> int:
        return len(self.unpinned)


def extract_pinned(session: TabSession, options: Optional[PinnedOptions] = None) -> PinnedResult:
    """Split session tabs into pinned and unpinned."""
    opts = options or PinnedOptions()
    result = PinnedResult()

    for tab in session.tabs:
        if tab.pinned:
            result.pinned.append(tab)
        else:
            result.unpinned.append(tab)

    return result


def pinned_to_session(session: TabSession, options: Optional[PinnedOptions] = None) -> TabSession:
    """Return a new session containing only pinned tabs."""
    opts = options or PinnedOptions()
    result = extract_pinned(session, opts)

    name = opts.session_name or f"{session.name} (pinned)"
    new_session = TabSession(name=name)

    for tab in result.pinned:
        group = tab.group if opts.include_groups else None
        new_session.add_tab(Tab(
            title=tab.title,
            url=tab.url,
            group=group,
            pinned=tab.pinned,
            tags=list(tab.tags),
        ))

    return new_session


def strip_pinned(session: TabSession) -> TabSession:
    """Return a copy of the session with pinned tabs removed."""
    new_session = TabSession(name=session.name)
    for tab in session.tabs:
        if not tab.pinned:
            new_session.add_tab(tab)
    return new_session
