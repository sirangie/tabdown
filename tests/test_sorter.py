"""Tests for tabdown.sorter."""
import pytest

from tabdown.parser import Tab, TabSession
from tabdown.sorter import (
    SortKey,
    SortOptions,
    SortOrder,
    sort_session,
    sort_tabs,
)


def make_tab(title: str, url: str, group: str | None = None) -> Tab:
    return Tab(title=title, url=url, group=group)


def make_session(*tabs: Tab) -> TabSession:
    s = TabSession(name="test")
    for t in tabs:
        s.add_tab(t)
    return s


def test_sort_by_title_asc():
    tabs = [
        make_tab("Zebra", "https://z.com"),
        make_tab("Apple", "https://a.com"),
        make_tab("Mango", "https://m.com"),
    ]
    opts = SortOptions(key=SortKey.TITLE, order=SortOrder.ASC, group_first=False)
    result = sort_tabs(tabs, opts)
    assert [t.title for t in result] == ["Apple", "Mango", "Zebra"]


def test_sort_by_title_desc():
    tabs = [
        make_tab("Zebra", "https://z.com"),
        make_tab("Apple", "https://a.com"),
    ]
    opts = SortOptions(key=SortKey.TITLE, order=SortOrder.DESC, group_first=False)
    result = sort_tabs(tabs, opts)
    assert result[0].title == "Zebra"


def test_sort_by_domain():
    tabs = [
        make_tab("Page", "https://zebra.org/page"),
        make_tab("Page", "https://apple.io/page"),
    ]
    opts = SortOptions(key=SortKey.DOMAIN, order=SortOrder.ASC, group_first=False)
    result = sort_tabs(tabs, opts)
    assert result[0].url == "https://apple.io/page"


def test_sort_group_first_clusters_groups():
    tabs = [
        make_tab("B-tab", "https://b.com", group="Beta"),
        make_tab("A-tab", "https://a.com", group="Alpha"),
        make_tab("B2-tab", "https://b2.com", group="Beta"),
        make_tab("No group", "https://ng.com"),
    ]
    opts = SortOptions(key=SortKey.TITLE, order=SortOrder.ASC, group_first=True)
    result = sort_tabs(tabs, opts)
    groups_in_order = [t.group for t in result]
    # Alpha cluster comes before Beta cluster; ungrouped last
    assert groups_in_order == ["Alpha", "Beta", "Beta", None]


def test_sort_session_returns_new_session():
    t1 = make_tab("Z", "https://z.com")
    t2 = make_tab("A", "https://a.com")
    session = make_session(t1, t2)
    opts = SortOptions(key=SortKey.TITLE, order=SortOrder.ASC, group_first=False)
    new_session = sort_session(session, opts)
    titles = [t.title for t in new_session.tabs.values()]
    assert titles == ["A", "Z"]
    # original unchanged
    assert list(session.tabs.values())[0].title == "Z"


def test_sort_default_options():
    tabs = [make_tab("C", "https://c.com"), make_tab("A", "https://a.com")]
    result = sort_tabs(tabs)  # default options
    assert result[0].title == "A"
