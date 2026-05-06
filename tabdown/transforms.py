"""High-level transform pipeline: apply sort, dedupe, and filter in one call."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

from tabdown.deduplicator import DedupeOptions, dedupe_session
from tabdown.filters import FilterOptions, filter_session
from tabdown.parser import TabSession
from tabdown.sorter import SortOptions, sort_session


@dataclass
class TransformResult:
    session: TabSession
    original_count: int
    after_filter: int
    after_dedupe: int
    after_sort: int

    @property
    def removed_by_filter(self) -> int:
        return self.original_count - self.after_filter

    @property
    def removed_by_dedupe(self) -> int:
        return self.after_filter - self.after_dedupe


@dataclass
class TransformOptions:
    filter: Optional[FilterOptions] = None
    dedupe: Optional[DedupeOptions] = None
    sort: Optional[SortOptions] = None


def apply_transforms(session: TabSession, options: TransformOptions) -> TransformResult:
    """Apply filter → dedupe → sort pipeline and return a TransformResult."""
    original_count = len(session.tabs)

    # Step 1: filter
    if options.filter is not None:
        session = filter_session(session, options.filter)
    after_filter = len(session.tabs)

    # Step 2: dedupe
    removed_by_dedupe = 0
    if options.dedupe is not None:
        session, removed_by_dedupe = dedupe_session(session, options.dedupe)
    after_dedupe = len(session.tabs)

    # Step 3: sort
    if options.sort is not None:
        session = sort_session(session, options.sort)
    after_sort = len(session.tabs)

    return TransformResult(
        session=session,
        original_count=original_count,
        after_filter=after_filter,
        after_dedupe=after_dedupe,
        after_sort=after_sort,
    )
