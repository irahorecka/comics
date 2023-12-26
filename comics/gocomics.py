"""
comics/gocomics
~~~~~~~~~~~~~~~
"""

import os
import shutil
import urllib3
from datetime import datetime
from functools import lru_cache, wraps
from inspect import unwrap
from io import BytesIO

import dateutil.parser
import requests
from bs4 import BeautifulSoup
from PIL import Image

from comics.constants import directory
from comics.exceptions import InvalidDateError

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
_BASE_URL = "https://www.gocomics.com"
_BASE_RANDOM_URL = "https://www.gocomics.com/random"


def bypass_comics_cache(func):
    """Comics cache wrapper that checks and bypasses specific cached arguments."""

    @wraps(func)
    def wrapper(*args, **kwargs):
        """Checks and bypasses specific cached arguments for: 1. URL that starts with
        the base random URL pattern; 2. If the requested URL requires stream.

        Returns:
            requests.models.Response: Queried or cached response.
        """
        url = args[0]
        is_stream = kwargs.get("stream", False)
        # 1. Query URL if URL starts with the default random URL pattern
        # 2. Query URL if request requires stream
        return (
            unwrap(func)(*args, **kwargs)
            if url.startswith(_BASE_RANDOM_URL) or is_stream
            else func(*args, **kwargs)
        )

    return wrapper


class search:
    """Constructs user interface with GoComics."""

    def __init__(self, endpoint):
        self.endpoint = endpoint
        self.start_date = directory.get_start_date(self.endpoint)
        self.title = directory.get_title(self.endpoint)

    def __repr__(self):
        return f'search(endpoint="{self.endpoint}", title="{self.title}")'

    def date(self, date):
        """Constructs user interface with GoComics provided a comic strip date.

        Args:
            date (datetime.datetime | str): Comic strip date.

        Raises:
            InvalidDateError: If date is out of range for queried comic.

        Returns:
            ComicsAPI: `ComicsAPI` instance of comic strip published on the provided date.
        """
        if isinstance(date, str):
            date = dateutil.parser.parse(date)
        if date < datetime.strptime(self.start_date, "%Y-%m-%d"):
            raise InvalidDateError(
                f"Search for dates after {self.start_date}. Your input: {datetime.strftime(date, '%Y-%m-%d')}"
            )
        return ComicsAPI(self.endpoint, self.title, date)

    def random_date(self):
        """Constructs user interface with GoComics with a random comic strip date.

        Returns:
            ComicsAPI: `ComicsAPI` instance of comic strip published on a random date.
        """
        return ComicsAPI(self.endpoint, self.title)


class ComicsAPI:
    """User interface with GoComics."""

    def __init__(self, endpoint, title, date=None):
        self.endpoint = endpoint
        self.title = title
        # Select a random comic strip if date is not specified
        if date is None:
            r = self._get_response(self._random_url)
            # Set date as date of random comic strip
            self._date = dateutil.parser.parse("-".join(r.url.split("/")[-3:]))
        else:
            self._date = date

    def __repr__(self):
        return f'ComicsAPI(endpoint="{self.endpoint}", title="{self.title}", date="{self.date}")'

    @property
    def date(self):
        """Returns string formatted comic strip date.

        Returns:
            str: String formatted comic strip date.
        """
        return datetime.strftime(self._date, "%Y-%m-%d")

    def download(self, path=None):
        """Downloads comic strip. Downloads as a PNG file if no image endpoint is specified.

        Args:
            path (pathlib.Path | str, optional): Path to export file. If no path is specified,
                the comic will be exported to the current working directory as '{endpoint}.png',
                with `endpoint` being the comic strip endpoint (e.g., Calvin and Hobbes -->
                calvinandhobbes). Defaults to None.
        """
        path = os.getcwd() if path is None else str(path)
        if os.path.isdir(path):
            path = os.path.join(path, f"{self.endpoint}.png")
        # Stream outside of context - will corrupt image if exception raised in opened file
        stream = self.stream()
        with open(path, "wb") as file:
            shutil.copyfileobj(stream.raw, file)

    def show(self):
        """Shows comic strip."""
        # Conversion to RGB prevents conversion error if file is a static GIF
        Image.open(BytesIO(self.stream().content)).convert("RGB").show()

    def stream(self):
        """Streams comic strip response.

        Returns:
            requests.models.Response: Streamed comic strip response.
        """
        # Must be called for every image request
        return self._get_response(self.image_url, stream=True)

    @property
    def image_url(self):
        """Gets comic strip image URL from GoComics.

        Raises:
            InvalidDateError: If date is invalid for queried comic.

        Returns:
            str: Comic strip URL.
        """
        r = self._get_response(self.url)
        comic_html = BeautifulSoup(r.content, "html.parser")
        comic_img = comic_html.find("div", {"class": "comic__image"})
        try:
            return (
                comic_img.find("picture", {"class": "item-comic-image"})
                .find("img")["data-srcset"]
                .split(" ")
                .pop(0)
            )
        except AttributeError as e:
            raise InvalidDateError(
                f'"{self.date}" is not a valid date for comic "{self.title}"'
            ) from e

    @property
    def url(self):
        """Constructs GoComics URL with date.

        Args:
            date (datetime.datetime): Date to query.

        Returns:
            str: GoComics URL with date.
        """
        strf_datetime = datetime.strftime(self._date, "%Y/%m/%d")
        return f"{_BASE_URL}/{self.endpoint}/{strf_datetime}"

    @property
    def _random_url(self):
        """Constructs random GoComics URL.

        Returns:
            str: Random GoComics URL.
        """
        return f"{_BASE_RANDOM_URL}/{self.endpoint}"

    @staticmethod
    @bypass_comics_cache
    @lru_cache(maxsize=128)
    def _get_response(*args, **kwargs):
        """Gets response for queried URL.

        Returns:
            requests.models.Response: Queried URL response.
        """
        r = requests.get(*args, **kwargs, verify=False)
        r.raise_for_status()
        return r
