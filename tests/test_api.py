"""
tests/test_api
~~~~~~~~~~~~~~
"""

import warnings
from datetime import datetime, timedelta
from pathlib import Path

import pytest
import requests
from PIL import Image
from pytest import mark

import comics
from comics._gocomics import bypass_comics_cache, ComicsAPI

# 2025-06-05: Intermittend failures on fetching images from GoComics even with retries
# Re-run flaky tests up to 4 times with a delay of 2 seconds between attempts
pytestmark = pytest.mark.flaky(reruns=4, reruns_delay=2)


def test_search_requires_date():
    """Test that search requires a date argument."""
    # Calling without a date argument is now a TypeError
    with pytest.raises(TypeError):
        comics.search("peanuts")


def test_search_with_valid_date_returns_comics_api():
    """Test that search with a valid date returns a ComicsAPI instance."""
    inst = comics.search("peanuts", date="1965-07-04")
    assert isinstance(inst, comics._gocomics.ComicsAPI)
    assert inst.title == "Peanuts"
    assert inst.date == "1965-07-04"


def test_search_with_invalid_date_before_start():
    """Test that search with an invalid date before the start date raises an error."""
    # Pick a date earlier than the comic's start date --> InvalidDateError
    start = comics._constants.directory.get_start_date("peanuts")
    before = (datetime.strptime(start, "%Y-%m-%d") - timedelta(days=1)).strftime("%Y-%m-%d")
    with pytest.raises(comics.exceptions.InvalidDateError):
        comics.search("peanuts", date=before)


def test_search_with_invalid_date_in_future():
    """Test that search with an invalid date in the future raises an error."""
    future = (datetime.today().date() + timedelta(days=1)).strftime("%Y-%m-%d")
    with pytest.raises(comics.exceptions.InvalidDateError):
        comics.search("peanuts", date=future)


def test_search_random_returns_comics_api_within_range():
    """Test that search with 'random' returns a ComicsAPI instance with a valid date."""
    inst = comics.search("peanuts", date="random")
    assert isinstance(inst, comics._gocomics.ComicsAPI)
    # Ensure returned date falls between start_date and today
    dt = datetime.strptime(inst.date, "%Y-%m-%d").date()
    start = datetime.strptime(
        comics._constants.directory.get_start_date("peanuts"), "%Y-%m-%d"
    ).date()
    today = datetime.today().date()
    assert start <= dt <= today


# fmt: off
attributes = (
    ("calvinandhobbes", "Calvin and Hobbes", "2017-02-14", "https://www.gocomics.com/calvinandhobbes/2017/02/14"),
    ("jim-benton-cartoons", "Jim Benton Cartoons", "2020-05-10", "https://www.gocomics.com/jim-benton-cartoons/2020/05/10"),
    ("foxtrot", "FoxTrot", "1992-04-17", "https://www.gocomics.com/foxtrot/1992/04/17"),
    ("garfield", "Garfield", "2010-06-30", "https://www.gocomics.com/garfield/2010/06/30"),
    ("peanuts", "Peanuts", "1965-07-04", "https://www.gocomics.com/peanuts/1965/07/04"),
)
# fmt: on
@mark.parametrize("attr", attributes)
def test_attributes(attr):
    """
    Test proper instance attributes.

    Args:
        attr (tuple): Args to unpack for testing proper instance attributes.
    """
    endpoint, title, date, url = attr
    comics_inst = comics.search(endpoint, date=date)
    assert comics_inst.title == title
    assert comics_inst.date == date
    assert comics_inst.url == url
    img_url = comics_inst.image_url_with_retries(retries=5, base_delay=0.5)
    assert requests.head(img_url, timeout=10).headers.get("content-type", "").startswith("image/")


def test_stream():
    """Test comic image stream instance and status code."""
    ch = comics.search("calvinandhobbes", date="random")
    assert isinstance(ch.stream(), requests.models.Response)
    assert ch.stream().status_code == 200


