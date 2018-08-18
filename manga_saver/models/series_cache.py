"""Model for a single series of manga to allow caching of index pages."""
from datetime import datetime
import re

from manga_saver.models.manga_source import MangaSource

import requests


class SeriesCache(object):
    """The cache for a manga series.

    Attributes:
        title: The title of the series.

    """

    def __init__(self, title, update_interval=21600):
        """Set up a new empty cache.

        Update interval is used to determine when a cache is outdated.
        Default is 21600 seconds, or 6 hours.
        """
        if type(title) is not str:
            raise TypeError('title must be a string.')
        if not title:
            raise ValueError('title cannot be an empty string.')
        if type(update_interval) is not int:
            raise TypeError('Update interval must be an integer.')
        if update_interval < 0:
            raise ValueError('Update interval cannot be negative.')

        self.title = title
        self._update_interval = update_interval

        self._index_pages = {}
        self._chapter_lists = {}
        self._custom_urls = {}
        self._last_updated = {}

    def __repr__(self):
        """Display the name and cache size of the series."""
        return f'<SeriesCache: {self.title}, cache: {len(self)} sources>'

    def __str__(self):
        """Display the name of the series."""
        return self.title

    def __len__(self):
        """Get the number of sources in the series cache."""
        return len(self._index_pages)

    def __contains__(self, item):
        """Check if the item is in the cache."""
        return repr(item) in self._index_pages

    def has_outdated_cache(self, source):
        """Check if cache for a source is older than the update interval."""
        if not isinstance(source, MangaSource):
            raise TypeError('source must be a MangaSource.')

        now = datetime.utcnow().timestamp()

        last_update = self._last_updated[repr(source)] if source in self else 0
        return now - last_update > self._update_interval

    def update_index(self, source, index_url=None):
        """Store the html for the index page at a source.

        Provide a index_url to set a custom URL for this source.
        Only necessary if the generated URL for this series fails.
        """
        if not isinstance(source, MangaSource):
            raise TypeError('source must be a MangaSource.')
        if index_url is not None and type(index_url) is not str:
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
        self._last_updated[src_name] = datetime.utcnow().timestamp()

    def get_index(self, source, index_url=None):
        """Get the html for the index page at a source.

        Also updates the stored html for a source if the update
        interval has elapsed. Default is 21600 seconds, or 6 hours.
        """
        if not isinstance(source, MangaSource):
            raise TypeError('source must be a MangaSource.')
        if index_url is not None and type(index_url) is not str:
            raise TypeError('URL must be a string.')

        is_new_url = index_url and self._custom_urls[repr(source)] != index_url

        if is_new_url or self.has_outdated_cache(source):
            self.update_index(source, index_url)

        return self._index_pages[repr(source)]

    def set_chapter_list(self, source, chapter_list):
        """Store the chapter list at a source.

        chapter_list must be a dictionary with a string of the chapter number
        as the key and the URL to the first or only page of the chapter
        as the value.
        """
        if not isinstance(source, MangaSource):
            raise TypeError('source must be a MangaSource.')
        if source not in self:
            raise ValueError(
                'Cannot set chapter list for source without index.')

        number_re = re.compile(r'\d+\.\d+|\d+')
        if chapter_list is not None and type(chapter_list) is not dict:
            raise TypeError('chapter_list must be a dictionary.')
        if not all(type(key) is str and number_re.fullmatch(key)
                   for key in (chapter_list if chapter_list else [])):
            raise ValueError('Improperly formatted chapter numbers.')
        if not all(type(val) is str and val.startswith('http')
                   for val in (chapter_list.values() if chapter_list else [])):
            raise ValueError('Improperly formatted chapter URLs.')

        self._chapter_lists[repr(source)] = chapter_list

    def get_chapter_list(self, source):
        """Get the chapter list at a source.

        If the cache is out of date for the source, always returns None.
        Default is 21600 seconds, or 6 hours.
        """
        if not isinstance(source, MangaSource):
            raise TypeError('source must be a MangaSource.')

        if self.has_outdated_cache(source):
            return

        return self._chapter_lists.get(repr(source), None)
