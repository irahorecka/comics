"""
tests/test_exceptions
~~~~~~~~~~~~~~~~~~~~~
"""

import datetime
import os
from inspect import unwrap
from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest
import requests
from playwright.sync_api import Error as PlaywrightError, TimeoutError as PlaywrightTimeoutError

import comics
from comics._gocomics import ComicsAPI

_ci_skip = pytest.mark.skipif(
    os.getenv("CI") == "true", reason="GoComics blocks GitHub Actions IPs"
)


def test_invalid_endpoint():
    """
    Tests proper raise of InvalidEndpointError when using an endpoint that does
    not exist in GoComics.
    """
    with pytest.raises(comics.exceptions.InvalidEndpointError):
        comics.search("invalid_endpoint", date="2000-01-01")


@_ci_skip
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


@_ci_skip
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
    with pytest.raises(comics.exceptions.ComicsPlaywrightError) as excinfo:
        _ = comic.image_url
    # Ensure the wrapped error preserves the original Playwright message
    assert "forced failure" in str(excinfo.value)


def test_comics_playwright_error_str_uses_cause():
    """When raised without a message, ComicsPlaywrightError.__str__ falls back to the cause."""
    cause = PlaywrightError("inner cause message")
    try:
        raise comics.exceptions.ComicsPlaywrightError() from cause
    except comics.exceptions.ComicsPlaywrightError as e:
        assert "inner cause message" in str(e)


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


_URL = "https://www.gocomics.com/foo/2022/01/01"
_REAL_PAGE = (
    "<html><head><meta property='og:image' content='https://img.comic.com/strip.png'/></head>"
    "<body><script src='/.bunny-shield/bd/bunnyprint.js'></script></body></html>"
)
_CHALLENGE_PAGE = "<html><body data-pow='1#2'></body></html>"


def _comic():
    return ComicsAPI("foo", "Foo", datetime.date(2022, 1, 1))


def _requests_get(monkeypatch, status_code, text):
    response = SimpleNamespace(
        status_code=status_code,
        content=text.encode(),
        raise_for_status=lambda: None,
    )
    monkeypatch.setattr(comics._gocomics.requests, "get", lambda *args, **kwargs: response)


@pytest.mark.parametrize("status_code", [403, 429])
def test_requests_blocked_status_raises_blocked_error(monkeypatch, status_code):
    """GoComics answers a missing strip with HTTP 200, so 403 and 429 are never a missing date."""
    _requests_get(monkeypatch, status_code, "")
    with pytest.raises(comics.exceptions.ComicsBlockedError):
        _comic()._get_response(_URL)


def test_requests_challenge_page_raises_blocked_error(monkeypatch):
    _requests_get(monkeypatch, 200, _CHALLENGE_PAGE)
    with pytest.raises(comics.exceptions.ComicsBlockedError):
        _comic()._get_response(_URL)


def test_requests_real_page_with_bunny_shield_script_is_not_blocked(monkeypatch):
    _requests_get(monkeypatch, 200, _REAL_PAGE)
    assert _comic()._get_response(_URL).content == _REAL_PAGE.encode()


class _FakePage:
    """Playwright page stand-in. `challenge` is whether `data-pow` is set after `goto`."""

    def __init__(self, status, challenge, clears, html):
        self.status, self.challenge, self.clears, self.html = status, challenge, clears, html

    def goto(self, url, timeout):
        return SimpleNamespace(status=self.status)

    def evaluate(self, js):
        return "Mozilla/5.0 HeadlessChrome/140.0" if "userAgent" in js else self.challenge

    def wait_for_function(self, js, timeout):
        if not self.clears:
            raise PlaywrightTimeoutError("timeout")

    def wait_for_load_state(self, state):
        pass

    def content(self):
        return self.html

    def close(self):
        pass


def _fake_playwright(monkeypatch, **page_args):
    """Patches `sync_playwright` so every engine serves a `_FakePage(**page_args)`."""
    engines = {}
    for name in ("webkit", "firefox", "chromium"):
        browser = MagicMock()
        browser.new_page.return_value = _FakePage(**page_args)
        browser.new_context.return_value.new_page.return_value = _FakePage(**page_args)
        engines[name] = MagicMock(launch=MagicMock(return_value=browser))
        engines[name].name = name
    ctx = MagicMock()
    ctx.__enter__.return_value = SimpleNamespace(**engines)
    monkeypatch.setattr(comics._gocomics, "sync_playwright", MagicMock(return_value=ctx))
    return engines


def test_playwright_waits_for_challenge_served_with_403(monkeypatch):
    """BunnyCDN serves its proof-of-work challenge with HTTP 403, which must not end the wait."""
    _fake_playwright(monkeypatch, status=403, challenge=True, clears=True, html=_REAL_PAGE)
    resp = unwrap(ComicsAPI._get_response_playwright)(_comic(), _URL)
    assert resp.content == _REAL_PAGE.encode()


def test_playwright_unresolved_challenge_raises_blocked_error(monkeypatch):
    _fake_playwright(monkeypatch, status=403, challenge=True, clears=False, html=_CHALLENGE_PAGE)
    with pytest.raises(comics.exceptions.ComicsBlockedError):
        unwrap(ComicsAPI._get_response_playwright)(_comic(), _URL)


@pytest.mark.parametrize("status", [403, 429])
def test_playwright_blocked_status_raises_blocked_error(monkeypatch, status):
    _fake_playwright(monkeypatch, status=status, challenge=False, clears=True, html="")
    with pytest.raises(comics.exceptions.ComicsBlockedError):
        unwrap(ComicsAPI._get_response_playwright)(_comic(), _URL)


def test_playwright_chromium_does_not_announce_itself_as_headless(monkeypatch):
    engines = _fake_playwright(monkeypatch, status=200, challenge=False, clears=True, html="ok")
    engines["webkit"].launch.side_effect = PlaywrightError("not installed")
    engines["firefox"].launch.side_effect = PlaywrightError("not installed")
    unwrap(ComicsAPI._get_response_playwright)(_comic(), _URL)
    context = engines["chromium"].launch.return_value.new_context
    assert context.call_args.kwargs["user_agent"] == "Mozilla/5.0 Chrome/140.0"


def test_blocked_error_is_not_retried(monkeypatch):
    calls = []

    def blocked(self, url):
        calls.append(url)
        raise comics.exceptions.ComicsBlockedError("blocked")

    monkeypatch.setattr(ComicsAPI, "_get_response_playwright", blocked)
    monkeypatch.setattr(ComicsAPI, "_get_response", blocked)
    comic = comics.search("calvinandhobbes", date="2020-01-01")
    with pytest.raises(comics.exceptions.ComicsBlockedError):
        comic.image_url_with_retries(retries=5, base_delay=0)
    assert len(calls) == 2  # Playwright, then the requests fallback; no retries


def test_blocked_error_with_force_playwright_is_a_playwright_error(monkeypatch):
    def blocked(self, url):
        raise comics.exceptions.ComicsBlockedError("blocked")

    monkeypatch.setattr(ComicsAPI, "_get_response_playwright", blocked)
    comic = comics.search("calvinandhobbes", date="2020-01-01", force_playwright=True)
    with pytest.raises(comics.exceptions.ComicsPlaywrightError) as excinfo:
        comic.image_url
    assert isinstance(excinfo.value.__cause__, comics.exceptions.ComicsBlockedError)
