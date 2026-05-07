"""Custom markdown template support for rendering tab sessions."""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

from tabdown.parser import Tab, TabSession


@dataclass
class TemplateOptions:
    template_str: str = ""
    tab_template: str = "- [{title}]({url})"
    group_header: str = "### {group}"
    session_header: str = "# {name}"
    include_stats: bool = False


class TemplateError(Exception):
    pass


_PLACEHOLDER_RE = re.compile(r"\{(\w+)\}")


def _fill(template: str, context: dict) -> str:
    """Fill placeholders in template from context dict, leaving unknown ones."""
    def replacer(m: re.Match) -> str:
        key = m.group(1)
        return str(context.get(key, m.group(0)))
    return _PLACEHOLDER_RE.sub(replacer, template)


def render_tab_with_template(tab: Tab, opts: TemplateOptions) -> str:
    context = {
        "title": tab.title,
        "url": tab.url,
        "group": tab.group or "",
    }
    return _fill(opts.tab_template, context)


def render_session_with_template(session: TabSession, opts: TemplateOptions) -> str:
    lines: list[str] = []
    lines.append(_fill(opts.session_header, {"name": session.name}))
    lines.append("")

    if opts.include_stats:
        total = sum(len(tabs) for tabs in session.groups.values()) + len(session.ungrouped_tabs)
        lines.append(f"_Total tabs: {total}_")
        lines.append("")

    if session.ungrouped_tabs:
        for tab in session.ungrouped_tabs:
            lines.append(render_tab_with_template(tab, opts))
        lines.append("")

    for group, tabs in session.groups.items():
        lines.append(_fill(opts.group_header, {"group": group}))
        lines.append("")
        for tab in tabs:
            lines.append(render_tab_with_template(tab, opts))
        lines.append("")

    return "\n".join(lines).rstrip() + "\n"


def load_template_options(path: Path) -> TemplateOptions:
    """Load template options from a simple .ini-style text file."""
    opts = TemplateOptions()
    if not path.exists():
        raise TemplateError(f"Template file not found: {path}")
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if "=" not in line:
            continue
        key, _, value = line.partition("=")
        key = key.strip()
        value = value.strip()
        if key == "tab_template":
            opts.tab_template = value
        elif key == "group_header":
            opts.group_header = value
        elif key == "session_header":
            opts.session_header = value
        elif key == "include_stats":
            opts.include_stats = value.lower() in ("1", "true", "yes")
    return opts
