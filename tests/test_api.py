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
    (comics.calvin_and_hobbes, "Calvin and Hobbes", "2017-02-14", "https://www.gocomics.com/calvinandhobbes/2017/02/14"),
    (comics.dilbert, "Dilbert Classics", "2016-01-22", "https://www.gocomics.com/dilbert-classics/2016/01/22"),
    (comics.foxtrot, "FoxTrot", "1992-04-17", "https://www.gocomics.com/foxtrot/1992/04/17"),
    (comics.garfield, "Garfield", "2010-06-30", "https://www.gocomics.com/garfield/2010/06/30"),
    (comics.peanuts, "Peanuts", "1965-07-04", "https://www.gocomics.com/peanuts/1965/07/04"),
)
# fmt: on
@mark.parametrize("attributes", attributes)
def test_attributes(attributes):
    """Test proper instance attributes.

    Args:
        attributes (tuple): Args to unpack for testing proper instance attributes.
    """
    comics_obj, title, date, url = attributes
    comics_inst = comics_obj.date(date)
    assert comics_inst.title == title
    assert comics_inst.date == date
    assert comics_inst.url == url


def test_random_date():
    """Test random date instance is equal to date instance when using fixed date."""
    ch_random = comics.calvin_and_hobbes.random_date()
    random_date = ch_random.date
    ch_date = comics.calvin_and_hobbes.date(random_date)
    assert ch_random.date == ch_date.date
    assert ch_random.url == ch_date.url


def test_stream():
    """Test comic image stream instance."""
    ch = comics.calvin_and_hobbes.random_date()
    assert isinstance(ch.stream(), requests.models.Response)


def test_download_comic_and_verify_content():
    """Test proper comic download execution and valid download image content."""
    ch = comics.calvin_and_hobbes.random_date()
    _download_comic_and_verify_content(ch)


def test_download_static_gif_to_png():
    """Test proper comic download execution and valid download image content of static GIF
    to PNG."""
    bad_ch_date = "2009-09-10"
    ch = comics.calvin_and_hobbes.date(bad_ch_date)
    _download_comic_and_verify_content(ch)


def _download_comic_and_verify_content(comics_inst):
    """Private function. Verify proper download execution and valid download image content
    of a `Comics` instance.

    Args:
        comics_inst (Comics): `Comics` instance.
    """
    img_filepath = Path(__file__).parent / "downloads" / "comics_test.png"
    # Verify download method works
    comics_inst.download(img_filepath)
    # Raises `PIL.UnidentifiedImageError` if invalid image
    Image.open(img_filepath).verify()
    os.remove(img_filepath)
