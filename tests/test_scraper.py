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


def test_get_page_has_empty_string_for_next_page_without_a_tag(dummy_source,
                                                               monkeypatch):
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
def test_generate_multipage_chapter_raises_error_for_non_string_chapter(value):
    """Test _generate_multipage_chapter raises a TypeError for bad chapter."""
    from .context import mangasource
    source = mangasource.MangaSource('test', 'www.test.com', '_')
    with pytest.raises(TypeError):
        scr.Scraper._generate_multipage_chapter(value, 'http://t.com/', source)


@pytest.mark.parametrize('value', [500, [], 2.1, {}])
def test_generate_multipage_chapter_raises_error_for_non_string_url(value):
    """Test _generate_multipage_chapter raises a TypeError for bad url."""
    from .context import mangasource
    source = mangasource.MangaSource('test', 'www.test.com', '_')
    with pytest.raises(TypeError):
        scr.Scraper._generate_multipage_chapter('1', value, source)


@pytest.mark.parametrize('value', [500, [], 2.1, {}, 'www.test.com'])
def test_generate_multipage_chapter_raises_error_for_bad_mangasource(value):
    """Test _generate_multipage_chapter raises a TypeError for bad source."""
    with pytest.raises(TypeError):
        scr.Scraper._generate_multipage_chapter('1', 'http://t.com/', value)


def test_generate_multipage_chapter_raises_error_for_empty_chap(dummy_source):
    """Test _generate_multipage_chapter raises ValueError for empty chap."""
    with pytest.raises(ValueError):
        scr.Scraper._generate_multipage_chapter(
            '', 'http://t.com/', dummy_source)


def test_generate_multipage_chapter_raises_error_for_empty_url(dummy_source):
    """Test _generate_multipage_chapter raises ValueError for empty url."""
    with pytest.raises(ValueError):
        scr.Scraper._generate_multipage_chapter(
            '1', '', dummy_source)


def test_generate_multipage_chapter_returns_generator(dummy_source):
    """Test _generate_multipage_chapter returns a generator of tuples."""
    pages = scr.Scraper._generate_multipage_chapter(
            '1', 'http://t.com/001/page/1', dummy_source)
    result = next(pages)
    assert type(result) is tuple


def test_generate_multipage_chapter_yields_image_and_extension(dummy_source):
    """Test _generate_multipage_chapter yeilds image data and extention."""
    pages = scr.Scraper._generate_multipage_chapter(
            '1', 'http://t.com/001/page/1', dummy_source)
    img, ext = next(pages)
    assert img == b'\x00\x00\x00\x00\x00\x00'
    assert ext == 'png'


def test_generate_multipage_chapter_yields_all_images_in_chapter(dummy_source,
                                                                 monkeypatch):
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
            '2', 'http://t.com/2/page/1', dummy_source)
    imgs = [pg for pg in pages]
    assert len(imgs) == 4
    assert imgs[0] != imgs[1] != imgs[2] != imgs[3]


def test_generate_multipage_chapter_works_for_last_chapter(dummy_source,
                                                           monkeypatch):
    """Test _generate_multipage_chapter still works for final chapter."""
    import requests

    def page_txt(ch, ch_len):
        for n in range(2, ch_len * 2):
            pg = n // 2
            yield f'''<a href="/{ch}/page/{pg % ch_len + 1}">
            <img src="https://file.co/img.png">
            </a>'''
        yield f'''<a href="/{ch}/end">
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
            '2', 'http://t.com/2/page/1', dummy_source)
    imgs = [pg for pg in pages]
    assert len(imgs) == 4


@pytest.mark.parametrize('val', [500, [], 2.1, {}])
def test_generate_singlepage_chapter_raises_error_for_non_string_chapter(val):
    """Test _generate_singlepage_chapter raises a TypeError for bad chapter."""
    from .context import mangasource
    source = mangasource.MangaSource('test', 'www.test.com', '_')
    with pytest.raises(TypeError):
        scr.Scraper._generate_singlepage_chapter(
            val, 'http://t.com/', source)


@pytest.mark.parametrize('value', [500, [], 2.1, {}])
def test_generate_singlepage_chapter_raises_error_for_non_string_url(value):
    """Test _generate_singlepage_chapter raises a TypeError for bad url."""
    from .context import mangasource
    source = mangasource.MangaSource('test', 'www.test.com', '_')
    with pytest.raises(TypeError):
        scr.Scraper._generate_singlepage_chapter('1', value, source)


@pytest.mark.parametrize('value', [500, [], 2.1, {}, 'www.test.com'])
def test_generate_singlepage_chapter_raises_error_for_bad_mangasource(value):
    """Test _generate_singlepage_chapter raises a TypeError for bad source."""
    with pytest.raises(TypeError):
        scr.Scraper._generate_singlepage_chapter('1', 'http://t.com/', value)


def test_generate_singlepage_chapter_raises_error_for_empty_chap(dummy_source):
    """Test _generate_singlepage_chapter raises ValueError for empty chap."""
    with pytest.raises(ValueError):
        scr.Scraper._generate_singlepage_chapter(
            '', 'http://t.com/', dummy_source)


def test_generate_singlepage_chapter_raises_error_for_empty_url(dummy_source):
    """Test _generate_singlepage_chapter raises ValueError for empty url."""
    with pytest.raises(ValueError):
        scr.Scraper._generate_singlepage_chapter(
            '1', '', dummy_source)


def test_generate_singlepage_chapter_returns_generator(dummy_source):
    """Test _generate_singlepage_chapter returns a generator of tuples."""
    pages = scr.Scraper._generate_singlepage_chapter(
            '1', 'http://t.com/001/page/1', dummy_source)
    result = next(pages)
    assert type(result) is tuple


def test_generate_singlepage_chapter_yields_image_and_extension(dummy_source):
    """Test _generate_singlepage_chapter yeilds image data and extention."""
    pages = scr.Scraper._generate_singlepage_chapter(
            '1', 'http://t.com/001/page/1', dummy_source)
    img, ext = next(pages)
    assert img == b'\x00\x00\x00\x00\x00\x00'
    assert ext == 'png'


def test_generate_singlepage_chapter_yields_all_images_in_chapter(dummy_source,
                                                                  monkeypatch):
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
            '2', 'http://t.com/1', dummy_source)
    imgs = [pg for pg in pages]
    assert len(imgs) == 4
    assert imgs[0] != imgs[1] != imgs[2] != imgs[3]
