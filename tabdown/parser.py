"""Parse browser tab session data into structured Python objects."""

from dataclasses import dataclass, field
from typing import Optional
import json


@dataclass
class Tab:
    title: str
    url: str
    group: Optional[str] = None

    def __post_init__(self):
        if not self.url.startswith(("http://", "https://", "file://")):
            raise ValueError(f"Invalid URL: {self.url}")


@dataclass
class TabSession:
    name: str
    tabs: list[Tab] = field(default_factory=list)
    groups: dict[str, list[Tab]] = field(default_factory=dict)

    def add_tab(self, tab: Tab):
        self.tabs.append(tab)
        if tab.group:
            self.groups.setdefault(tab.group, []).append(tab)

    @property
    def ungrouped_tabs(self) -> list[Tab]:
        return [t for t in self.tabs if t.group is None]


def parse_session(data: dict) -> TabSession:
    """Parse a raw session dict into a TabSession object."""
    session_name = data.get("name", "Untitled Session")
    session = TabSession(name=session_name)

    raw_tabs = data.get("tabs", [])
    for raw in raw_tabs:
        title = raw.get("title") or raw.get("url", "Untitled")
        url = raw.get("url", "")
        group = raw.get("group", None)
        try:
            tab = Tab(title=title, url=url, group=group)
            session.add_tab(tab)
        except ValueError:
            continue  # skip malformed tabs

    return session


def parse_session_file(path: str) -> TabSession:
    """Load and parse a JSON session file."""
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return parse_session(data)