def test_download_comic_by_random_and_verify_random_content():
    """Test proper random comic download execution and valid download image content."""
    ch = comics.search("calvinandhobbes", date="random")
    _download_comic_and_verify_content(ch)


def test_download_comic_by_date_and_verify_content():
    """Test proper comic download execution and valid download image content."""
    ch = comics.search("calvinandhobbes", date="2025-04-03")
    _download_comic_and_verify_content(ch)


def test_download_static_gif_to_png():
    """
    Test proper comic download execution and valid download image content of static GIF
    to PNG.
    """
    bad_ch_date = "2009-09-10"
    ch = comics.search("calvinandhobbes", date=bad_ch_date)
    _download_comic_and_verify_content(ch)


def _download_comic_and_verify_content(comics_inst):
    """
    Private function. Verify proper download execution and valid download image content
    of a ComicsAPI instance.

    Args:
        comics_inst (ComicsAPI): ComicsAPI instance.
    """
    img_filepath = Path(__file__).parent / "downloads" / "comics_test.png"
    comics_inst.download(img_filepath)
    Image.open(img_filepath).verify()


@mark.parametrize("attr", attributes)
def test_direct_date_api_no_warning(attr):
    """
    Test direct date API call without DeprecationWarning.

    Args:
        attr (tuple): Args to unpack for testing direct date API call.
    """
    endpoint, title, date, url = attr
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        inst = comics.search(endpoint, date=date)
        # No DeprecationWarning should be raised
        assert not any(item.category is DeprecationWarning for item in w)
    assert inst.title == title
    assert inst.date == date


def test_direct_random_api_no_warning():
    """Test direct random API call without DeprecationWarning."""
    endpoint = "calvinandhobbes"
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        inst = comics.search(endpoint, date="random")
        assert not any(item.category is DeprecationWarning for item in w)
    # Should return a ComicsAPI with a valid date
    assert hasattr(inst, "date")
    assert isinstance(inst.date, str)
    # Should return a title as well
    assert hasattr(inst, "title")
    assert isinstance(inst.title, str)
    assert len(inst.date) == 10  # Expecting 'YYYY-MM-DD'
    # Optionally check date format

    try:
        datetime.strptime(inst.date, "%Y-%m-%d")
    except ValueError:
        assert False, f"Returned date {inst.date} is not a valid date string"


def test_image_url_with_retries_robustness():
    """Ensure image_url_with_retries does not raise immediately and returns a valid image URL."""
    ch = comics.search("jim-benton-cartoons", date="2020-05-10")
    url = ch.image_url_with_retries(retries=3, base_delay=0.5)
    head = requests.head(url, timeout=10)
    assert head.status_code == 200
    assert head.headers.get("content-type", "").startswith("image/")


def test_bypass_comics_cache(monkeypatch):
    """
    Test that bypass_comics_cache decorator bypasses cache for stream=True.
    """
    called = {}

    def dummy_func(*args, **kwargs):
        called["called"] = True
        return "streamed"

    wrapped = bypass_comics_cache(dummy_func)
    # Should call the original function if stream=True
    result = wrapped("foo", stream=True)
    assert called.get("called")
    assert result == "streamed"


def test_comicsapi_url_property():
    """
    Test ComicsAPI.url property returns correct URL.
    """
    date = datetime(2022, 5, 4).date()
    api = ComicsAPI("calvinandhobbes", "Calvin and Hobbes", date)
    expected_url = "https://www.gocomics.com/calvinandhobbes/2022/05/04"
    assert api.url == expected_url


def test_extract_image_url_from_meta():
    """
    Test ComicsAPI._extract_image_url_from_response extracts og:image meta.
    """

    class DummyResp:
        def __init__(self, html):
            self.content = html.encode("utf-8")

    # HTML with og:image meta
    html = """
    <html>
      <head>
        <meta property="og:image" content="https://img.comic.com/strip.png"/>
      </head>
      <body></body>
    </html>
    """
    api = ComicsAPI("foo", "Foo", datetime(2022, 1, 1).date())
    url = api._extract_image_url_from_response(DummyResp(html))
    assert url == "https://img.comic.com/strip.png"
