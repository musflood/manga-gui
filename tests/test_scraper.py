"""Tests for the scraper module."""
from bs4 import BeautifulSoup
import pytest

from .conftest import requests_patch
from .context import scraper as scr


def test_pull_page_image_raises_type_error_for_non_soup_html(dummy_source):
    """Test that a TypeError is raised for non soup HTML."""
    with pytest.raises(TypeError):
        scr.Scraper._pull_page_image('<img src="test.png">', dummy_source)


def test_pull_page_image_raises_type_error_for_bad_source(dummy_soup):
    """Test that a TypeError is raised for non MangaSource source."""
    with pytest.raises(TypeError):
        scr.Scraper._pull_page_image(dummy_soup, 'http://www.source.com/')


def test_pull_page_image_raises_value_error_for_no_images(dummy_source):
    """Test that a ValueError is raised for html with no image on it."""
    html = BeautifulSoup('<a href="/page"></a>', 'html.parser')
    with pytest.raises(ValueError):
        scr.Scraper._pull_page_image(html, dummy_source)


def test_pull_page_image_raises_value_error_for_img_without_src(dummy_source):
    """Test that a ValueError is raised for image with no src on it."""
    html = BeautifulSoup('<img :src="item.src">', 'html.parser')
    with pytest.raises(ValueError):
        scr.Scraper._pull_page_image(html, dummy_source)


def test_pull_page_image_adds_protocol_to_src_url(dummy_source):
    """Test that _pull_page_image fixes image URL with no protocol."""
    html = BeautifulSoup('<img src="//file.co/test.png">', 'html.parser')
    assert scr.Scraper._pull_page_image(html, dummy_source)


def test_pull_page_image_gets_img_data_and_extention(dummy_soup, dummy_source):
    """Test that _pull_page_image returns proper values for image."""
    img, ext, _ = scr.Scraper._pull_page_image(dummy_soup, dummy_source)
    assert img == b'\x00\x00\x00\x00\x00\x00'
    assert ext == 'png'


def test_pull_page_image_a_tag_for_multipage_source(dummy_soup, dummy_source):
    """Test that _pull_page_image returns anchor tag for multipage source."""
    _, _, tag = scr.Scraper._pull_page_image(dummy_soup, dummy_source)
    assert tag.name == 'a'


def test_pull_page_image_img_tag_for_one_page_source(dummy_soup, dummy_source):
    """Test that _pull_page_image returns image tag for singlepage source."""
    dummy_source.is_multipage = False
    _, _, tag = scr.Scraper._pull_page_image(dummy_soup, dummy_source)
    assert tag.name == 'img'


def test_pull_page_image_takes_first_image_from_soup(dummy_soup, dummy_source):
    """Test that _pull_page_image removes first image from soup."""
    assert len(dummy_soup.find_all('img')) == 4
    _, _, tag = scr.Scraper._pull_page_image(dummy_soup, dummy_source)
    assert len(dummy_soup.find_all('img')) == 3
    assert tag.img['id'] == '1'


@pytest.mark.parametrize('value', [500, [], 2.1, {}])
def test_get_page_raises_type_error_for_non_string_url(value):
    """Test that _get_page raises a TypeError for non-string URL."""
    from .context import mangasource
    source = mangasource.MangaSource('test', 'www.test.com', '_')
    with pytest.raises(TypeError):
        scr.Scraper._get_page(value, source)


@pytest.mark.parametrize('value', [500, [], 2.1, {}, 'www.test.com'])
def test_get_page_raises_type_error_for_bad_mangasource(value):
    """Test that _get_page raises a TypeError for non-MangaSource source."""
    with pytest.raises(TypeError):
        scr.Scraper._get_page('www.test.com', value)


def test_get_page_raises_value_error_for_invalid_url(dummy_source):
    """Test that _get_page raises a ValueError for an invalid URL."""
    with pytest.raises(ValueError):
        scr.Scraper._get_page('www.test.com', dummy_source)


def test_get_page_gets_img_data_extention_next_url_and_soup(dummy_source):
    """Test that _get_page returns the proper values."""
    result = scr.Scraper._get_page('http://www.test.com/001/page/1',
                                   dummy_source)
    img, ext, next_page, html = result
    assert img == b'\x00\x00\x00\x00\x00\x00'
    assert ext == 'png'
    assert next_page == 'http://www.test.com/001/page/2'
    assert isinstance(html, BeautifulSoup)


