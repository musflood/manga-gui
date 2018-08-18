"""Tests for the series_cache module."""
import pytest

from .conftest import requests_patch
from .context import series_cache as sc


@pytest.mark.parametrize('value', [500, [], 2.1, {}])
def test_constructor_raises_error_for_non_string_title(value):
    """Test that constructor for SeriesCache takes only string title."""
    with pytest.raises(TypeError):
        sc.SeriesCache(value)


def test_constructor_raises_error_for_empty_string_title():
    """Test that constructor for SeriesCache does not take an empty title."""
    with pytest.raises(ValueError):
        sc.SeriesCache('')


@pytest.mark.parametrize('value', ['500', [], 2.1, {}])
def test_constructor_raises_error_for_non_int_interval(value):
    """Test that constructor for SeriesCache takes only int update interval."""
    with pytest.raises(TypeError):
        sc.SeriesCache('title', update_interval=value)


def test_constructor_raises_error_for_negative_interval():
    """Test constructor for SeriesCache does not take an negative interval."""
    with pytest.raises(ValueError):
        sc.SeriesCache('title', update_interval=-5)


def test_constructor_sets_atrributes_and_empty_cache():
    """Test that constructor for SeriesCache initializes empty cache."""
    cache = sc.SeriesCache('testing')
    assert cache.title == 'testing'
    assert cache._update_interval == 21600
    assert cache._index_pages == {}
    assert cache._custom_urls == {}
    assert cache._chapter_lists == {}
    assert cache._last_updated == {}


def test_constructor_sets_update_interval_to_interval_when_given():
    """Test that constructor for SeriesCache initializes empty cache."""
    cache = sc.SeriesCache('testing', update_interval=500)
    assert cache._update_interval == 500


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


def test_contains_false_if_an_item_is_not_in_the_cache(
        empty_cache, dummy_source):
    """Test that 'in' works with the series cache."""
    assert (dummy_source in empty_cache) is False


def test_has_outdated_cache_raises_error_for_bad_source(empty_cache):
    """Test has_outdated_cache raises TypeError for non MangaSource source."""
    with pytest.raises(TypeError):
        empty_cache.has_outdated_cache('http://t.co/')


def test_has_outdated_cache_true_for_source_not_in_cache(
        empty_cache, dummy_source):
    """Test has_outdated_cache returns True for source not in cache."""
    assert empty_cache.has_outdated_cache(dummy_source) is True


def test_has_outdated_cache_true_for_old_source(filled_cache):
    """Test has_outdated_cache returns True for source past update interval."""
    from .context import manga_source
    source = manga_source.MangaSource('old-source', 'http://old.net/', '')
    assert source in filled_cache
    assert filled_cache.has_outdated_cache(source) is True


def test_has_outdated_cache_true_past_custom_update_interval(filled_cache):
    """Test has_outdated_cache for recent outside interval treats as old."""
    from .context import manga_source
    source = manga_source.MangaSource('source2', 'http://www.another.com', '')
    filled_cache._update_interval = 5000
    assert filled_cache.has_outdated_cache(source) is True


def test_has_outdated_cache_false_for_new_source(filled_cache, dummy_source):
    """Test has_outdated_cache returns True for source past update interval."""
    assert filled_cache.has_outdated_cache(dummy_source) is False


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


def test_update_index_adds_new_source_to_cache_if_not_in_cache(
        empty_cache, dummy_source):
    """Test that update_index adds a new source if not in cache."""
    assert len(empty_cache) == 0
    empty_cache.update_index(dummy_source)
    assert len(empty_cache) == 1
    assert dummy_source in empty_cache


def test_update_index_does_not_add_source_if_already_in_cache(
        filled_cache, dummy_source):
    """Test that update_index does not add duplicate of source."""
    assert len(filled_cache) == 3
    assert dummy_source in filled_cache
    filled_cache.update_index(dummy_source)
    assert len(filled_cache) == 3
    assert dummy_source in filled_cache


def test_update_index_updates_cached_index_for_a_source_in_cache(
        filled_cache, dummy_source):
    """Test that update_index updates the cache of a source."""
    old_index = filled_cache._index_pages[repr(dummy_source)]
    filled_cache.update_index(dummy_source)
    assert old_index != filled_cache._index_pages[repr(dummy_source)]


def test_update_index_updates_update_time_for_a_source_in_cache(
        filled_cache, dummy_source):
    """Test that update_index updates the cache of a source."""
    old_timestamp = filled_cache._last_updated[repr(dummy_source)]
    filled_cache.update_index(dummy_source)
    assert old_timestamp < filled_cache._last_updated[repr(dummy_source)]


def test_update_index_uses_root_url_if_no_custom_url_given(
        filled_cache, dummy_source):
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


def test_update_index_uses_given_custom_url_for_new_source(
        empty_cache, dummy_source):
    """Test that update_index uses index_url for index page if given."""
    empty_cache.update_index(dummy_source, 'http://t.co/testS')
    index_page = empty_cache._index_pages[repr(dummy_source)]
    assert dummy_source.root_url not in index_page
    assert 'http://t.co/testS' in index_page


