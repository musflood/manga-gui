"""Model for a single series of manga to allow caching of index pages."""
from datetime import datetime

from manga_saver.mangasource import MangaSource

import requests


class SeriesCache(object):
    """The cache for a manga series.

    Attributes:
        title: The title of the series.

    """

    def __init__(self, title):
        """Set up a new empty cache."""
        if type(title) is not str:
            raise TypeError('title must be a string.')
        if not title:
            raise ValueError('title cannot be an empty string.')

        self.title = title
        self._index_pages = {}
        self._custom_urls = {}
        self._last_updated = {}

    def __repr__(self):
        """Display the name and cache size of the series."""
        cache_size = len(self._index_pages)
        return f'<SeriesCache: {self.title}, cache: {cache_size} sources>'

    def __str__(self):
        """Display the name of the series."""
        return self.title

    def update_index(self, source, index_url=None):
        """Store the html for the index page at a source.

        Provide a index_url to set a custom URL for this source.
        Only necessary if the generated URL for this series fails.
        """
        if not isinstance(source, MangaSource):
            raise TypeError('source must be a MangaSource.')
        if index_url and type(index_url) is not str:
            raise TypeError('URL must be a string.')

        src_name = repr(source)

        if index_url:
            self._custom_urls[src_name] = index_url

        elif src_name in self._custom_urls:
            index_url = self._custom_urls[src_name]

        else:
            index_url = source.index_url(self.title)

        res = requests.get(index_url)

        self._index_pages[src_name] = res.text
        now = datetime.utcnow().timestamp()
        self._last_updated[src_name] = now

    def get_index(self, source, index_url=None, update_interval=21600):
        """Get the html for the index page at a source.

        Also updates the stored html for a source if the update
        interval has elapsed. Default is 21600 seconds, or 6 hours.
        """
        if not isinstance(source, MangaSource):
            raise TypeError('source must be a MangaSource.')
        if index_url and type(index_url) is not str:
            raise TypeError('URL must be a string.')

        now = datetime.utcnow().timestamp()
        if now - self._last_updated[repr(source)] > update_interval:
            self.update_index(source, index_url)

        return self._index_pages[repr(source)]