def test_get_page_removes_image_link_from_html(dummy_source):
    """Test that _get_page removes the image element from the html result."""
    result = scr.Scraper._get_page('http://www.test.com/001/page/1',
                                   dummy_source)
    next_page, html = result[2:]
    assert html.find('a', href=lambda h: h in next_page) is None


def test_get_page_has_empty_string_for_next_page_without_a_tag(
        dummy_source, monkeypatch):
    """Test _get_page returns an empty string for next page URL on img tag."""
    import requests
    req = requests_patch(text='<img src="https://file.co/img.png">',
                         content=b'\x00\x00\x00\x00\x00\x00')
    monkeypatch.setattr(requests, 'get', req)
    result = scr.Scraper._get_page('http://www.test.com/001/page/1',
                                   dummy_source)
    assert result[2] == ''


def test_get_page_gets_next_url_with_relative_path(dummy_source, monkeypatch):
    """Test _get_page returns next page url with relative path."""
    import requests
    req = requests_patch(text='''<a href="./2">
        <img src="https://file.co/img.png">
        </a>''', content=b'\x00\x00\x00\x00\x00\x00')
    monkeypatch.setattr(requests, 'get', req)
    result = scr.Scraper._get_page('http://www.test.com/001/page/1',
                                   dummy_source)
    assert result[2] == 'http://www.test.com/001/page/2'


@pytest.mark.parametrize('value', [500, [], 2.1, {}])
def test_generate_multipage_chapter_raises_error_for_non_string_url(value):
    """Test _generate_multipage_chapter raises a TypeError for bad url."""
    from .context import mangasource
    source = mangasource.MangaSource('test', 'www.test.com', '_')
    with pytest.raises(TypeError):
        scr.Scraper._generate_multipage_chapter(value, source)


@pytest.mark.parametrize('value', [500, [], 2.1, {}, 'www.test.com'])
def test_generate_multipage_chapter_raises_error_for_bad_mangasource(value):
    """Test _generate_multipage_chapter raises a TypeError for bad source."""
    with pytest.raises(TypeError):
        scr.Scraper._generate_multipage_chapter('http://t.com/', value)


def test_generate_multipage_chapter_raises_error_for_empty_url(dummy_source):
    """Test _generate_multipage_chapter raises ValueError for empty url."""
    with pytest.raises(ValueError):
        scr.Scraper._generate_multipage_chapter('', dummy_source)


def test_generate_multipage_chapter_returns_generator(dummy_source):
    """Test _generate_multipage_chapter returns a generator of tuples."""
    pages = scr.Scraper._generate_multipage_chapter(
        'http://t.com/001/page/1', dummy_source)
    result = next(pages)
    assert type(result) is tuple


def test_generate_multipage_chapter_yields_image_and_extension(dummy_source):
    """Test _generate_multipage_chapter yeilds image data and extention."""
    pages = scr.Scraper._generate_multipage_chapter(
        'http://t.com/001/page/1', dummy_source)
    img, ext = next(pages)
    assert img == b'\x00\x00\x00\x00\x00\x00'
    assert ext == 'png'


