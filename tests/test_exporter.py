"""Tests for tabdown.exporter — loading sessions from browser JSON exports."""

import json
import pytest
from pathlib import Path

from tabdown.exporter import load_session_from_file, ExportError
from tabdown.parser import TabSession


SAMPLE_DIR = Path(__file__).parent.parent / "tabdown" / "formats"


def test_load_chrome_sample():
    session = load_session_from_file(SAMPLE_DIR / "chrome_sample.json", browser="chrome")
    assert isinstance(session, TabSession)
    assert session.name == "Work Research"
    assert len(session.tabs) == 3


def test_load_chrome_auto_detect():
    session = load_session_from_file(SAMPLE_DIR / "chrome_sample.json", browser="auto")
    assert session.name == "Work Research"


def test_load_firefox_sample():
    session = load_session_from_file(SAMPLE_DIR / "firefox_sample.json", browser="firefox")
    assert isinstance(session, TabSession)
    assert session.name == "Evening Reading"
    assert len(session.tabs) == 3


def test_load_firefox_auto_detect():
    session = load_session_from_file(SAMPLE_DIR / "firefox_sample.json", browser="auto")
    assert session.name == "Evening Reading"


def test_chrome_groups_preserved():
    session = load_session_from_file(SAMPLE_DIR / "chrome_sample.json", browser="chrome")
    dev_tabs = [t for t in session.tabs if t.group == "Dev"]
    assert len(dev_tabs) == 2


def test_file_not_found():
    with pytest.raises(FileNotFoundError):
        load_session_from_file("nonexistent_file.json")


def test_invalid_json(tmp_path):
    bad_file = tmp_path / "bad.json"
    bad_file.write_text("{ not valid json ")
    with pytest.raises(ExportError, match="Invalid JSON"):
        load_session_from_file(bad_file, browser="chrome")


def test_unsupported_browser(tmp_path):
    good_file = tmp_path / "data.json"
    good_file.write_text(json.dumps({"windows": []}))
    with pytest.raises(ExportError, match="Unsupported browser"):
        load_session_from_file(good_file, browser="safari")


def test_auto_detect_unknown_format(tmp_path):
    unknown = tmp_path / "unknown.json"
    unknown.write_text(json.dumps({"tabs": [], "source": "unknown"}))
    with pytest.raises(ExportError, match="auto-detect"):
        load_session_from_file(unknown, browser="auto")


def test_tabs_have_valid_urls():
    session = load_session_from_file(SAMPLE_DIR / "chrome_sample.json", browser="chrome")
    for tab in session.tabs:
        assert tab.url.startswith("http")
