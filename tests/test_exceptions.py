"""
tests/test_exceptions
~~~~~~~~~~~~~~~~~~~~~
"""

import pytest

import comics
from comics import DateError


def test_date_before_creation():
    """Tests proper raise of `DateError` when using date that is before the
    comic's creation date."""
    with pytest.raises(DateError):
        comics.calvin_and_hobbes.date("1900-01-01")


def test_unregistered_date():
    """Tests proper raise of `DateError` when using an unregistered date for
    the comic of interest."""
    ch = comics.calvin_and_hobbes.date("2050-01-01")
    with pytest.raises(DateError):
        ch.show()
