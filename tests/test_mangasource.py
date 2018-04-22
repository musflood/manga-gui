"""Tests for the manga_source module."""
from .context import mangasource as ms

import pytest


@pytest.mark.parametrize('value', [500, [], 2.1, {}])
def test_constructor_raises_type_error_for_non_string_name(value):
    """Test that constructor raises a TypeError for non-string."""
    with pytest.raises(TypeError):
        ms.MangaSource(value, 'http://www.source.com/', '_')


@pytest.mark.parametrize('value', [500, [], 2.1, {}])
def test_constructor_raises_type_error_for_non_string_url(value):
    """Test that constructor raises a TypeError for non-string."""
    with pytest.raises(TypeError):
        ms.MangaSource('test', value, '_')


@pytest.mark.parametrize('value', [500, [], 2.1, {}])
def test_constructor_raises_type_error_for_non_string_slug_filler(value):
    """Test that constructor raises a TypeError for non-string."""
    with pytest.raises(TypeError):
        ms.MangaSource('test', 'http://www.source.com/', value)


def test_constructor_raises_value_error_for_empty_name():
    """Test that ocnstructor raises TypeError for empty name."""
    with pytest.raises(ValueError):
        ms.MangaSource('', 'http://www.source.com/', '-')


def test_constructor_raises_value_error_for_empty_url():
    """Test that ocnstructor raises TypeError for empty url."""
    with pytest.raises(ValueError):
        ms.MangaSource('test', '', '-')


def test_constructor_raises_value_error_for_invalid_url():
    """Test that ocnstructor raises TypeError for invalid url."""
    with pytest.raises(ValueError):
        ms.MangaSource('test', 'bad test', '-')


def test_constructor_sets_initial_values():
    """Test that the constructor for MangaSource works correctly."""
    source = ms.MangaSource('test source', 'http://www.source.com/', '-')
    assert source.name == 'test source'
    assert source.root_url == 'http://www.source.com/'
    assert source.slug_filler == '-'


def test_constructor_adds_ending_slash_to_url():
    """Test that that constructor adds the ending slash to URL."""
    source = ms.MangaSource('test source', 'http://www.source.com', '-')
    assert source.root_url == 'http://www.source.com/'


def test_constructor_adds_protocol_to_url():
    """Test that that constructor adds the HTTP to URL."""
    source = ms.MangaSource('test source', 'www.source.com/', '-')
    assert source.root_url == 'http://www.source.com/'


def test_constructor_adds_protocol_and_ending_slash_to_url():
    """Test that that constructor adds the HTTP and slash to URL."""
    source = ms.MangaSource('test source', 'www.source.com', '-')
    assert source.root_url == 'http://www.source.com/'


def test_repr_displays_name_and_url(source):
    """Test that the repr of MangaSource displays correctly."""
    rep = repr(source)
    assert rep == '<MangaSource: test source @ http://www.source.com/>'


def test_str_representation_displays_name_only(source):
    """Test that the str of MangaSource displays correctly."""
    assert str(source) == 'test source'


@pytest.mark.parametrize('value', [500, [], 2.1, {}])
def test_get_slug_raises_type_error_for_non_string(value):
    """Test that _get_slug raises a TypeError for non-string."""
    source = ms.MangaSource('test', 'http://www.source.com/', '_')
    with pytest.raises(TypeError):
        source._get_slug(value)


@pytest.mark.parametrize('slug_filler', ['', '-', '_', '+'])
def test_get_slug_replaces_spaces_with_slug_filler(slug_filler):
    """Test that _get_slug replaces spaces with filler."""
    source = ms.MangaSource('test', 'http://www.source.com/', slug_filler)
    assert source._get_slug('hi there') == slug_filler.join(('hi', 'there'))


@pytest.mark.parametrize('string, result', [
    ('it\'s?', 'its'), ('hi.there', 'hithere'), ('it-can"t be!', 'itcant_be'),
    ('1984+', '1984'), ('5_a: redux', '5a_redux'), ('sup - er', 'sup__er')
])
def test_get_slug_removes_url_unsafe_characters(string, result):
    """Test that _get_slug replaces spaces with filler."""
    source = ms.MangaSource('test', 'http://www.source.com/', '_')
    assert source._get_slug(string) == result


@pytest.mark.parametrize('string, result', [
    ('Find it!', 'find_it'), ('RE:soo', 'resoo'), ('it X it', 'it_x_it'),
    ('sUpErHaCkA', 'superhacka')
])
def test_get_slug_converts_string_to_lower_case(string, result):
    """Test that _get_slug converts string to lower case."""
    source = ms.MangaSource('test', 'http://www.source.com/', '_')
    assert source._get_slug(string) == result


@pytest.mark.parametrize('value', [500, [], 2.1, {}])
def test_index_url_raises_type_error_for_non_string(value):
    """Test that index_url raises a TypeError for non-string."""
    source = ms.MangaSource('test', 'http://www.source.com/', '_')
    with pytest.raises(TypeError):
        source.index_url(value)


def test_index_url_joins_root_url_to_slug_of_title(source):
    """Test that index_url joins the root url to the title slug."""
    assert source.index_url('hi there') == 'http://www.source.com/hi_there'


def test_ping_gives_false_for_offline_site(source, fail_response, monkeypatch):
    """Test that ping returns False for a site that is off-line."""
    import requests
    monkeypatch.setattr(requests, 'head', fail_response)
    assert source.ping() is False


def test_ping_gives_true_for_online_site(source, conn_response, monkeypatch):
    """Test that ping returns True for a site that is on-line."""
    import requests
    monkeypatch.setattr(requests, 'head', conn_response)
    assert source.ping() is True