def test_update_index_uses_given_custom_url_for_dup_source(
        filled_cache, dummy_source):
    """Test that update_index uses index_url for index page if given."""
    filled_cache.update_index(dummy_source, 'http://t.co/testS')
    index_page = filled_cache._index_pages[repr(dummy_source)]
    assert dummy_source.root_url not in index_page
    assert 'http://t.co/testS' in index_page


def test_update_index_uses_cached_url_for_dup_source(filled_cache):
    """Test that update_index uses cached index url if available."""
    from .context import manga_source
    source = manga_source.MangaSource('old-source', 'http://old.net/', '')
    assert source in filled_cache
    filled_cache.update_index(source)
    index_page = filled_cache._index_pages[repr(source)]
    assert source.root_url not in index_page
    assert 'https://old.chap.net/TestSeries' in index_page


def test_update_index_replaces_cached_url_if_custom_url_given(filled_cache):
    """Test that update_index updates the cached url if a new one is given."""
    from .context import manga_source
    source = manga_source.MangaSource('old-source', 'http://old.net/', '')
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


def test_get_index_for_source_not_in_cache_adds_to_cache(
        empty_cache, dummy_source):
    """Test that get_index for source not in cache adds it."""
    assert dummy_source not in empty_cache
    empty_cache.get_index(dummy_source)
    assert dummy_source in empty_cache


def test_get_index_for_source_not_in_cache_returns_new_index(
        empty_cache, dummy_source, monkeypatch):
    """Test that get_index for source not in cache gets its index page."""
    import requests
    index = '<p>chap</p>'
    monkeypatch.setattr(requests, 'get', requests_patch(text=index))
    result = empty_cache.get_index(dummy_source)
    assert result == index


def test_get_index_recent_source_returns_cached_index(
        filled_cache, dummy_source):
    """Test that get_index for recent source returns cached index."""
    index = filled_cache._index_pages[repr(dummy_source)]
    result = filled_cache.get_index(dummy_source)
    assert index == result


def test_get_index_recent_uses_cached_index_for_same_custom_url(filled_cache):
    """Test that get_index for recent source uses cache for same custom url."""
    from .context import manga_source
    source = manga_source.MangaSource('source2', 'http://www.another.com', '')
    old_index = filled_cache._index_pages[repr(source)]
    result = filled_cache.get_index(source, 'http://another.net/TestSeries')
    assert result == old_index


def test_get_index_recent_gets_new_index_for_new_custom_url(filled_cache):
    """Test that get_index for recent source gets new index for custom url."""
    from .context import manga_source
    source = manga_source.MangaSource('source2', 'http://www.another.com', '')
    old_index = filled_cache._index_pages[repr(source)]
    result = filled_cache.get_index(source, 'http://another.net/tEsTsErIeS')
    assert result != old_index


def test_get_index_old_source_updates_cached_index(filled_cache):
    """Test that get_index for old source updates cached index."""
    from .context import manga_source
    source = manga_source.MangaSource('old-source', 'http://old.net/', '')
    old_index = filled_cache._index_pages[repr(source)]
    result = filled_cache.get_index(source)
    assert result != old_index


def test_get_index_old_source_updates_timstamp(filled_cache):
    """Test that get_index for old source updates the timestamp."""
    from .context import manga_source
    source = manga_source.MangaSource('old-source', 'http://old.net/', '')
    old_timestamp = filled_cache._last_updated[repr(source)]
    filled_cache.get_index(source)
    new_timestamp = filled_cache._last_updated[repr(source)]
    assert old_timestamp < new_timestamp


def test_get_index_old_source_updates_url_when_given(filled_cache):
    """Test that get_index for old source updates the custom url."""
    from .context import manga_source
    source = manga_source.MangaSource('old-source', 'http://old.net/', '')
    assert filled_cache._custom_urls[repr(source)] != 'http://o.co/testseries'
    filled_cache.get_index(source, 'http://o.co/testseries')
    assert filled_cache._custom_urls[repr(source)] == 'http://o.co/testseries'


def test_set_chapter_list_raises_error_for_bad_source(empty_cache):
    """Test set_chapter_list raises a TypeError for non MangaSource source."""
    with pytest.raises(TypeError):
        empty_cache.set_chapter_list('http://t.co/', {})


def test_set_chapter_list_raises_error_for_source_not_in_cache(
        empty_cache, dummy_source):
    """Test set_chapter_list raises a ValueError for source not in cache."""
    with pytest.raises(ValueError):
        empty_cache.set_chapter_list(dummy_source, {})


@pytest.mark.parametrize('value', [500, [], 2.1, '500'])
def test_set_chapter_list_raises_error_for_non_dict_chapter_list(value):
    """Test that set_chapter_list raises a TypeError for non dict chap list."""
    from .conftest import filled_cache, dummy_source
    source = dummy_source()
    cache = filled_cache(source)
    with pytest.raises(TypeError):
        cache.set_chapter_list(source, value)


@pytest.mark.parametrize('value', [500, 2.1, ('55', '56')])
def test_set_chapter_list_raises_error_for_non_string_chap_nums(value):
    """Test set_chapter_list raises a ValueError for malformed chap list."""
    from .conftest import filled_cache, dummy_source
    source = dummy_source()
    cache = filled_cache(source)
    with pytest.raises(ValueError):
        cache.set_chapter_list(source, {value: 'http://t.co'})


