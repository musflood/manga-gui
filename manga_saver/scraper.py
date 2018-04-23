"""Scraper to pull chapter images from a source."""
import re
import urllib

from bs4 import BeautifulSoup
import requests

from manga_saver.mangasource import MangaSource
from manga_saver.seriescache import SeriesCache


class Scraper(object):
    """Scraper that pulls page images from a source."""

    @classmethod
    def _pull_page_image(cls, html, source):
        """Pull the page image from the given HTML.

        Note that the image element returned by this method is
        removed from the BeautifulSoup passed in as html.

        Args:
            html: A BeautifulSoup of the HTML to search.
            source: The MangaSource this HTML came from.

        Returns:
            A tuple of the image data in a byte-string, the file
            extension for the image as a string, and the BeautifulSoup
            element that held the page image. This element will be
            the anchor tag around the image tag for a multipage source.

        Raises:
            TypeError: For improperly typed arguments.
            ValueError: For HTML that has no page image or the page
                image has no source to get image data from.

        """
        if not isinstance(html, BeautifulSoup):
            raise TypeError('link must be a string.')
        if not isinstance(source, MangaSource):
            raise TypeError('source must be a MangaSource.')

        imgs = html.findAll('img', attrs=source.pg_img_attrs)

        if not imgs:
            raise ValueError('Webpage has no page image.')

        img_tag = imgs[0]

        try:
            img_link = img_tag['src']
        except KeyError:
            raise ValueError('Page image has no source.')

        if img_link.startswith('//'):
            img_link = 'http:' + img_link

        ext = img_link.rsplit('.', 1)[-1]

        image_data = requests.get(img_link).content

        if source.is_multipage and img_tag.find_parent('a'):
            img_tag = img_tag.find_parent('a')

        img_tag = img_tag.extract()

        return image_data, ext, img_tag

    @classmethod
    def _get_page(cls, url, source):
        """Get and parse a page of a chapter.

        Works for both multipage and singlepage sources.

        Args:
            url: The link to the page, or only page, of the chapter.
            source: The MangaSource this link came from.

        Returns:
            A tuple of the page image, the file extention for that image,
            the URL for the next page, and the BeautifulSoup of the
            current page.

        Raises:
            TypeError: For improperly typed arguments
            ValueError: For an invlid URL.

        """
        if type(url) is not str:
            raise TypeError('Given URL must be a string.')
        if not isinstance(source, MangaSource):
            raise TypeError('Given source must be a MangaSource.')

        try:
            res = requests.get(url)
        except requests.exceptions.RequestException:
            raise ValueError('Invalid URL given for page.')

        html = BeautifulSoup(res.text, 'html.parser')

        data, ext, tag = cls._pull_page_image(html, source)

        try:
            next_page = tag['href']
            next_page = urllib.parse.urljoin(url, next_page)
        except KeyError:
            next_page = ''

        return data, ext, next_page, html

    @classmethod
    def _generate_multipage_chapter(cls, chapter, url, source):
        """Generate all the image data for the pages of a multipage source.

        Args:
            chapter: The number of the chapter being generated.
            url: The link to the first page of the chapter.
            source: The MangaSource this link came from.

        Yields:
            A tuple of the page image data and file extension.

        Raises:
            TypeError: For improperly typed arguments.
            ValueError: For empty chapter or url.

        """
        if not all(type(arg) is str for arg in (chapter, url)):
            raise TypeError('Chapter and URL must be strings.')
        if not isinstance(source, MangaSource):
            raise TypeError('Given source must be a MangaSource.')
        if not all((chapter, url)):
            raise ValueError('Cannot use empty strings for chapter or URL.')

        def gen(url):
            while chapter in url:
                data, ext, url, _ = cls._get_page(url, source)
                yield data, ext
        return gen(url)

    @classmethod
    def _generate_singlepage_chapter(cls, chapter, url, source):
        """Generate all the image data for the pages of a singlepage source.

        Args:
            chapter: The number of the chapter being generated.
            url: The link to the chapter page with page images.
            source: The MangaSource this link came from.

        Yields:
            A tuple of the page image data and file extension.

        Raises:
            TypeError: For improperly typed arguments.
            ValueError: For empty chapter or url.

        """
        if not all(type(arg) is str for arg in (chapter, url)):
            raise TypeError('Chapter and URL must be strings.')
        if not isinstance(source, MangaSource):
            raise TypeError('Given source must be a MangaSource.')
        if not all((chapter, url)):
            raise ValueError('Cannot use empty strings for chapter or URL.')

        def gen():
            data, ext, _, html = cls._get_page(url, source)
            yield data, ext

            while html.find('img', attrs=source.pg_img_attrs):
                yield cls._pull_page_image(html, source)[:2]
        return gen()

    @classmethod
    def _get_chapter_link(cls, series, chapter, source, index_url=None):
        """Get the link to the first page of the chapter from the index.

        Args:
            series: The SeriesCache of the series for the chapter.
            chapter: The chapter of the series, as a string.
            source: The MangaSource to get the chapter from.
            index_url: (optional) A custom URL for the index of the series.

        Returns:
            The link to the first page of the chapter.

        Raises:
            TypeError: For improperly typed arguments.
            ValueError: For empty chapter or invalid chapter.

        """
        if not isinstance(series, SeriesCache):
            raise TypeError('Given series must be a SeriesCache.')
        if type(chapter) is not str:
            raise TypeError('Chapter must be a string.')
        if not isinstance(source, MangaSource):
            raise TypeError('Given source must be a MangaSource.')
        if index_url and type(index_url) is not str:
            raise TypeError('URL must be a string.')
        if not chapter:
            raise ValueError('Cannot use empty string for chapter.')

        index_html = series.get_index(source, index_url)
        index_html = BeautifulSoup(index_html, 'html.parser')

        index_url = index_url.rstrip('/')
        slug = index_url.rsplit('/', 1)[1]

        chap_re = f'{slug}/{chapter}'
        chap_link = index_html.find('a', href=re.compile(f'{chap_re}$'))
        if not chap_link:
            chap_link = index_html.find('a', href=re.compile(f'{chap_re}/'))

        if not chap_link:
            raise ValueError(f'Chapter {chapter} is not available.')

        return chap_link['href']

    @classmethod
    def chapter_pages(cls, series, chapter, source, index_url=None):
        """Generate the pages for a chapter of the series from a source.

        Args:
            series: The SeriesCache of the series for the chapter.
            chapter: The chapter of the series, as a string.
            source: The MangaSource to get the chapter from.
            index_url: (optional) A custom URL for the index of the series.

        Yields:
            A tuple of the page image data and file extension.

        Raises:
            TypeError: For improperly typed arguments.
            ValueError: For empty chapter.

        """
        if not isinstance(series, SeriesCache):
            raise TypeError('Given series must be a SeriesCache.')
        if type(chapter) is not str:
            raise TypeError('Chapter must be a string.')
        if not isinstance(source, MangaSource):
            raise TypeError('Given source must be a MangaSource.')
        if index_url and type(index_url) is not str:
            raise TypeError('URL must be a string.')
        if not chapter:
            raise ValueError('Cannot use empty string for chapter.')

        url = cls._get_chapter_link(series, chapter, source, index_url)

        if source.is_multipage:
            pages = cls._generate_multipage_chapter(chapter, url, source)
        else:
            pages = cls._generate_singlepage_chapter(chapter, url, source)

        def gen(pages):
            for page in pages:
                yield page

        return gen(pages)
