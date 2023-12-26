"""
tests/test_api
~~~~~~~~~~~~~~
"""

import os
from pathlib import Path

import requests
from pytest import mark
from PIL import Image

import comics


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
    """Test proper instance attributes.

    Args:
        attr (tuple): Args to unpack for testing proper instance attributes.
    """
    endpoint, title, date, url = attr
    comics_inst = comics.search(endpoint).date(date)
    assert comics_inst.title == title
    assert comics_inst.date == date
    assert comics_inst.url == url
    # Check if comic strip URL content is an image
    assert requests.head(comics_inst.image_url).headers.get("content-type", "").startswith("image/")


def test_random_date():
    """Test random date instance is equal to date instance when using fixed date."""
    ch_random = comics.search("calvinandhobbes").random_date()
    random_date = ch_random.date
    ch_date = comics.search("calvinandhobbes").date(random_date)
    assert ch_random.date == ch_date.date
    assert ch_random.url == ch_date.url


def test_stream():
    """Test comic image stream instance and status code."""
    ch = comics.search("calvinandhobbes").random_date()
    assert isinstance(ch.stream(), requests.models.Response)
    assert ch.stream().status_code == 200


def test_download_comic_and_verify_content():
    """Test proper comic download execution and valid download image content."""
    ch = comics.search("calvinandhobbes").random_date()
    _download_comic_and_verify_content(ch)


def test_download_static_gif_to_png():
    """Test proper comic download execution and valid download image content of static GIF
    to PNG."""
    bad_ch_date = "2009-09-10"
    ch = comics.search("calvinandhobbes").date(bad_ch_date)
    _download_comic_and_verify_content(ch)


def _download_comic_and_verify_content(comics_inst):
    """Private function. Verify proper download execution and valid download image content
    of a `ComicsAPI` instance.

    Args:
        comics_inst (ComicsAPI): `ComicsAPI` instance.
    """
    img_filepath = Path(__file__).parent / "downloads" / "comics_test.png"
    # Start by deleting the image if present - this allows me to keep the file tracked in Git to enable
    # GitHub Actions testing
    os.remove(img_filepath)
    # Verify download method works
    comics_inst.download(img_filepath)
    # Raises `PIL.UnidentifiedImageError` if invalid image
    Image.open(img_filepath).verify()
