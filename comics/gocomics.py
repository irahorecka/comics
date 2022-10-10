"""
comics/gocomics.py
~~~~~~~~~~~~~~~~~~
"""

import os
import shutil
from datetime import datetime
from io import BytesIO

import dateutil.parser
import requests
from bs4 import BeautifulSoup
from PIL import Image


class DateError(Exception):
    """An invalid publication date was queried."""


class GoComicsAPI:
    title = "NULL"
    start_date = datetime.today()
    _endpoint = "NULL"

    @classmethod
    def search_date(cls, date):
        if isinstance(date, str):
            date = dateutil.parser.parse(date)
        if date < cls.start_date:
            date_strf = datetime.strftime(date, "%Y-%m-%d")
            start_date_strf = datetime.strftime(cls.start_date, "%Y-%m-%d")
            raise DateError(f"Search for dates after {start_date_strf}. Your input: {date_strf}")
        return GoComics(cls.title, cls._endpoint, date)

    @classmethod
    def random_date(cls):
        return GoComics(cls.title, cls._endpoint)


class GoComics:
    def __init__(self, title, endpoint, date=None):
        self.title = title
        self.endpoint = endpoint
        # Select a random comic strip if date is not specified
        if date is None:
            self.url = self._get_random_url()
            self._date = datetime(1900, 1, 1)
        else:
            self.url = self._get_date_url(date)
            self._date = date

    @property
    def date(self):
        return datetime.strftime(self._date, "%Y-%m-%d")

    def download(self, path=None):
        path = os.getcwd() if path is None else str(path)
        if os.path.isdir(path):
            path = os.path.join(path, f"{self.endpoint}.png")
        # Stream outside of context - will corrupt image if exception raised in opened file
        stream = self.stream()
        with open(path, "wb") as file:
            shutil.copyfileobj(stream.raw, file)

    def show(self):
        Image.open(BytesIO(self.stream().content)).show()

    def stream(self):
        # Must be called for every image request
        return self._get_response(self._get_strip_url(), stream=True)

    def _get_date_url(self, date):
        strf_datetime = datetime.strftime(date, "%Y/%m/%d")
        return f"https://www.gocomics.com/{self.endpoint}/{strf_datetime}"

    def _get_random_url(self):
        return f"https://www.gocomics.com/random/{self.endpoint}"

    def _get_strip_url(self):
        r = self._get_response(self.url)
        self._date = dateutil.parser.parse("-".join(r.url.split("/")[-3:]))
        # Set new URL soon as a date is found to allow multiple URL use
        if self.url == self._get_random_url():
            self.url = self._get_date_url(self._date)
        strip_site_text = r.text
        strip_site = BeautifulSoup(strip_site_text, "html.parser")
        strip_img = strip_site.find("div", {"class": "comic__image"})
        try:
            return (
                strip_img.find("picture", {"class": "item-comic-image"})
                .find("img")["data-srcset"]
                .split(" ")
                .pop(0)
            )
        except AttributeError as e:
            raise DateError(f'{self.date} is not a valid date for comic "{self.title}"') from e

    @staticmethod
    def _get_response(*args, **kwargs):
        response = requests.get(*args, **kwargs)
        response.raise_for_status()
        return response
