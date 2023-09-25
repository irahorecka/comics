# comics

[GoComics](https://www.gocomics.com/) API wrapper

[![pypiv](https://img.shields.io/pypi/v/comics.svg)](https://pypi.python.org/pypi/comics)
[![Python 3.7+](https://img.shields.io/badge/python-3.7+-blue.svg)](https://www.python.org/downloads/)
[![continuous-integration](https://github.com/irahorecka/comics/workflows/continuous-integration/badge.svg?branch=main)](https://github.com/irahorecka/comics/actions)
[![Licence](https://img.shields.io/badge/license-MIT-blue.svg)](https://raw.githubusercontent.com/irahorecka/comics/main/LICENSE)

## Installation

```bash
pip install comics
```

## Quick start

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

# List available comics - total of 475
comics.directory.listall()
# >>> ("a_problem_like_jamal", "aaggghhh", "adam_at_home", "adult_children", ... )

# Find Calvin and Hobbes
comics.directory.search("Calvin and Hobbes")
# >>> ("calvin_and_hobbes", "calvin_and_hobbes_en_espanol")
```

Use the desired endpoint to query a comic. For example, to search for Calvin and Hobbes comics in english use `comics.calvin_and_hobbes`; for spanish, use `comics.calvin_and_hobbes_en_espanol`.

## Search and download comics

Instantiate a query class with a date argument or use the random date constructor:

```python
import comics

# Get a Calvin and Hobbes comic strip by date
ch = comics.calvin_and_hobbes.date("2013-05-13")  # Also accepts datetime object

# Get a random Calvin and Hobbes comic strip
random_ch = comics.calvin_and_hobbes.random_date()
```

Once instantiated, show, download, or stream the comic strip:

```python
# Show comic strip - opens in default image viewer application
ch.show()

# Download comic strip - defaults to {comic endpoint}.png if an export path is not provided
# E.g., a Calvin and Hobbes comic strip will be exported as "calvinandhobbes.png" in the current working directory
ch.download()

# Stream comic strip - useful if custom image content manipulation is desired
ch.stream()
```

## Attributes

An instantiated query class will have the following public attributes:

```python
import comics

garfield = comics.garfield.date("08/20/2000")
garfield.date
# >>> "2000-08-20"
garfield.title
# >>> "Garfield"
garfield.url
# >>> "https://www.gocomics.com/garfield/2000/08/20"
garfield.image_url
# >>> "https://assets.amuniversal.com/6694c52099bd01365606005056a9545d"
```

## Exceptions

An exception will be thrown if the query date is unregistered or before the comic's origin date:

```python
import comics
from comics.exceptions import InvalidDateError

try:
    peanuts = comics.peanuts.date("1900-01-01")
    peanuts.download()
except InvalidDateError:
    print("Whoops, an invalid date was queried.")
```

## Contribute

* [Issues Tracker](https://github.com/irahorecka/comics/issues)
* [Source Code](https://github.com/irahorecka/comics/tree/main/comics)

## Support

If you are having issues or would like to propose a new feature, please use the [issues tracker](https://github.com/irahorecka/comics/issues).

<div align="center">
    <img src="docs/dilbert.png">
</div>

## License

This project is licensed under the MIT license.
