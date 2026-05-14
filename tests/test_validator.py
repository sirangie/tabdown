"""Tests for tabdown.validator."""
import pytest
from tabdown.parser import Tab, TabSession
from tabdown.validator import (
    ValidatorOptions,
    ValidationResult,
    validate_tab,
    validate_session,
)


def make_tab(url: str, title: str = "Some Page", group: str | None = None) -> Tab:
    return Tab(url=url, title=title, group=group)


def make_session(*tabs: Tab, name: str = "Test Session") -> TabSession:
    session = TabSession(name=name)
    for tab in tabs:
        session.add_tab(tab)
    return session


# --- validate_tab ---

def test_valid_tab_no_issues():
    tab = make_tab("https://example.com", "Example")
    issues = validate_tab(tab, ValidatorOptions())
    assert issues == []


def test_invalid_url_flagged():
    tab = make_tab("not-a-url", "Bad Tab")
    issues = validate_tab(tab, ValidatorOptions())
    rules = [i.rule for i in issues]
    assert "invalid_url" in rules


def test_empty_title_flagged_when_required():
    tab = make_tab("https://example.com", "")
    issues = validate_tab(tab, ValidatorOptions(require_title=True))
    rules = [i.rule for i in issues]
    assert "missing_title" in rules


def test_empty_title_ignored_when_not_required():
    tab = make_tab("https://example.com", "")
    issues = validate_tab(tab, ValidatorOptions(require_title=False))
    rules = [i.rule for i in issues]
    assert "missing_title" not in rules


def test_http_flagged_when_https_required():
    tab = make_tab("http://example.com", "Example")
    issues = validate_tab(tab, ValidatorOptions(require_https=True))
    rules = [i.rule for i in issues]
    assert "not_https" in rules


def test_https_not_flagged_when_https_required():
    tab = make_tab("https://example.com", "Example")
    issues = validate_tab(tab, ValidatorOptions(require_https=True))
    rules = [i.rule for i in issues]
    assert "not_https" not in rules


def test_title_too_long_flagged():
    tab = make_tab("https://example.com", "A" * 120)
    issues = validate_tab(tab, ValidatorOptions(max_title_length=100))
    rules = [i.rule for i in issues]
    assert "title_too_long" in rules


def test_title_within_limit_not_flagged():
    tab = make_tab("https://example.com", "Short title")
    issues = validate_tab(tab, ValidatorOptions(max_title_length=100))
    rules = [i.rule for i in issues]
    assert "title_too_long" not in rules


def test_blocked_domain_flagged():
    tab = make_tab("https://ads.example.com", "Ad Page")
    options = ValidatorOptions(blocked_domains=["ads.example.com"])
    issues = validate_tab(tab, options)
    rules = [i.rule for i in issues]
    assert "blocked_domain" in rules


def test_non_blocked_domain_not_flagged():
    tab = make_tab("https://example.com", "Good Page")
    options = ValidatorOptions(blocked_domains=["ads.example.com"])
    issues = validate_tab(tab, options)
    rules = [i.rule for i in issues]
    assert "blocked_domain" not in rules


# --- validate_session ---

def test_valid_session_no_issues():
    session = make_session(
        make_tab("https://example.com", "Example"),
        make_tab("https://python.org", "Python"),
    )
    result = validate_session(session)
    assert result.is_valid
    assert result.issue_count == 0


def test_session_with_bad_tabs_has_issues():
    session = make_session(
        make_tab("https://example.com", "Good"),
        make_tab("ftp://bad.com", "Bad"),
    )
    result = validate_session(session)
    assert not result.is_valid
    assert result.issue_count > 0


def test_summary_valid():
    session = make_session(make_tab("https://example.com", "Example"))
    result = validate_session(session)
    assert "no issues" in result.summary()


def test_summary_invalid_lists_issues():
    session = make_session(make_tab("bad-url", ""))
    result = validate_session(session)
    summary = result.summary()
    assert "issue" in summary
    assert "invalid_url" in summary
