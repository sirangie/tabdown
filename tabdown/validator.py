"""Validate tab sessions against configurable rules."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional
from urllib.parse import urlparse

from tabdown.parser import Tab, TabSession


@dataclass
class ValidationIssue:
    tab_url: str
    tab_title: str
    rule: str
    message: str

    def __str__(self) -> str:
        return f"[{self.rule}] '{self.tab_title}' ({self.tab_url}): {self.message}"


@dataclass
class ValidationResult:
    issues: List[ValidationIssue] = field(default_factory=list)

    @property
    def is_valid(self) -> bool:
        return len(self.issues) == 0

    @property
    def issue_count(self) -> int:
        return len(self.issues)

    def summary(self) -> str:
        if self.is_valid:
            return "Session is valid — no issues found."
        lines = [f"{self.issue_count} issue(s) found:"]
        for issue in self.issues:
            lines.append(f"  - {issue}")
        return "\n".join(lines)


@dataclass
class ValidatorOptions:
    require_title: bool = True
    require_https: bool = False
    max_title_length: Optional[int] = None
    blocked_domains: List[str] = field(default_factory=list)


def _is_valid_url(url: str) -> bool:
    try:
        result = urlparse(url)
        return result.scheme in ("http", "https") and bool(result.netloc)
    except Exception:
        return False


def validate_tab(tab: Tab, options: ValidatorOptions) -> List[ValidationIssue]:
    issues: List[ValidationIssue] = []

    if not _is_valid_url(tab.url):
        issues.append(ValidationIssue(tab.url, tab.title, "invalid_url", "URL is not a valid http/https URL"))

    if options.require_title and not tab.title.strip():
        issues.append(ValidationIssue(tab.url, tab.title, "missing_title", "Tab has an empty title"))

    if options.require_https and not tab.url.startswith("https://"):
        issues.append(ValidationIssue(tab.url, tab.title, "not_https", "URL does not use HTTPS"))

    if options.max_title_length and len(tab.title) > options.max_title_length:
        issues.append(ValidationIssue(tab.url, tab.title, "title_too_long",
                                       f"Title exceeds {options.max_title_length} characters"))

    parsed = urlparse(tab.url)
    domain = parsed.netloc.lower().lstrip("www.")
    for blocked in options.blocked_domains:
        if domain == blocked.lower().lstrip("www."):
            issues.append(ValidationIssue(tab.url, tab.title, "blocked_domain",
                                           f"Domain '{domain}' is blocked"))
            break

    return issues


def validate_session(session: TabSession, options: Optional[ValidatorOptions] = None) -> ValidationResult:
    if options is None:
        options = ValidatorOptions()
    result = ValidationResult()
    for tab in session.all_tabs:
        result.issues.extend(validate_tab(tab, options))
    return result
