"""
tests/test_exceptions
~~~~~~~~~~~~~~~~~~~~~
"""

import pytest

import comics
from comics import InvalidDateError, InvalidEndpointError


def test_invalid_endpoint():
    """Tests proper raise of `InvalidEndpointError` when using an endpoint that does
    not exist in GoComics."""
    with pytest.raises(InvalidEndpointError):
        comics.search("invalid_endpoint").date("2000-01-01")


def test_comic_not_found():
    """Tests proper raise of `InvalidDateError` when using a date that does not exist
    for the queried comic."""
    with pytest.raises(InvalidDateError):
        invalid_foxtrot = comics.search("foxtrot").date(
            "2025-04-03"
        )  # Known to be a non-existent date for Foxtrot
        invalid_foxtrot.image_url


def test_date_before_creation():
    """Tests proper raise of `InvalidDateError` when using date that is before the
    comic's creation date."""
    with pytest.raises(InvalidDateError):
        comics.search("calvinandhobbes").date("1900-01-01")


def test_invalid_future_date():
    """Tests proper raise of `InvalidDateError` when using date that is in the future."""
    with pytest.raises(InvalidDateError):
        comics.search("calvinandhobbes").date("2050-01-01")
