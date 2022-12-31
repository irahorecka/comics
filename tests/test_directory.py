"""
tests/test_directory
~~~~~~~~~~~~~~~~~~~~
"""

from pytest import mark

import comics


def test_directory_listall():
    """Tests proper return of comic endpoints when calling `comics.directory.listall`
    method."""
    all_comics = comics.directory.listall()
    # Number of comics registered in GoComics as of Dec. 2022 is 474
    assert len(all_comics) == 474
    # Check if all comics directory is a tuple of sorted comic endpoints
    assert all_comics == tuple(sorted(all_comics))


@mark.parametrize("params", (("fox", 3), ("calvin", 2), ("se", 30), ("rm", 6), ("at", 42)))
def test_directory_search(params):
    """Tests proper return of comic endpoints when calling `comics.directory.search`
    method with search keywords (case insensitive)."""
    search_kwd, num_results = params
    assert len(comics.directory.search(search_kwd)) == num_results
    # Test case insensitivity
    assert len(comics.directory.search(search_kwd.upper())) == num_results
    assert len(comics.directory.search(search_kwd.title())) == num_results
    assert len(comics.directory.search(search_kwd.capitalize())) == num_results
