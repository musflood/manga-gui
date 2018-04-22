"""Scraper to pull chapter images from a source."""
import urllib

from bs4 import BeautifulSoup
import requests

from manga_saver.mangasource import MangaSource


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