@pytest.mark.parametrize('value', ['chap', 'ch.50', 'chapter 4.6'])
def test_set_chapter_list_raises_error_for_non_number_chap_nums(value):
    """Test set_chapter_list raises a ValueError for malformed chap list."""
    from .conftest import filled_cache, dummy_source
    source = dummy_source()
    cache = filled_cache(source)
    with pytest.raises(ValueError):
        cache.set_chapter_list(source, {value: 'http://t.co'})


@pytest.mark.parametrize('value', [500, 2.1, ('55', '56'), [], {}])
def test_set_chapter_list_raises_error_for_non_string_chap_urls(value):
    """Test set_chapter_list raises a ValueError for malformed chap list."""
    from .conftest import filled_cache, dummy_source
    source = dummy_source()
    cache = filled_cache(source)
    with pytest.raises(ValueError):
        cache.set_chapter_list(source, {'5': value})


@pytest.mark.parametrize('value', ['www.goo.co', '/chap/10', '//foo.bar', '5'])
def test_set_chapter_list_raises_error_for_improper_or_partial_chap_url(value):
    """Test set_chapter_list raises a ValueError for malformed chap list."""
    from .conftest import filled_cache, dummy_source
    source = dummy_source()
    cache = filled_cache(source)
    with pytest.raises(ValueError):
        cache.set_chapter_list(source, {'5': value})


def test_set_chapter_list_adds_source_to_chapter_list_cache(filled_cache):
    """Test set_chapter_list adds the source to chap cache if not present."""
    from .context import manga_source
    source = manga_source.MangaSource('source2', 'http://www.another.com', '')
    assert repr(source) not in filled_cache._chapter_lists
    filled_cache.set_chapter_list(source, {})
    assert repr(source) in filled_cache._chapter_lists


def test_set_chapter_list_sets_empty_chapter_list_for_source(
        filled_cache, dummy_source):
    """Test set_chapter_list adds chapter list to cache for source."""
    filled_cache.set_chapter_list(dummy_source, {})
    assert filled_cache._chapter_lists[repr(dummy_source)] == {}


def test_set_chapter_list_sets_filled_chapter_list_for_source(
        filled_cache, dummy_source):
    """Test set_chapter_list adds chapter list to cache for source."""
    chaps = {
        '5': 'http://foo.bar/chap/5',
        '5.3': 'http://foo.bar/chap/5.3'
    }
    filled_cache.set_chapter_list(dummy_source, chaps)
    assert filled_cache._chapter_lists[repr(dummy_source)] == chaps


def test_set_chapter_list_resets_chapter_list_for_source(
        filled_cache, dummy_source):
    """Test set_chapter_list adds chapter list to cache for source."""
    chaps = {
        '5': 'http://foo.bar/chap/5',
        '5.3': 'http://foo.bar/chap/5.3'
    }
    filled_cache.set_chapter_list(dummy_source, chaps)
    assert filled_cache._chapter_lists[repr(dummy_source)] == chaps
    filled_cache.set_chapter_list(dummy_source, {})
    assert filled_cache._chapter_lists[repr(dummy_source)] == {}


def test_set_chapter_list_can_set_chapter_list_to_none(
        filled_cache, dummy_source):
    """Test set_chapter_list can set the chapter list for a source to None."""
    filled_cache.set_chapter_list(dummy_source, None)
    assert filled_cache._chapter_lists[repr(dummy_source)] is None


def test_get_chapter_list_raises_error_for_bad_source(empty_cache):
    """Test get_chapter_list raises a TypeError for non MangaSource source."""
    with pytest.raises(TypeError):
        empty_cache.get_chapter_list('http://t.co/')


def test_get_chapter_list_returns_stored_list_for_recent_source(
        filled_cache, dummy_source):
    """Test get_chapter_list returns cached chapter list for recent source."""
    chapters = filled_cache._chapter_lists[repr(dummy_source)]
    assert filled_cache.get_chapter_list(dummy_source) == chapters


def test_get_chapter_list_returns_none_for_old_source(filled_cache):
    """Test get_chapter_list returns None for old source."""
    from .context import manga_source
    source = manga_source.MangaSource('old-source', 'http://old.net/', '')
    chapters = filled_cache._chapter_lists[repr(source)]
    assert chapters is not None
    assert filled_cache.get_chapter_list(source) is None


def test_get_chapter_list_returns_none_for_source_not_in_cache(empty_cache):
    """Test get_chapter_list returns None for source not in the cache."""
    from .context import manga_source
    source = manga_source.MangaSource('new one', 'http://new.net', '+')
    assert empty_cache.get_chapter_list(source) is None


def test_get_chapter_list_returns_none_for_source_without_chaps(filled_cache):
    """Test get_chapter_list returns None for source. without cached chaps."""
    from .context import manga_source
    source = manga_source.MangaSource('source2', 'http://www.another.com', '')
    assert filled_cache.get_chapter_list(source) is None
