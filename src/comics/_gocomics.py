"""
comics/_gocomics
~~~~~~~~~~~~~~~~
"""

import contextlib
import json
import os
import time
from datetime import datetime, timedelta
from functools import lru_cache, wraps
from inspect import unwrap
from io import BytesIO
from random import randint
from unittest.mock import MagicMock
from playwright.sync_api import (
    sync_playwright,
    Error as PlaywrightError,
    TimeoutError as PlaywrightTimeoutError,
)

import dateutil.parser
import requests
from requests.models import Response
import urllib3
from bs4 import BeautifulSoup
from PIL import Image

from ._constants import directory
from .exceptions import ComicsPlaywrightError, InvalidDateError

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
_BASE_URL = "https://www.gocomics.com"


def bypass_comics_cache(func):
    """Comics cache wrapper that checks and bypasses specific cached arguments."""

    @wraps(func)
    def wrapper(*args, **kwargs):
        """
        Checks and bypasses specific cached arguments for: 1. URL that starts with
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
    """
    Constructs or dispatches user interface with GoComics.
    """

    def __new__(cls, endpoint, date, force_playwright=False):
        """
        Constructs or dispatches user interface with GoComics.

        Args:
            endpoint (str): Comic strip endpoint.
            date (datetime.datetime | str): Comic strip date, or 'random' for a random comic.
            force_playwright (bool): Whether to force using Playwright for fetching
                comic strip pages; defaults to requesting via `requests` if playwright
                is not installed. Defaults to False.

        Raises:
            InvalidDateError: If date is out of range for queried comic.

        Returns:
            search: Builder for dispatching user interface with GoComics.
        """
        # Initialize builder for dispatch
        builder = super().__new__(cls)
        # Set required attributes
        builder.endpoint = endpoint
        builder.start_date = directory.get_start_date(endpoint)
        builder.title = directory.get_title(endpoint)
        builder.force_playwright = force_playwright
        # Dispatch based on `date` argument
        if isinstance(date, str) and date.strip().lower() == "random":
            return builder.random_date()
        return builder.date(date)

    def __repr__(self):
        return f'search(endpoint="{self.endpoint}", title="{self.title}")'

    def date(self, date):
        """
        Constructs user interface with GoComics provided a comic strip date.

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

        return ComicsAPI(self.endpoint, self.title, date, self.force_playwright)

    def random_date(self, max_attempts=20):
        """
        Constructs user interface with GoComics with a random comic strip date.

        Args:
            max_attempts (int): Maximum number of attempts to find a valid comic strip.
                Defaults to 20.

        Raises:
            InvalidDateError: If no valid comic strip could be found after fallback attempts.

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

    def __init__(self, endpoint, title, date, force_playwright=False):
        self.endpoint = endpoint
        self.title = title
        self._date = date
        self._force_playwright = force_playwright

    def __repr__(self):
        return f'ComicsAPI(endpoint="{self.endpoint}", title="{self.title}", date="{self.date()}")'

    @property
    def date(self):
        """
        Returns string formatted comic strip date.

        Returns:
            str: String formatted comic strip date.
        """
        return datetime.strftime(self._date, "%Y-%m-%d")

    def download(self, path=None, retries=5, base_delay=0.5):
        """
        Downloads comic strip. Downloads as a PNG file if no image endpoint is specified.

        Args:
            path (pathlib.Path | str): Path to export file. If no path is specified,
                the comic will be exported to the current working directory as '{endpoint}.png',
                with endpoint being the comic strip endpoint (e.g., Calvin and Hobbes -->
                calvinandhobbes). Defaults to None.
            retries (int): Number of retries if image not found. Defaults to 5.
            base_delay (float): Base delay between retries. Defaults to 0.5 seconds.

        Raises:
            InvalidDateError: If no image URL could be found after retries.
        """
        # If path is None or directory, set default path to current working directory
        if path is None or os.path.isdir(path):
            path = os.path.join(path or os.getcwd(), f"{self.endpoint}.png")

        response = self.stream(retries=retries, base_delay=base_delay)
        image = Image.open(BytesIO(response.content)).convert("RGB")
        image.save(path, format="PNG", quality=100)

    def show(self, retries=5, base_delay=0.5):
        """
        Shows comic strip in Jupyter notebook if available, otherwise opens in default image viewer.

        Args:
            retries (int): Number of retries if image not found. Defaults to 5.
            base_delay (float): Base delay between retries. Defaults to 0.5 seconds.

        Raises:
            InvalidDateError: If no image URL could be found after retries.
        """
        # Open the image in the default viewer if not in Jupyter notebook
        image = Image.open(
            BytesIO(self.stream(retries=retries, base_delay=base_delay).content)
        ).convert("RGB")
        image.show()
        # Else, display the image in Jupyter notebook if available
        with contextlib.suppress(ImportError, NameError):
            from IPython.display import display

            get_ipython
            display(image)

    def stream(self, retries=5, base_delay=0.5):
        """
        Streams comic strip response.

        Args:
            retries (int): Number of retries if image not found. Defaults to 5.
            base_delay (float): Base delay between retries. Defaults to 0.5 seconds.

        Raises:
            InvalidDateError: If no image URL could be found after retries.

        Returns:
            requests.models.Response: Streamed comic strip response.
        """
        # note: we don't need playwright to get image streams; which is good
        # because playwright doesn't let us get the raw bytes of the page anyways.
        return self._get_response(self.image_url_with_retries(retries, base_delay), stream=True)

    @property
    def image_url(self):
        """
        Returns comic strip image URL. Fetches page using Playwright first, then falls back to requests
        if Playwright is not forced; otherwise, raises PlaywrightError.

        Raises:
            ComicsPlaywrightError: If no image URL could be found for the requested date.

        Returns:
            str: Comic strip image URL.
        """
        try:
            r = self._get_response_playwright(self.url)
        except PlaywrightError as ex:
            if self._force_playwright is True:
                raise ComicsPlaywrightError from ex
            else:
                r = self._get_response(self.url)

        return self._extract_image_url_from_response(r)

    def image_url_with_retries(self, retries=5, base_delay=0.5):
        """
        Retry wrapper for image_url property.

        Args:
            retries (int): Number of retries if image not found. Defaults to 5.
            base_delay (float): Base delay between retries. Defaults to 0.5 seconds.

        Raises:
            InvalidDateError: If no image URL could be found after retries.
            ComicsPlaywrightError: If no image URL could be found for the requested date.

        Returns:
            str: Comic strip image URL.
        """
        # Retry logic for image_url property
        for i in range(retries + 1):
            try:
                if i == 0:
                    return self.image_url
                else:
                    try:
                        r = unwrap(type(self)._get_response_playwright)(self, self.url)
                    except PlaywrightError as ex:
                        if self._force_playwright is True:
                            raise ComicsPlaywrightError from ex
                        else:
                            r = unwrap(type(self)._get_response)(self, self.url)
                    return self._extract_image_url_from_response(r)
            # Handle specific InvalidDateError to retry
            except InvalidDateError:
                if i < retries:
                    time.sleep(base_delay * (2**i))
                else:
                    raise InvalidDateError(
                        f"Could not find image URL for {self.date} after {retries} retries."
                    )

    def _extract_image_url_from_response(self, r):
        """
        Extracts comic strip image URL from the response.

        Args:
            r (requests.models.Response): Response object from GoComics.

        Raises:
            InvalidDateError: If no image URL could be found for the requested date.

        Returns:
            str: Comic strip image URL.
        """
        # Get the HTML content of the comic strip page
        comic_html = BeautifulSoup(r.content, "html.parser")

        # GoComics silently serves today's comic at future URLs if the comic hasn't been published yet.
        # This is a server-side reroute (not an HTTP redirect), so we can't detect it via response URL.
        # To catch this, we extract the displayed calendar date and compare it with the requested date.
        date_button = comic_html.find(
            "button", class_=lambda c: c and "ButtonCalendar_buttonCalendar" in c
        )
        # If the date button is not found, it means the comic strip is not available for the requested date
        if date_button:
            displayed_text = date_button.get_text(strip=True)
            try:
                parsed = dateutil.parser.parse(displayed_text)
                displayed_date = parsed.date()
                if (displayed_date.month, displayed_date.day) < (
                    self._date.month,
                    self._date.day,
                ):
                    displayed_date = displayed_date.replace(year=self._date.year - 1)
                else:
                    displayed_date = displayed_date.replace(year=self._date.year)
            except ValueError:
                displayed_date = None

            if displayed_date and displayed_date != self._date:
                raise InvalidDateError(
                    f"GoComics silently served the {displayed_date} strip instead of the requested {self.date}."
                )

        # First, try extracting the image URL from the og:image property
        meta = comic_html.find("meta", property="og:image")
        if meta:
            return meta["content"]

        # If not found, try extracting image URL from ld+json script tag within the correct container
        viewer_div = comic_html.find(
            "div",
            class_=lambda c: c and c.startswith("ShowComicViewer_showComicViewer__comic"),
        )
        if viewer_div:
            script_tag = viewer_div.find("script", type="application/ld+json")
            if script_tag:
                with contextlib.suppress(json.JSONDecodeError):
                    json_data = json.loads(script_tag.string.strip())
                    src = json_data.get("contentUrl")
                    if src:
                        return src

        # If all else fails, raise an error
        raise InvalidDateError(
            f'"{self.date}" is not a valid date for comic "{self.title}" or image could not be found.'
        )

    @property
    def url(self):
        """
        Constructs GoComics URL with date.

        Returns:
            str: GoComics URL with date.
        """
        strf_datetime = datetime.strftime(self._date, "%Y/%m/%d")
        return f"{_BASE_URL}/{self.endpoint}/{strf_datetime}"

    @bypass_comics_cache
    @lru_cache(maxsize=128)
    def _get_response_playwright(self, url):
        """
        Gets response for queried GoComics URL (using PlayWright).

        Args:
            url (str): Argument for page.goto.

        Raises:
            PlaywrightError: If Playwright encounters an error or the page is not found.

        Returns:
            requests.models.Response: Response object for the queried URL.
        """
        with sync_playwright() as p:
            # Try any of the following browsers. If one of them succeeds, go ahead, if not then ignore the result.
            browsers = [p.webkit, p.firefox, p.chromium]
            for browser in browsers:
                try:
                    launched_browser = browser.launch()
                    page = launched_browser.new_page()
                    r = page.goto(url)
                    if r is not None:
                        if r.status >= 400 and r.status < 600:
                            print(f"HTTP error {r.status} for {url} with {browser.name}")
                            continue
                        st = page.content()
                        launched_browser.close()
                        resp = Response()
                        resp = MagicMock(spec=Response)
                        resp.status_code = 400
                        resp.text = st
                        resp.content = str.encode(st)
                        return resp
                except (PlaywrightError, PlaywrightTimeoutError) as ex:
                    print(f"Playwright error with {browser.name}: {ex}")

            raise PlaywrightError(
                f"Playwright failed to launch on {', '.join([b.name for b in browsers])}.\nMake sure Playwright is installed and set up correctly."
            )

    @bypass_comics_cache
    @lru_cache(maxsize=128)
    def _get_response(self, *args, **kwargs):
        """
        Gets response for queried URL (using requests).

        Args:
            args (tuple): Arguments for requests.get.
            kwargs (dict): Keyword arguments for requests.get.

        Raises:
            InvalidDateError: If the comic strip is not found for the queried date.

        Returns:
            requests.models.Response: Response object for the queried URL.
        """
        headers = kwargs.pop("headers", {})
        headers.setdefault("Accept", "image/webp,image/apng,image/*,*/*;q=0.8")
        r = requests.get(*args, headers=headers, verify=False, timeout=10)
        try:
            r.raise_for_status()
        except requests.exceptions.HTTPError as e:
            raise InvalidDateError(f"Comic strip not found for {args[0]}") from e

        return r
