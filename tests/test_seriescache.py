"""Tests for the seriescache module."""
import pytest

from .conftest import requests_patch
from .context import seriescache as sc


@pytest.mark.parametrize('value', [500, [], 2.1, {}])
def test_constructor_raises_error_for_non_string_title(value):
    """Test that constructor for SeriesCache takes only string title."""
    with pytest.raises(TypeError):
        sc.SeriesCache(value)


def test_constructor_raises_error_for_empty_string_title():
    """Test that constructor for SeriesCache does not take an empty title."""
    with pytest.raises(ValueError):
        sc.SeriesCache('')


def test_constructor_sets_atrributes_and_empty_cache():
    """Test that constructor for SeriesCache initializes empty cache."""
    cache = sc.SeriesCache('testing')
    assert cache.title == 'testing'
    assert cache._index_pages == {}
    assert cache._custom_urls == {}
    assert cache._last_updated == {}


def test_repr_displays_title_and_cache_size_for_empty_cache(empty_cache):
    """Test that repr works for empty series cache."""
    assert repr(empty_cache) == '<SeriesCache: empty test, cache: 0 sources>'


def test_repr_displays_title_and_cache_size_for_filled_cache(filled_cache):
    """Test that repr works for filled series cache."""
    assert repr(filled_cache) == '<SeriesCache: test series, cache: 3 sources>'


def test_str_displays_title_only(filled_cache):
    """Test that str displays only the title of the series for the cache."""
    assert str(filled_cache) == 'test series'


def test_len_gets_zero_for_number_of_sources_in_empty_cache(empty_cache):
    """Test that len gets the number of sources in the cache."""
    assert len(empty_cache) == 0


def test_len_gets_number_of_sources_in_filled_cache(filled_cache):
    """Test that len gets the number of sources in the cache."""
    assert len(filled_cache) == 3


def test_contains_true_if_an_item_is_in_the_cache(filled_cache, dummy_source):
    """Test that 'in' works with the series cache."""
    assert (dummy_source in filled_cache) is True


def test_contains_false_if_an_item_is_not_in_the_cache(empty_cache,
                                                       dummy_source):
    """Test that 'in' works with the series cache."""
    assert (dummy_source in empty_cache) is False


def test_update_index_raises_error_for_bad_source(empty_cache):
    """Test that update_index raises a TypeError for non MangaSource source."""
    with pytest.raises(TypeError):
        empty_cache.update_index('http://t.co/')


@pytest.mark.parametrize('value', [500, [], 2.1, {}])
def test_update_index_raises_error_for_non_string_index_url(value):
    """Test that update_index raises a TypeError for non MangaSource source."""
    from .conftest import empty_cache, dummy_source
    with pytest.raises(TypeError):
        empty_cache().update_index(dummy_source(), value)


def test_update_index_adds_new_source_to_cache_if_not_in_cache(empty_cache,
                                                               dummy_source):
    """Test that update_index adds a new source if not in cache."""
    assert len(empty_cache) == 0
    empty_cache.update_index(dummy_source)
    assert len(empty_cache) == 1
    assert dummy_source in empty_cache


def test_update_index_does_not_add_source_if_already_in_cache(filled_cache,
                                                              dummy_source):
    """Test that update_index does not add duplicate of source."""
    assert len(filled_cache) == 3
    assert dummy_source in filled_cache
    filled_cache.update_index(dummy_source)
    assert len(filled_cache) == 3
    assert dummy_source in filled_cache


def test_update_index_updates_cached_index_for_a_source_in_cache(filled_cache,
                                                                 dummy_source):
    """Test that update_index updates the cache of a source."""
    old_index = filled_cache._index_pages[repr(dummy_source)]
    filled_cache.update_index(dummy_source)
    assert old_index != filled_cache._index_pages[repr(dummy_source)]


def test_update_index_updates_update_time_for_a_source_in_cache(filled_cache,
                                                                dummy_source):
    """Test that update_index updates the cache of a source."""
    old_timestamp = filled_cache._last_updated[repr(dummy_source)]
    filled_cache.update_index(dummy_source)
    assert old_timestamp < filled_cache._last_updated[repr(dummy_source)]


def test_update_index_uses_root_url_if_no_custom_url_given(filled_cache,
                                                           dummy_source):
    """Test that update_index uses source root url if no index_url given."""
    filled_cache.update_index(dummy_source)
    index_page = filled_cache._index_pages[repr(dummy_source)]
    assert dummy_source.root_url in index_page


def test_update_index_adds_custom_url_if_given(empty_cache, dummy_source):
    """Test that update_index adds custom url if an index_url is given."""
    assert len(empty_cache._custom_urls) == 0
    empty_cache.update_index(dummy_source, 'http://t.co/testS')
    assert len(empty_cache._custom_urls) == 1
    assert empty_cache._custom_urls[repr(dummy_source)] == 'http://t.co/testS'


def test_update_index_uses_given_custom_url_for_new_source(empty_cache,
                                                           dummy_source):
    """Test that update_index uses index_url for index page if given."""
    empty_cache.update_index(dummy_source, 'http://t.co/testS')
    index_page = empty_cache._index_pages[repr(dummy_source)]
    assert dummy_source.root_url not in index_page
    assert 'http://t.co/testS' in index_page


def test_update_index_uses_given_custom_url_for_dup_source(filled_cache,
                                                           dummy_source):
    """Test that update_index uses index_url for index page if given."""
    filled_cache.update_index(dummy_source, 'http://t.co/testS')
    index_page = filled_cache._index_pages[repr(dummy_source)]
    assert dummy_source.root_url not in index_page
    assert 'http://t.co/testS' in index_page


