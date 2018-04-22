"""Tests for the scraper module."""
from bs4 import BeautifulSoup
import pytest

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
    """Test that _pull_page_image returns image tag for one page source."""
    dummy_source.is_multipage = False
    _, _, tag = scr.Scraper._pull_page_image(dummy_soup, dummy_source)
    assert tag.name == 'img'


def test_pull_page_image_takes_first_image_from_soup(dummy_soup, dummy_source):
    """Test that _pull_page_image removes first image from soup."""
    assert len(dummy_soup.find_all('img')) == 4
    _, _, tag = scr.Scraper._pull_page_image(dummy_soup, dummy_source)
    assert len(dummy_soup.find_all('img')) == 3
    assert tag.img['id'] == '1'
