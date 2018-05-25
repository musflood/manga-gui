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
    def chapter_list(cls, series, source, index_url=None):
        """Get a dict of chapter numbers and links to the first, or only page.

        Args:
            series: The SeriesCache of the series for the chapter.
            source: The MangaSource to get the chapter from.
            index_url: (optional) A custom URL for the index of the series.

        Returns:
            A dictionary of the chapter number as a string and the link.

        Raises:
            TypeError: For improperly typed arguments.
            ValueError: For a source that is missing the index element.

        """
        if not isinstance(series, SeriesCache):
            raise TypeError('Given series must be a SeriesCache.')
        if not isinstance(source, MangaSource):
            raise TypeError('Given source must be a MangaSource.')
        if index_url and type(index_url) is not str:
            raise TypeError('URL must be a string.')

        index_html = series.get_index(source, index_url)
        index_html = BeautifulSoup(index_html, 'html.parser')
        index_html = index_html.find(source.index_tag,
                                     attrs=source.index_attrs)

        if not index_html:
            raise ValueError('No chapter list found in source.')

        chapter_re = re.compile(r'(\D|\b)\d+(\D|\b)')

        def chapter_anchor_tag(tag):
            if tag.name != 'a':
                return False

            contents = ''.join(s for s in tag.stripped_strings)
            has_correct_contents = chapter_re.search(contents)

            return has_correct_contents

        chap_links = index_html.findAll(chapter_anchor_tag)

        find_ch = cls._make_chapter_finder(series.title)

        return {find_ch(tag.text): tag['href'] for tag in chap_links}

    @classmethod
    def _make_chapter_finder(cls, series_title):
        """Make a function that finds the chapter number in an index entry."""
        if type(series_title) is not str:
            raise TypeError('Series title must be a string.')

        number_re = re.compile(r'\d+\.\d+|\d+')
        chapter_re = re.compile(r'\bch.*?\b(\d+\.\d+|\d+)')

        def chapter_number(text):
            text = text.lower()
            text = text.replace(series_title.lower(), '', 1)

            numbers = number_re.findall(text)
            if not numbers:
                raise ValueError('Index entry has no chapter number.')

            if len(numbers) == 1:
                return numbers[0].lstrip('0')

            ch_numbers = chapter_re.findall(text)
            if ch_numbers:
                return ch_numbers[0].lstrip('0')

            return numbers[0].lstrip('0')

        return chapter_number

    @classmethod
    def chapter_pages(cls, chapter_url, source):
        """Generate the pages for a chapter of the series from a source.

        Args:
            chapter_url: The URL of the first or only page of the chapter.
            source: The MangaSource to get the chapter from.

        Yields:
            A tuple of the page image data and file extension.

        Raises:
            TypeError: For improperly typed arguments.
            ValueError: For empty chapter.

        """
        if type(chapter_url) is not str:
            raise TypeError('Chapter URL must be a string.')
        if not isinstance(source, MangaSource):
            raise TypeError('Given source must be a MangaSource.')
        if not chapter_url:
            raise ValueError('Cannot use an empty string for chapter URL.')

        if source.is_multipage:
            pages = cls._generate_multipage_chapter(chapter_url, source)
        else:
            pages = cls._generate_singlepage_chapter(chapter_url, source)

        def gen(pages):
            for page in pages:
                yield page

        return gen(pages)

    @classmethod
    def _generate_multipage_chapter(cls, url, source):
        """Generate all the image data for the pages of a multipage source.

        Args:
            url: The link to the first page of the chapter.
            source: The MangaSource this link came from.

        Yields:
            A tuple of the page image data and file extension.

        Raises:
            TypeError: For improperly typed arguments.
            ValueError: For empty chapter or url.

        """
        if type(url) is not str:
            raise TypeError('URL must be a string.')
        if not isinstance(source, MangaSource):
            raise TypeError('Given source must be a MangaSource.')
        if not url:
            raise ValueError('Cannot use an empty strings for URL.')

        def gen(url):
            base_url, end = url.rstrip('/').rsplit('/', 1)

            dashed_number = re.match(r'^\d*(-|_)\d*$', end)
            if dashed_number:
                base_end = end.split(dashed_number.groups()[0])[0]
                base_url += f'/{base_end}'

            while base_url in url:
                try:
                    data, ext, url, _ = cls._get_page(url, source)
                except ValueError:
                    break
                yield data, ext
        return gen(url)

    @classmethod
    def _generate_singlepage_chapter(cls, url, source):
        """Generate all the image data for the pages of a singlepage source.

        Args:
            url: The link to the chapter page with page images.
            source: The MangaSource this link came from.

        Yields:
            A tuple of the page image data and file extension.

        Raises:
            TypeError: For improperly typed arguments.
            ValueError: For empty chapter or url.

        """
        if type(url) is not str:
            raise TypeError('URL must be a string.')
        if not isinstance(source, MangaSource):
            raise TypeError('Given source must be a MangaSource.')
        if not url:
            raise ValueError('Cannot use an empty strings for URL.')

        def gen():
            data, ext, _, html = cls._get_page(url, source)
            yield data, ext

            while html.find('img', attrs=source.pg_img_attrs):
                yield cls._pull_page_image(html, source)[:2]
        return gen()

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
