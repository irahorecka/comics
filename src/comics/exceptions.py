"""
comics/exceptions
~~~~~~~~~~~~~~~~~
"""


class InvalidDateError(Exception):
    """An invalid publication date was queried."""


class InvalidEndpointError(Exception):
    """An invalid GoComics endpoint was queried."""


class ComicsBlockedError(Exception):
    """GoComics' CDN blocked the request (HTTP 403 or 429, or an unresolved challenge)."""


class ComicsPlaywrightError(Exception):
    """An error occurred while making a request to the GoComics API using Playwright."""

    # Ensure str(e) is informative even when raised as `raise ComicsPlaywrightError from ex`.
    def __str__(self):
        msg = super().__str__()
        if msg:
            return msg
        cause = getattr(self, "__cause__", None)
        return str(cause) if cause else ""