def test_generate_multipage_chapter_yields_all_images_in_chapter(
        dummy_source, monkeypatch):
    """Test _generate_multipage_chapter yeilds image data and extention."""
    import requests

    def page_txt(ch_len):
        n = 2
        while True:
            pg = n // 2
            yield f'''<a href="/{pg // ch_len + 2}/page/{pg % ch_len + 1}">
            <img src="https://file.co/img.png">
            </a>'''
            n += 1

    def content():
        n = 1
        while True:
            yield b'\x00' * (n // 2)
            n += 1

    req = requests_patch(text=page_txt(4), content=content())
    monkeypatch.setattr(requests, 'get', req)

    pages = scr.Scraper._generate_multipage_chapter(
        'http://t.com/2/page/1', dummy_source)
    imgs = [pg for pg in pages]
    assert len(imgs) == 4
    assert imgs[0] != imgs[1] != imgs[2] != imgs[3]


def test_generate_multipage_chapter_works_for_last_chapter(
        dummy_source, monkeypatch):
    """Test _generate_multipage_chapter still works for final chapter."""
    import requests

    def page_txt(ch, ch_len):
        for n in range(2, ch_len * 2):
            pg = n // 2
            yield f'''<a href="/{ch}/page/{pg % ch_len + 1}">
            <img src="https://file.co/img.png">
            </a>'''
        yield f'''<a href="/{ch}/page/end">
        <img src="https://file.co/img.png">
        </a>'''
        yield ''
        yield f'<p>Chapter {ch} is the last one!</p>'

    def content():
        n = 1
        while True:
            yield b'\x00' * (n // 2)
            n += 1

    req = requests_patch(text=page_txt(2, 4), content=content())
    monkeypatch.setattr(requests, 'get', req)

    pages = scr.Scraper._generate_multipage_chapter(
        'http://t.com/2/page/1', dummy_source)
    imgs = [pg for pg in pages]
    assert len(imgs) == 4


def test_generate_multipage_chapter_works_dashed_url(
        dummy_source, monkeypatch):
    """Test _generate_multipage_chapter still works for dashed chapter url."""
    import requests

    def page_txt(ch_len):
        for n in range(2, ch_len * 2 + 1):
            pg = n // 2
            yield f'''<a href="https://foo.co/chap/437217-{pg % ch_len + 1}">
            <img src="https://file.co/img.png">
            </a>'''
        yield f'''<a href="https://foo.co/chap/437416/">
        <img src="https://file.co/img.png">
        </a>'''

    req = requests_patch(text=page_txt(4), content='')
    monkeypatch.setattr(requests, 'get', req)

    pages = scr.Scraper._generate_multipage_chapter(
        'https://foo.co/chap/437217-1', dummy_source)
    imgs = [pg for pg in pages]
    assert len(imgs) == 4


@pytest.mark.parametrize('value', [500, [], 2.1, {}])
def test_generate_singlepage_chapter_raises_error_for_non_string_url(value):
    """Test _generate_singlepage_chapter raises a TypeError for bad url."""
    from .context import mangasource
    source = mangasource.MangaSource('test', 'www.test.com', '_')
    with pytest.raises(TypeError):
        scr.Scraper._generate_singlepage_chapter(value, source)


@pytest.mark.parametrize('value', [500, [], 2.1, {}, 'www.test.com'])
def test_generate_singlepage_chapter_raises_error_for_bad_mangasource(value):
    """Test _generate_singlepage_chapter raises a TypeError for bad source."""
    with pytest.raises(TypeError):
        scr.Scraper._generate_singlepage_chapter('http://t.com/', value)


def test_generate_singlepage_chapter_raises_error_for_empty_url(dummy_source):
    """Test _generate_singlepage_chapter raises ValueError for empty url."""
    with pytest.raises(ValueError):
        scr.Scraper._generate_singlepage_chapter('', dummy_source)


def test_generate_singlepage_chapter_returns_generator(dummy_source):
    """Test _generate_singlepage_chapter returns a generator of tuples."""
    pages = scr.Scraper._generate_singlepage_chapter(
        'http://t.com/001/page/1', dummy_source)
    result = next(pages)
    assert type(result) is tuple


def test_generate_singlepage_chapter_yields_image_and_extension(dummy_source):
    """Test _generate_singlepage_chapter yeilds image data and extention."""
    pages = scr.Scraper._generate_singlepage_chapter(
        'http://t.com/001/page/1', dummy_source)
    img, ext = next(pages)
    assert img == b'\x00\x00\x00\x00\x00\x00'
    assert ext == 'png'


def test_generate_singlepage_chapter_yields_all_images_in_chapter(
        dummy_source, monkeypatch):
    """Test _generate_singlepage_chapter yeilds image data and extention."""
    import requests

    page_txt = '''
    <img src="http://files.co/test.png" id="1">
    <img src="http://files.co/test.png" id="2">
    <img src="http://files.co/test.png" id="3">
    <img src="http://files.co/test.png" id="4">
    '''

    def content():
        n = 0
        while True:
            yield b'\x00' * n
            n += 1

    req = requests_patch(text=page_txt, content=content())
    monkeypatch.setattr(requests, 'get', req)

    pages = scr.Scraper._generate_singlepage_chapter(
        'http://t.com/1', dummy_source)
    imgs = [pg for pg in pages]
    assert len(imgs) == 4
    assert imgs[0] != imgs[1] != imgs[2] != imgs[3]


@pytest.mark.parametrize('value', [500, [], 2.1, {}])
def test_make_chapter_finder_raises_error_for_non_string_title(value):
    """Test _make_chapter_finder raises a TypeError for bad title."""
    with pytest.raises(TypeError):
        scr.Scraper._make_chapter_finder(value)


def test_make_chapter_finder_returns_a_function():
    """Test _make_chapter_finder returns a function."""
    result = scr.Scraper._make_chapter_finder('')
    assert callable(result)


def test_chapter_finder_raises_error_for_missing_chapter_number():
    """Test that chapter finder raises a ValueError for text missing number."""
    find = scr.Scraper._make_chapter_finder('')
    with pytest.raises(ValueError):
        find('nothing')


chapter_entries = [
    ('{} 77 Vol 08 The Wired Red Wild Card Part 1', '77'),
    ('Vol.10 chapter 85 : The wired red wild card pt.9', '85'),
    ('97 - The Wired Red Wild Card PT.21', '97'),
    ('{} 55.1', '55.1'),
    ('Chaper 20', '20'),
    ('Vol.10 Ch.43', '43'),
    ('CH.004', '4')
]


@pytest.mark.parametrize('title',
                         ['title', '300', 'NO.7', 'The Longest 4Ever'])
@pytest.mark.parametrize('text, num', chapter_entries)
def test_chapter_finder_finds_the_chapter_number(title, text, num):
    """Test that chapter finder gets the correct chapter number."""
    text = text.format(title)
    find = scr.Scraper._make_chapter_finder(title)
    assert find(text) == num


@pytest.mark.parametrize('value', [500, [], 2.1, {}])
def test_chapter_list_raises_error_for_non_string_url(value):
    """Test chapter_list raises a TypeError for bad url."""
    from .context import mangasource, seriescache
    source = mangasource.MangaSource('test', 'www.test.com', '_')
    cache = seriescache.SeriesCache('title')
    with pytest.raises(TypeError):
        scr.Scraper.chapter_list(cache, source, value)


@pytest.mark.parametrize('value', [500, [], 2.1, {}, 'www.test.com'])
def test_chapter_list_raises_error_for_bad_mangasource(value):
    """Test chapter_list raises a TypeError for bad source."""
    from .context import seriescache
    cache = seriescache.SeriesCache('title')
    with pytest.raises(TypeError):
        scr.Scraper.chapter_list(cache, value)


@pytest.mark.parametrize('value', [500, [], 2.1, {}, 'title'])
def test_chapter_list_raises_error_for_bad_seriescache(value):
    """Test chapter_list raises a TypeError for bad source."""
    from .context import mangasource
    source = mangasource.MangaSource('test', 'www.test.com', '_')
    with pytest.raises(TypeError):
        scr.Scraper.chapter_list(value, source)


def test_chapter_list_raises_error_when_index_not_found(
        dummy_source, filled_cache):
    """Test chapter_list raises ValueError for no index found in source."""
    del filled_cache._chapter_lists[repr(dummy_source)]
    with pytest.raises(ValueError):
        scr.Scraper.chapter_list(filled_cache, dummy_source)


def test_chapter_list_sets_cached_list_to_none_when_index_not_found(
        dummy_source, filled_cache):
    """Test chapter_list sets cached list to None when no index found."""
    del filled_cache._chapter_lists[repr(dummy_source)]
    try:
        scr.Scraper.chapter_list(filled_cache, dummy_source)
    except ValueError:
        assert filled_cache._chapter_lists[repr(dummy_source)] is None
    else:
        assert False  # Did not raise appropriate errpr


def test_chapter_list_uses_cache_list_if_available(filled_cache, dummy_source):
    """Test chapter_list returns the cached chapter list when available."""
    chapters = filled_cache._chapter_lists[repr(dummy_source)]
    assert scr.Scraper.chapter_list(filled_cache, dummy_source) is chapters


def test_chapter_list_builds_list_if_cache_outdated(filled_cache, monkeypatch):
    """Test chapter_list creates a chapter list when outdated."""
    import requests
    from .context import mangasource

    req = requests_patch(text='''<table>
        <a href="/test-series/5">Chapter link 5</a>
        <a href="/test-series/4">Chapter link 4</a>
    </table>''')
    monkeypatch.setattr(requests, 'get', req)

    source = mangasource.MangaSource('old-source', 'http://old.net/', '')
    chapters = filled_cache._chapter_lists[repr(source)]

    new_chapters = scr.Scraper.chapter_list(filled_cache, source)
    assert new_chapters is not chapters


def test_chapter_list_builds_list_if_no_cache_available(
        empty_cache, dummy_source, monkeypatch):
    """Test chapter_list creates a chapter list when outdated."""
    import requests

    req = requests_patch(text='<table><a href="/ch/5">5</a></table>')
    monkeypatch.setattr(requests, 'get', req)

    new_chapters = scr.Scraper.chapter_list(empty_cache, dummy_source)
    assert type(new_chapters) is dict


def test_chapter_list_returns_empty_dict_for_empty_index(
        dummy_source, empty_cache):
    """Test chapter_list gets empty dict for index with no chapters."""
    from datetime import datetime
    now = datetime.utcnow().timestamp()
    empty_cache._index_pages = {
        repr(dummy_source): '<table><a href="/"><No chaps</a></table>'
    }
    empty_cache._last_updated = {repr(dummy_source): now}

    chapters = scr.Scraper.chapter_list(empty_cache, dummy_source)
    assert len(chapters) == 0


def test_chapter_list_finds_all_chapters(various_indexes):
    """Test chapter_list retrieves all chapters from index page."""
    chapters = scr.Scraper.chapter_list(*various_indexes)
    assert len(chapters) == 10


def test_chapter_list_gets_chapter_numbers_for_all_entries(various_indexes):
    """Test chapter_list gets the chapter number from the index entry."""
    chapters = scr.Scraper.chapter_list(*various_indexes)
    assert all(chap.replace('.', '', 1).isdecimal() for chap in chapters)


def test_chapter_list_gets_chapter_number_without_html(various_indexes):
    """Test chapter_list gets the chapter number without any html."""
    chapters = scr.Scraper.chapter_list(*various_indexes)
    assert all('<' not in chap for chap in chapters)


def test_chapter_list_gets_url_for_each_chapter(various_indexes):
    """Test chapter_list gets the url for each chapter."""
    chapters = scr.Scraper.chapter_list(*various_indexes)
    assert all(url.startswith('http') for url in chapters.values())


def test_chapter_list_adds_chapter_list_to_cache_missing_chapters(
        empty_cache, dummy_source, monkeypatch):
    """Test chapter_list adds chapter list to the cache."""
    import requests

    req = requests_patch(text='<table><a href="/ch/5">5</a></table>')
    monkeypatch.setattr(requests, 'get', req)

    new_chapters = scr.Scraper.chapter_list(empty_cache, dummy_source)
    assert repr(dummy_source) in empty_cache._chapter_lists
    assert empty_cache.get_chapter_list(dummy_source) is new_chapters


def test_chapter_list_updates_chapter_list_for_old_cache(
        filled_cache, monkeypatch):
    """Test chapter_list updates chapter list for an outdated cache."""
    import requests

    from .context import mangasource
    source = mangasource.MangaSource('old-source', 'http://old.net/', '')

    req = requests_patch(text='<table><a href="/ch/5">5</a></table>')
    monkeypatch.setattr(requests, 'get', req)

    chapters = filled_cache._chapter_lists[repr(source)]

    scr.Scraper.chapter_list(filled_cache, source)

    assert filled_cache.get_chapter_list(source) is not chapters


@pytest.mark.parametrize('value', [500, [], 2.1, {}])
def test_chapter_pages_raises_error_for_non_string_chapter(value):
    """Test chapter_pages raises a TypeError for bad chapter."""
    from .context import mangasource
    from .context import seriescache
    source = mangasource.MangaSource('test', 'www.test.com', '_')
    cache = seriescache.SeriesCache('title')
    with pytest.raises(TypeError):
        scr.Scraper.chapter_pages(value, cache, source)


@pytest.mark.parametrize('value', [500, [], 2.1, {}, 'title'])
def test_chapter_pages_raises_error_for_bad_seriescache(value):
    """Test chapter_pages raises a TypeError for bad cache."""
    from .context import mangasource
    source = mangasource.MangaSource('test', 'www.test.com', '_')
    with pytest.raises(TypeError):
        scr.Scraper.chapter_pages('http://t.com/', value, source)


@pytest.mark.parametrize('value', [500, [], 2.1, {}, 'www.test.com'])
def test_chapter_pages_raises_error_for_bad_mangasource(value):
    """Test chapter_pages raises a TypeError for bad source."""
    from .context import seriescache
    cache = seriescache.SeriesCache('title')
    with pytest.raises(TypeError):
        scr.Scraper.chapter_pages('http://t.com/', cache, value)


def test_chapter_pages_raises_error_for_empty_chap(empty_cache, dummy_source):
    """Test chapter_pages raises ValueError for empty chapter number."""
    with pytest.raises(ValueError):
        scr.Scraper.chapter_pages('', empty_cache, dummy_source)


def test_chapter_pages_raises_error_for_chapter_not_in_chapter_list(
        empty_cache, dummy_source, monkeypatch):
    """Test chapter_pages raises a KeyError for chapter not in chapter list."""
    import requests

    req = requests_patch(text='<table><a href="/10">Chapter 10</a></table>')
    monkeypatch.setattr(requests, 'get', req)

    with pytest.raises(KeyError):
        scr.Scraper.chapter_pages('1', empty_cache, dummy_source)


def test_chapter_pages_uses_cached_chapter_url_when_available(
        filled_cache, dummy_source, monkeypatch):
    """Test chapter_pages uses cached chapter URL from chapter list cache."""
    import requests

    req = requests_patch(text='<table><a href="/10">Chapter 10</a></table>')
    monkeypatch.setattr(requests, 'get', req)

    chapters = filled_cache.get_chapter_list(dummy_source)

    assert '10' not in chapters and '1' in chapters

    pages = scr.Scraper.chapter_pages('1', filled_cache, dummy_source)

    assert pages is not None
    with pytest.raises(KeyError):
        scr.Scraper.chapter_pages('10', filled_cache, dummy_source)


def test_chapter_pages_gets_new_chapter_url_when_not_available(
        empty_cache, dummy_source, monkeypatch):
    """Test chapter_pages retrieves new chapter list when not available."""
    import requests

    req = requests_patch(text='<table><a href="/10">Chapter 10</a></table>')
    monkeypatch.setattr(requests, 'get', req)

    pages = scr.Scraper.chapter_pages('10', empty_cache, dummy_source)
    assert pages is not None


def test_chapter_pages_updates_chapter_list_cache_when_not_available(
        empty_cache, dummy_source, monkeypatch):
    """Test chapter_pages retrieves new chapter list when not available."""
    import requests

    req = requests_patch(text='<table><a href="/10">Chapter 10</a></table>')
    monkeypatch.setattr(requests, 'get', req)

    assert empty_cache.get_chapter_list(dummy_source) is None

    scr.Scraper.chapter_pages('10', empty_cache, dummy_source)

    assert '10' in empty_cache.get_chapter_list(dummy_source)


def test_chapter_pages_yields_all_images_in_multipage_chapter(
        filled_cache, dummy_source, monkeypatch):
    """Test chapter_pages yeilds all images in multipage source."""
    import requests

    def page_txt(ch_len):
        n = 2
        while True:
            pg = n // 2
            yield f'''
            <a href="/test_series/{pg // ch_len + 1}/page/{pg % ch_len + 1}">
            <img src="https://file.co/img.png">
            </a>'''
            n += 1

    def content():
        n = 1
        while True:
            yield b'\x00' * (n // 2)
            n += 1

    req = requests_patch(text=page_txt(4), content=content())
    monkeypatch.setattr(requests, 'get', req)

    pages = scr.Scraper.chapter_pages('1', filled_cache, dummy_source)
    imgs = [pg for pg in pages]
    assert len(imgs) == 4
    assert imgs[0] != imgs[1] != imgs[2] != imgs[3]


def test_chapter_pages_yields_all_images_in_singlepage_chapter(
        filled_cache, dummy_source, monkeypatch):
    """Test chapter_pages yeilds all images in singlepage source."""
    import requests
    dummy_source.is_multipage = False

    page_txt = '''
    <img src="http://files.co/test.png" id="1">
    <img src="http://files.co/test.png" id="2">
    <img src="http://files.co/test.png" id="3">
    <img src="http://files.co/test.png" id="4">
    '''

    def content():
        n = 0
        while True:
            yield b'\x00' * n
            n += 1

    req = requests_patch(text=page_txt, content=content())
    monkeypatch.setattr(requests, 'get', req)

    pages = scr.Scraper.chapter_pages('1', filled_cache, dummy_source)
    imgs = [pg for pg in pages]
    assert len(imgs) == 4
    assert imgs[0] != imgs[1] != imgs[2] != imgs[3]
