"""
comics/gocomics
~~~~~~~~~~~~~~~
"""

import contextlib
import os
import re
from datetime import datetime, timedelta
from functools import lru_cache, wraps
from inspect import unwrap
from io import BytesIO
from random import randint

import dateutil.parser
import requests
import urllib3
from bs4 import BeautifulSoup
from PIL import Image

from comics.constants import directory
from comics.exceptions import InvalidDateError

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
_BASE_URL = "https://www.gocomics.com"


def bypass_comics_cache(func):
    """Comics cache wrapper that checks and bypasses specific cached arguments."""

    @wraps(func)
    def wrapper(*args, **kwargs):
        """Checks and bypasses specific cached arguments for: 1. URL that starts with
        the base random URL pattern; 2. If the requested URL requires stream.

        Returns:
            requests.models.Response: Queried or cached response.
        """
        is_stream = kwargs.get("stream", False)
        # 1. Query URL if URL starts with the default random URL pattern
        # 2. Query URL if request requires stream
        return unwrap(func)(*args, **kwargs) if is_stream else func(*args, **kwargs)

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
            ComicsAPI: ComicsAPI instance of comic strip published on the provided date.
        """
        if isinstance(date, str):
            date = dateutil.parser.parse(date)
        # Convert date to date object
        date = date.date() if isinstance(date, datetime) else date

        # Step 1: Check if date is after the comic syndication date
        if date < datetime.strptime(self.start_date, "%Y-%m-%d").date():
            raise InvalidDateError(
                f"Search for dates after {self.start_date}. Your input: {datetime.strftime(date, '%Y-%m-%d')}"
            )
        # Step 2: Check if date is not in the future
        if date > datetime.today().date():
            raise InvalidDateError(
                f"Search for dates on or before {datetime.today().date()}. Your input: {datetime.strftime(date, '%Y-%m-%d')}"
            )

        return ComicsAPI(self.endpoint, self.title, date)

    def random_date(self, max_attempts=20):
        """Constructs user interface with GoComics with a random comic strip date.

        Returns:
            ComicsAPI: ComicsAPI instance of comic strip published on a random date.
        """
        # Get today's date and start date of comic strip
        today = datetime.today().date()
        start = datetime.strptime(self.start_date, "%Y-%m-%d").date()

        # Step 1: Try full-range random dates
        for _ in range(max_attempts):
            rand_days = randint(0, (today - start).days)
            date = start + timedelta(days=rand_days)
            try:
                # Attempt to get comic strip for random date
                potential_comic = self.date(date)
                if potential_comic.image_url:
                    return potential_comic
            except (InvalidDateError, requests.exceptions.HTTPError):
                continue

        # Step 2: Fallback to past year
        fallback_start = today - timedelta(days=365)
        tried_offsets = set()
        while len(tried_offsets) < 365:
            offset = randint(0, 364)
            if offset in tried_offsets:
                continue
            tried_offsets.add(offset)
            date = fallback_start + timedelta(days=offset)
            try:
                potential_comic = self.date(date)
                if potential_comic.image_url:
                    return potential_comic
            except (InvalidDateError, requests.exceptions.HTTPError):
                continue

        raise InvalidDateError("Could not find a valid comic after fallback attempts.")


class ComicsAPI:
    """User interface with GoComics."""

    def __init__(self, endpoint, title, date):
        self.endpoint = endpoint
        self.title = title
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
                with endpoint being the comic strip endpoint (e.g., Calvin and Hobbes -->
                calvinandhobbes). Defaults to None.
        """
        # Determine output path
        if path is None or os.path.isdir(path):
            path = os.path.join(path or os.getcwd(), f"{self.endpoint}.png")

        # Fetch the high-res image bytes
        response = self.stream()
        image = Image.open(BytesIO(response.content)).convert("RGB")
        image.save(path, format="PNG", quality=100)

    def show(self):
        """Shows comic strip in Jupyter notebook if available, otherwise opens in default image viewer."""
        image = Image.open(BytesIO(self.stream().content)).convert("RGB")
        image.show()
        with contextlib.suppress(ImportError, NameError):
            # Attempt to import the display function from IPython.display
            from IPython.display import display

            get_ipython  # This function is only available in an IPython environment
            # Conversion to RGB prevents conversion error if file is a static GIF
            display(image)

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
            str: Comic strip image URL.
        """
        # Get comic strip HTML
        r = self._get_response(self.url)
        comic_html = BeautifulSoup(r.content, "html.parser")

        # GoComics silently serves today's comic at future URLs if the comic hasn't been published yet.
        # This is a server-side reroute (not an HTTP redirect), so we can't detect it via response URL.
        # To catch this, we extract the displayed calendar date and compare it with the requested date.
        date_button = comic_html.find(
            "button", class_=lambda c: c and "ButtonCalendar_buttonCalendar" in c
        )
        if date_button:
            displayed_text = date_button.get_text(strip=True)  # e.g., "Fri, Apr 4"
            try:
                parsed = dateutil.parser.parse(displayed_text)
                displayed_date = parsed.date()
                # GoComics omits year in button display; infer it from context
                if (displayed_date.month, displayed_date.day) < (self._date.month, self._date.day):
                    displayed_date = displayed_date.replace(year=self._date.year - 1)
                else:
                    displayed_date = displayed_date.replace(year=self._date.year)
            except ValueError:
                displayed_date = None

            if displayed_date and displayed_date != self._date:
                raise InvalidDateError(
                    f"GoComics silently served the {displayed_date} strip instead of the requested {self.date}."
                )

        # Primary method: look for comic image in viewer container
        viewer_div = comic_html.find(
            "div", class_=lambda c: c and c.startswith("ComicViewer_comicViewer__comic")
        )
        if viewer_div:
            img_tag = viewer_div.find("img")
            src = img_tag.get("src") if img_tag else None
            if img_tag and src:
                # Always replace quality to 100 if present
                if "quality=" in src:
                    return re.sub(r"quality=\d+", "quality=100", src)
                return src

        # If all else fails, raise an error
        raise InvalidDateError(
            f'"{self.date}" is not a valid date for comic "{self.title}" or image could not be found.'
        )

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

    @bypass_comics_cache
    @lru_cache(maxsize=128)
    def _get_response(self, *args, **kwargs):
        """Gets response for queried GoComics URL.

        Args:
            args (tuple): Arguments for requests.get.
            kwargs (dict): Keyword arguments for requests.get.

        Returns:
            requests.models.Response: Response object for the queried URL.
        """
        # Define headers to accept webp images - highest quality
        headers = kwargs.pop("headers", {})
        headers.setdefault("Accept", "image/webp,image/apng,image/*,*/*;q=0.8")
        r = requests.get(*args, headers=headers, verify=False, timeout=10)
        try:
            r.raise_for_status()
        except requests.exceptions.HTTPError as e:
            raise InvalidDateError(f"Comic strip not found for {args[0]}") from e

        return r