def test_update_index_uses_cached_url_for_dup_source(filled_cache):
    """Test that update_index uses cached index url if available."""
    from .context import mangasource
    source = mangasource.MangaSource('old-source', 'http://old.net/', '')
    assert source in filled_cache
    filled_cache.update_index(source)
    index_page = filled_cache._index_pages[repr(source)]
    assert source.root_url not in index_page
    assert 'https://old.chap.net/TestSeries' in index_page


def test_update_index_replaces_cached_url_if_custom_url_given(filled_cache):
    """Test that update_index updates the cached url if a new one is given."""
    from .context import mangasource
    source = mangasource.MangaSource('old-source', 'http://old.net/', '')
    url = filled_cache._custom_urls[repr(source)]
    assert url == 'https://old.chap.net/TestSeries'
    filled_cache.update_index(source, 'https://new.net/TestSeries')
    url = filled_cache._custom_urls[repr(source)]
    assert url == 'https://new.net/TestSeries'


def test_get_index_raises_error_for_bad_source(empty_cache):
    """Test that get_index raises a TypeError for non MangaSource source."""
    with pytest.raises(TypeError):
        empty_cache.get_index('http://t.co/')


@pytest.mark.parametrize('value', [500, [], 2.1, {}])
def test_get_index_raises_error_for_non_string_index_url(value):
    """Test that get_index raises a TypeError for non string url."""
    from .conftest import empty_cache, dummy_source
    with pytest.raises(TypeError):
        empty_cache().get_index(dummy_source(), value)


@pytest.mark.parametrize('value', ['500', [], 2.1, {}])
def test_get_index_raises_error_for_non_integer_update_interval(value):
    """Test that get_index raises a TypeError for non integer interval."""
    from .conftest import empty_cache, dummy_source
    with pytest.raises(TypeError):
        empty_cache().get_index(dummy_source(), update_interval=value)


def test_get_index_raises_error_for_negative_update_interval(empty_cache,
                                                             dummy_source):
    """Test that get_index raises a ValueError for negative interval."""
    with pytest.raises(ValueError):
        empty_cache.get_index(dummy_source, update_interval=-5)


def test_get_index_for_source_not_in_cache_adds_to_cache(empty_cache,
                                                         dummy_source):
    """Test that get_index for source not in cache adds it."""
    assert dummy_source not in empty_cache
    empty_cache.get_index(dummy_source)
    assert dummy_source in empty_cache


def test_get_index_for_source_not_in_cache_returns_new_index(empty_cache,
                                                             dummy_source,
                                                             monkeypatch):
    """Test that get_index for source not in cache gets its index page."""
    import requests
    index = '<p>chap</p>'
    monkeypatch.setattr(requests, 'get', requests_patch(text=index))
    result = empty_cache.get_index(dummy_source)
    assert result == index


def test_get_index_recent_source_returns_cached_index(filled_cache,
                                                      dummy_source):
    """Test that get_index for recent source returns cached index."""
    index = filled_cache._index_pages[repr(dummy_source)]
    result = filled_cache.get_index(dummy_source)
    assert index == result


def test_get_index_recent_uses_cached_index_for_same_custom_url(filled_cache):
    """Test that get_index for recent source uses cache for same custom url."""
    from .context import mangasource
    source = mangasource.MangaSource('source2', 'http://www.another.com', '')
    old_index = filled_cache._index_pages[repr(source)]
    result = filled_cache.get_index(source, 'http://another.net/TestSeries')
    assert result == old_index


def test_get_index_recent_gets_new_index_for_new_custom_url(filled_cache):
    """Test that get_index for recent source gets new index for custom url."""
    from .context import mangasource
    source = mangasource.MangaSource('source2', 'http://www.another.com', '')
    old_index = filled_cache._index_pages[repr(source)]
    result = filled_cache.get_index(source, 'http://another.net/tEsTsErIeS')
    assert result != old_index


def test_get_index_recent_given_update_interval_treats_as_old(filled_cache):
    """Test that get_index for recent outside interval treats as old source."""
    from .context import mangasource
    source = mangasource.MangaSource('source2', 'http://www.another.com', '')
    old_index = filled_cache._index_pages[repr(source)]
    result = filled_cache.get_index(source, update_interval=5000)
    assert result != old_index


def test_get_index_old_source_updates_cached_index(filled_cache):
    """Test that get_index for old source updates cached index."""
    from .context import mangasource
    source = mangasource.MangaSource('old-source', 'http://old.net/', '')
    old_index = filled_cache._index_pages[repr(source)]
    result = filled_cache.get_index(source)
    assert result != old_index


def test_get_index_old_source_updates_timstamp(filled_cache):
    """Test that get_index for old source updates the timestamp."""
    from .context import mangasource
    source = mangasource.MangaSource('old-source', 'http://old.net/', '')
    old_timestamp = filled_cache._last_updated[repr(source)]
    filled_cache.get_index(source)
    new_timestamp = filled_cache._last_updated[repr(source)]
    assert old_timestamp < new_timestamp


def test_get_index_old_source_updates_url_when_given(filled_cache):
    """Test that get_index for old source updates the custom url."""
    from .context import mangasource
    source = mangasource.MangaSource('old-source', 'http://old.net/', '')
    assert filled_cache._custom_urls[repr(source)] != 'http://o.co/testseries'
    filled_cache.get_index(source, 'http://o.co/testseries')
    assert filled_cache._custom_urls[repr(source)] == 'http://o.co/testseries'
