"""
comics/constants
~~~~~~~~~~~~~~~~
"""

import json
from functools import wraps
from pathlib import Path

from comics.exceptions import InvalidEndpointError

FILE_PATH = Path(__file__).resolve().parent


def _read_json(filepath, **kwargs):
    """Reads and returns .json `filepath` as dictionary.

    Args:
        filepath (str | pathlib.Path): Filepath of JSON file to read.
        **kwargs (Any): Kwargs to pass to `json.load`.

    Returns:
        dict: Dictionary representation of JSON file as specified in `filepath`.
    """
    with open(filepath, "r") as f:
        data = json.load(f, **kwargs)
    return data


def _verify_endpoint(method):
    """Wrapper to verify existence of a GoComics endpoint stored in variable `endpoint`."""

    @wraps(method)
    def wrapper(*args, **kwargs):
        """Verifies user-specified GoComics endpoint is found in registered endpoints.

        Returns:
            Any: The method called with all arguments and keyword arguments.

        Raises:
            InvalidEndpointError: An invalid GoComics endpoint was queried.
        """
        try:
            return method(*args, **kwargs)
        except KeyError as e:
            # Relies on `endpoint` being the second argument of a class method if the value is not
            # bound to kwarg variable `endpoint`
            endpoint = kwargs.get("endpoint", args[1])
            raise InvalidEndpointError(f"'{endpoint}' is not a valid GoComics endpoint.") from e

    return wrapper


class directory:
    """Directory of registered comics in GoComics."""

    _registered_comics = _read_json(FILE_PATH / "endpoints.json")

    @classmethod
    def listall(cls):
        """Returns every registered comic in GoComics.

        Returns:
            tuple: Every registered comic in GoComics.
        """
        return tuple(sorted(cls._registered_comics.keys()))

    @classmethod
    def search(cls, key):
        """Searches directory of registered comics in GoComics for keyword.

        Args:
            key (str): Keyword to search directory for comic.

        Returns:
            tuple: Every registered comic in GoComics containing the queried keyword.
        """
        return tuple(
            endpoint
            for endpoint, content in cls._registered_comics.items()
            if key.lower() in content["title"].lower()
        )

    @classmethod
    @_verify_endpoint
    def get_title(cls, endpoint):
        """Gets the title of a registered comic endpoint in GoComics.

        Args:
            endpoint (str): GoComics endpoint to query.

        Returns:
            str: The GoComics endpoint's title.

        Raises:
            InvalidEndpointError: An invalid GoComics endpoint was queried.
        """
        endpoint_content = cls._registered_comics[endpoint.lower()]
        return endpoint_content["title"]

    @classmethod
    @_verify_endpoint
    def get_start_date(cls, endpoint):
        """Gets the publication start date of a registered comic endpoint in GoComics.

        Args:
            endpoint (str): GoComics endpoint to query.

        Returns:
            str: The GoComics endpoint's publication start date in format "%Y-%m-%d".

        Raises:
            InvalidEndpointError: An invalid GoComics endpoint was queried.
        """
        endpoint_content = cls._registered_comics[endpoint.lower()]
        return endpoint_content["start_date"]
