"""Render a TabSession into markdown format."""

from tabdown.parser import Tab, TabSession


def render_tab(tab: Tab) -> str:
    """Render a single tab as a markdown list item."""
    return f"- [{tab.title}]({tab.url})"


def render_session(session: TabSession) -> str:
    """Render a full TabSession as a markdown document."""
    lines = []

    lines.append(f"# {session.name}")
    lines.append("")

    if session.groups:
        for group_name, tabs in session.groups.items():
            lines.append(f"## {group_name}")
            lines.append("")
            for tab in tabs:
                lines.append(render_tab(tab))
            lines.append("")

    ungrouped = session.ungrouped_tabs
    if ungrouped:
        if session.groups:
            lines.append("## Other")
            lines.append("")
        for tab in ungrouped:
            lines.append(render_tab(tab))
        lines.append("")

    return "\n".join(lines).rstrip() + "\n"


def render_session_to_file(session: TabSession, output_path: str) -> None:
    """Write rendered markdown to a file."""
    content = render_session(session)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(content)
