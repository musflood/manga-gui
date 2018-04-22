"""Tests for the manga_source module."""
from .context import mangasource as ms


def test_manga_source_sets_initial_values():
    """Test that the constructor for MangaSource works correctly."""
    source = ms.MangaSource('test source', 'www.source.com', '-')
    assert source.name == 'test source'
    assert source.root_url == 'www.source.com'
    assert source.slug_filler == '-'
