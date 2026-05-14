"""Rename tabs and groups within a session using pattern-based rules."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable, Dict, List, Optional
import re

from tabdown.parser import Tab, TabSession


@dataclass
class RenameRule:
    """A single rename rule: match pattern applied to field, replace with template."""
    pattern: str
    replacement: str
    field: str = "title"  # "title" | "url" | "group"
    flags: int = re.IGNORECASE

    def matches(self, tab: Tab) -> bool:
        value = self._get_field(tab)
        if value is None:
            return False
        return bool(re.search(self.pattern, value, self.flags))

    def apply(self, tab: Tab) -> Tab:
        value = self._get_field(tab)
        if value is None:
            return tab
        new_value = re.sub(self.pattern, self.replacement, value, flags=self.flags)
        if self.field == "title":
            return Tab(url=tab.url, title=new_value, group=tab.group,
                       pinned=tab.pinned, note=tab.note, tags=tab.tags)
        if self.field == "group":
            return Tab(url=tab.url, title=tab.title, group=new_value,
                       pinned=tab.pinned, note=tab.note, tags=tab.tags)
        return tab

    def _get_field(self, tab: Tab) -> Optional[str]:
        if self.field == "title":
            return tab.title
        if self.field == "url":
            return tab.url
        if self.field == "group":
            return tab.group
        return None


@dataclass
class RenameOptions:
    rules: List[RenameRule] = field(default_factory=list)
    stop_on_first_match: bool = True


@dataclass
class RenameResult:
    session: TabSession
    renamed_count: int


def rename_tab(tab: Tab, options: RenameOptions) -> tuple[Tab, bool]:
    """Apply rename rules to a single tab. Returns (new_tab, was_renamed)."""
    for rule in options.rules:
        if rule.matches(tab):
            new_tab = rule.apply(tab)
            if options.stop_on_first_match:
                return new_tab, True
            tab = new_tab
    return tab, False


def rename_session(session: TabSession, options: RenameOptions) -> RenameResult:
    """Apply rename rules to all tabs in a session."""
    new_session = TabSession(name=session.name)
    renamed_count = 0
    for tab in session.tabs:
        new_tab, changed = rename_tab(tab, options)
        new_session.add_tab(new_tab)
        if changed:
            renamed_count += 1
    return RenameResult(session=new_session, renamed_count=renamed_count)
