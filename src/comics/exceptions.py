"""
comics/exceptions
~~~~~~~~~~~~~~~~~
"""


class InvalidDateError(Exception):
    """An invalid publication date was queried."""


class InvalidEndpointError(Exception):
    """An invalid GoComics endpoint was queried."""


class ComicsPlaywrightError(Exception):
    """An error occurred while making a request to the GoComics API using Playwright."""
