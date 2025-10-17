"""
comics/exceptions
~~~~~~~~~~~~~~~~~
"""


class InvalidDateError(Exception):
    """An invalid publication date was queried."""


class InvalidEndpointError(Exception):
    """An invalid GoComics endpoint was queried."""


class PlaywrightNotInstalledError(Exception):
    """Playwright was not installed. Run `playright install` to install."""
