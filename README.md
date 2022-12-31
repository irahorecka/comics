# comics

[GoComics](https://www.gocomics.com/) API wrapper

[![pypiv](https://img.shields.io/pypi/v/comics.svg)](https://pypi.python.org/pypi/comics)
[![Python 3.7+](https://img.shields.io/badge/python-3.7+-blue.svg)](https://www.python.org/downloads/)
[![continuous-integration](https://github.com/irahorecka/jupyterblack/workflows/continuous-integration/badge.svg?branch=master)](https://github.com/irahorecka/comics/actions)
[![Licence](https://img.shields.io/badge/license-MIT-blue.svg)](https://raw.githubusercontent.com/irahorecka/jupyterblack/master/LICENSE)

## Installation

```bash
pip install comics
```

## Quick Start

Find and download the Calvin and Hobbes comic strip published on January 2, 1990:

```python
import comics

ch = comics.calvin_and_hobbes.date('January 2, 1990')
ch.download('calvinandhobbes.png')
```

<div align="center">
    <img src="docs/calvinandhobbes.png">
</div>

## Find comics

Comics can be found using the `directory` class:

```python
import comics

# List available comics - total of 474
comics.directory.listall()

# Find your favorite comic
comics.directory.search("Dilbert")

>>> ("dilbert", "dilbert_en_espanol")
```

Use the desired endpoint to query your comic. For example, to search for Dilbert comics in english use `comics.dilbert`; for spanish, use `comics.dilbert_en_espanol`.

## Search and download comics

Instantiate your query class with a date argument or use the random date constructor:

```python
import comics

dilbert = comics.dilbert.date("2013-05-13")  # Also accepts datetime object
random_dilbert = comics.dilbert.random_date()
```

Once instantiated, show, download, or stream the comic strip:

```python
# Show comic - opens default image viewer application
dilbert.show()
# Download comic - defaults to {comic endpoint}.png if an export path is not provided. E.g., a Dilbert comic strip will be exported as "dilbert.png" in the current working directory
dilbert.download()
# Stream comic - useful if custom image content manipulation is desired
dilbert.stream()
```

## Attributes

Every instantiated query class will have the following public attributes:

```python
import comics

garfield = comics.garfield.date("08/20/2000")
garfield.date  # "2000-08-20"
garfield.title  # "Garfield"
garfield.url  # "https://www.gocomics.com/garfield/2000/08/20"
```

## Exceptions

An exception will be thrown if the query date is unregistered or before the comic's origin date. Catch this exception as follows:

```python
import comics
from comics import DateError

try:
    peanuts = comics.peanuts.date("1900-01-01")
    peanuts.download()
except DateError:
    print("Whoops - an invalid date was queried.")
```

## Contribute

- [Issue Tracker](https://github.com/irahorecka/comics/issues)
- [Source Code](https://github.com/irahorecka/comics/tree/master/comics)

## Support

If you are having issues or would like to propose a new feature, please use the [issues tracker](https://github.com/irahorecka/comics/issues).

<div align="center">
    <img src="docs/dilbert.png">
</div>

## License

The project is licensed under the MIT license.
