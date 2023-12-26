"""
comics/exceptions
~~~~~~~~~~~~~~~~~
"""


class InvalidDateError(Exception):
    """An invalid publication date was queried."""


class InvalidEndpointError(Exception):
    """An invalid GoComics endpoint was queried."""
