# comics

> [!CAUTION]
> **DEPRECATION WARNING:**
> In version 0.7.0, the builder-style methods `.date()` and `.random_date()` will be deprecated.
> Please use the new single-call API:
>
> ```python
> comic = comics.search("calvinandhobbes", date="YYYY-MM-DD")
> comic = comics.search("calvinandhobbes", date="random")
> ```

<p align="center">
  <img src="https://static.wikia.nocookie.net/garfield/images/8/83/GoComicsLogo.png/revision/latest/scale-to-width-down/2849?cb=20230628152535" width="50%"/>
</p>

<br>

[GoComics](https://www.gocomics.com/) API wrapper

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![pypiv](https://img.shields.io/pypi/v/comics.svg)](https://pypi.python.org/pypi/comics)
[![Licence](https://img.shields.io/badge/license-MIT-blue.svg)](https://raw.githubusercontent.com/irahorecka/comics/main/LICENSE)
[![tests](https://github.com/irahorecka/comics/actions/workflows/ci.yml/badge.svg)](https://github.com/irahorecka/comics/actions)

## Installation

```bash
pip install comics
```

## Quick start

Find and download the Calvin and Hobbes comic strip published on January 2, 1990:

```python
import comics

ch = comics.search("calvinandhobbes", date="1990-01-02")
ch.download("calvinandhobbes.png")
```

<div align="center">
    <img src="docs/calvinandhobbes.png">
</div>

## Find comics

Available comics can be found using the `directory` class:

```python
import comics

# List available comics - total of 401
comics.directory.listall()
# >>> ("1-and-done", "9-chickweed-lane-classics", "9chickweedlane", "9to5", ... )

# Find endpoints for Calvin and Hobbes
comics.directory.search("Calvin and Hobbes")
# >>> ("calvinandhobbes", "calvinandhobbesenespanol")
```

First, pass the desired endpoint to `comics.search`. For example, to search for Calvin and Hobbes comics in english use `comics.search("calvinandhobbes")`; for spanish, use `comics.search("calvinandhobbesenespanol")`.

## Search and download comics

Then, search for a comic strip by passing `date` into `search()`:

```python
import comics

# Get a Calvin and Hobbes comic strip by date
ch = comics.search("calvinandhobbes", date="2013-05-13")  # Also accepts datetime.date or datetime object

# Get a random Calvin and Hobbes comic strip
random_ch = comics.search("calvinandhobbes", date="random")
```

Finally, show, download, or stream the comic strip:

```python
# Show comic strip - opens in Jupyter notebook or default image viewer application
ch.show()

# Download comic strip - defaults to {endpoint}.png if an export path is not provided
# E.g., a Calvin and Hobbes comic strip will be exported as "calvinandhobbes.png" in the current working directory
ch.download()

# Stream comic strip - useful if custom image content manipulation is desired
ch.stream()
```

### Retry logic

If a comic strip fails to load due to CDN delays or missing image data, a retry mechanism is built into `download()`, `show()`, and `stream()`. You can control this behavior via:

- `retries`: number of attempts before failing (default = 5)
- `base_delay`: exponential backoff seed time in seconds (default = 0.5)

This improves reliability when fetching newly released strips or handling transient issues.

| Attempt | Wait Before Attempt (sec) | Cumulative Time (sec) |
|---------|---------------------------|------------------------|
| 1       | 0.0                       | 0.0                    |
| 2       | 0.5                       | 0.5                    |
| 3       | 1.0                       | 1.5                    |
| 4       | 2.0                       | 3.5                    |
| 5       | 4.0                       | 7.5                    |
| 6       | 8.0                       | 15.5                   |

Retry behavior can be customized per call:

```python
# Try 3 times total with shorter delay
ch.download(retries=2, base_delay=0.25)
```

## Attributes

An instantiated `search` class will have the following public attributes:

```python
import comics

garfield = comics.search("garfield")
garfield.endpoint
# >>> "garfield"
garfield.title
# >>> "Garfield"
garfield.start_date
# >>> "1978-06-19"
```

An instantiated `search` class with `date` will have the following public attributes:

```python
import comics

garfield = comics.search("garfield", date="2000-08-20")
garfield.endpoint
# >>> "garfield"
garfield.title
# >>> "Garfield"
garfield.date
# >>> "2000-08-20"
garfield.url
# >>> "https://www.gocomics.com/garfield/2000/08/20"
garfield.image_url
# >>> "https://assets.amuniversal.com/6694c52099bd01365606005056a9545d"
```

## Exceptions

An exception will be thrown if the queried date is unregistered or before the comic's origin date:

```python
import comics
from comics.exceptions import InvalidDateError

try:
    peanuts = comics.search("peanuts", date="1900-01-01")
    peanuts.download()
except InvalidDateError:
    print("Whoops, an invalid date was queried.")
```

An exception will be thrown if the queried endpoint is unregistered:

```python
import comics
from comics.exceptions import InvalidEndpointError

try:
    invalid_comic = comics.search("invalid_endpoint", date="2000-01-01")
    invalid_comic.download()
except InvalidEndpointError:
    print("Whoops, an invalid endpoint was queried.")
```

## Contribute

- [Issues Tracker](https://github.com/irahorecka/comics/issues)
- [Source Code](https://github.com/irahorecka/comics/tree/main/comics)

## Support

If you are having issues or would like to propose a new feature, please use the [issues tracker](https://github.com/irahorecka/comics/issues).

<div align="center">
    <img src="docs/dilbert.png">
</div>

## License

This project is licensed under the MIT license.
