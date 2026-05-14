"""Tab relevance scoring based on recency, frequency, and keyword matching."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional
from urllib.parse import urlparse

from tabdown.parser import Tab, TabSession


@dataclass
class ScoreOptions:
    keywords: List[str] = field(default_factory=list)
    boost_pinned: bool = True
    boost_grouped: bool = False
    keyword_weight: float = 2.0
    pinned_bonus: float = 1.5
    grouped_bonus: float = 0.5


@dataclass
class ScoredTab:
    tab: Tab
    score: float

    def __lt__(self, other: "ScoredTab") -> bool:
        return self.score < other.score


def _keyword_score(tab: Tab, keywords: List[str], weight: float) -> float:
    if not keywords:
        return 0.0
    text = f"{tab.title} {tab.url}".lower()
    hits = sum(1 for kw in keywords if kw.lower() in text)
    return hits * weight


def score_tab(tab: Tab, options: ScoreOptions) -> ScoredTab:
    score = 0.0
    score += _keyword_score(tab, options.keywords, options.keyword_weight)
    if options.boost_pinned and getattr(tab, "pinned", False):
        score += options.pinned_bonus
    if options.boost_grouped and tab.group:
        score += options.grouped_bonus
    return ScoredTab(tab=tab, score=round(score, 4))


def score_session(
    session: TabSession,
    options: Optional[ScoreOptions] = None,
) -> List[ScoredTab]:
    if options is None:
        options = ScoreOptions()
    all_tabs = list(session.ungrouped_tabs)
    for tabs in session.groups.values():
        all_tabs.extend(tabs)
    scored = [score_tab(t, options) for t in all_tabs]
    return sorted(scored, key=lambda s: s.score, reverse=True)
