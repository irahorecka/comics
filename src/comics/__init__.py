"""
comics
~~~~~~
"""

from . import exceptions
from ._constants import directory
from ._gocomics import search

__all__ = ["directory", "exceptions", "search"]
__version__ = "0.9.0"
