"""
tests/test_exceptions
~~~~~~~~~~~~~~~~~~~~~
"""

import datetime
from unittest.mock import MagicMock

import pytest
from playwright.sync_api import Error as PlaywrightError

import comics
from comics._gocomics import ComicsAPI


def test_invalid_endpoint():
    """
    Tests proper raise of InvalidEndpointError when using an endpoint that does
    not exist in GoComics.
    """
    with pytest.raises(comics.exceptions.InvalidEndpointError):
        comics.search("invalid_endpoint", date="2000-01-01")


def test_comic_not_found():
    """
    Tests proper raise of InvalidDateError when using a date that does not exist
    for the queried comic.
    """
    with pytest.raises(comics.exceptions.InvalidDateError):
        invalid_foxtrot = comics.search(
            "foxtrot", date="2025-04-03"
        )  # Known to be a non-existent date for Foxtrot
        invalid_foxtrot.image_url


def test_date_before_creation():
    """
    Tests proper raise of InvalidDateError when using date that is before the
    comic's creation date.
    """
    with pytest.raises(comics.exceptions.InvalidDateError):
        comics.search("calvinandhobbes", date="1900-01-01")


def test_invalid_future_date():
    """Tests proper raise of InvalidDateError when using date that is in the future."""
    with pytest.raises(comics.exceptions.InvalidDateError):
        comics.search("calvinandhobbes", date="2050-01-01")


def test_future_date_reroute():
    """Tests that GoComics silently rerouting a future date to today raises InvalidDateError."""
    with pytest.raises(comics.exceptions.InvalidDateError):
        # Call internal API to bypass internal future date check
        comic = comics._gocomics.ComicsAPI(
            "brewsterrockit", "Brewster Rockit", datetime.date(2030, 12, 31)
        )
        _ = comic.image_url  # Force parsing of HTML and reroute check


def test_invalid_date_error_message():
    """Test that InvalidDateError includes the expected message when date is out of range."""
    with pytest.raises(comics.exceptions.InvalidDateError) as excinfo:
        comics.search("calvinandhobbes", date="1800-01-01")
    assert "after" in str(excinfo.value) or "before" in str(excinfo.value)


def test_playwright_error_spoof(monkeypatch):
    """
    Force Playwright to fail for all browsers and assert ComicsPlaywrightError is raised.
    This patches `comics._gocomics.sync_playwright` to a context manager whose
    __enter__ returns an object with webkit, firefox and chromium attributes whose
    `launch` methods raise PlaywrightError.

    Args:
        monkeypatch (pytest.MonkeyPatch): Pytest monkeypatch fixture.
    """
    # Construct the fake sync_playwright context manager
    mock_sync = MagicMock()
    mock_playwright = MagicMock()
    # Make each browser's launch raise PlaywrightError
    mock_playwright.webkit.launch.side_effect = PlaywrightError("forced failure")
    mock_playwright.firefox.launch.side_effect = PlaywrightError("forced failure")
    mock_playwright.chromium.launch.side_effect = PlaywrightError("forced failure")
    mock_playwright.webkit.name = "webkit"
    mock_playwright.firefox.name = "firefox"
    mock_playwright.chromium.name = "chromium"
    # Context manager that returns mock_playwright
    mock_ctx = MagicMock()
    mock_ctx.__enter__.return_value = mock_playwright
    mock_sync.return_value = mock_ctx
    # Monkeypatch the real sync_playwright in the comics._gocomics module
    monkeypatch.setattr(comics._gocomics, "sync_playwright", mock_sync)

    # Create a ComicsAPI that forces playwright usage and assert the wrapped error
    comic = comics.search("foxtrot", date="2025-01-01", force_playwright=True)
    with pytest.raises(comics.exceptions.ComicsPlaywrightError):
        _ = comic.image_url


def test_playwright_failure_falls_back(monkeypatch):
    """
    Test that when Playwright fails and force_playwright is False, ComicsAPI falls back to requests.

    Args:
        monkeypatch (pytest.MonkeyPatch): Pytest monkeypatch fixture.
    """
    # Remove reliance on a real GoComics URL. Instead, patch _get_response_playwright to raise PlaywrightError,
    # and patch _get_response to return a fake response with an og:image meta tag.
    # Patch _get_response_playwright to always raise PlaywrightError
    monkeypatch.setattr(
        ComicsAPI,
        "_get_response_playwright",
        lambda self, url: (_ for _ in ()).throw(PlaywrightError("forced failure")),
    )

    # Patch _get_response to return a dummy response with og:image meta
    class DummyResp:
        def __init__(self):
            self.content = b"""
            <html>
              <head>
                <meta property="og:image" content="https://img.comic.com/fallback.png"/>
              </head>
              <body></body>
            </html>
            """

    monkeypatch.setattr(ComicsAPI, "_get_response", lambda self, url: DummyResp())

    # Use a stable endpoint; date is arbitrary since response is mocked
    comic = comics.search("calvinandhobbes", date="2020-01-01", force_playwright=False)
    url = comic.image_url
    assert url == "https://img.comic.com/fallback.png"
