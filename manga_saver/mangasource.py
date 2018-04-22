"""A source website from which to pull manga."""
import requests

import re
import urllib


class MangaSource(object):
    """Details for a source website."""

    def __init__(self, name, root_url, slug_filler):
        """Set up details for a new source."""
        if not all(type(arg) is str for arg in (name, root_url, slug_filler)):
            raise TypeError('Must construct a MangaSource with strings.')

        if not all((name, root_url)):
            raise ValueError('Cannot use empty strings for a MangaSource.')

        self.name = name

        if not root_url.startswith('http'):
            root_url = 'http://' + root_url
        if not root_url.endswith('/'):
            root_url += '/'

        valid_url = re.fullmatch(r'^https?://[^\s/$.?#].[^\s]*$',
                                 root_url, flags=re.I)
        if not valid_url:
            raise ValueError(f'{root_url} if not a valid url.')

        self.root_url = root_url

        self.slug_filler = slug_filler

    def __repr__(self):
        """Display the name and url for the source."""
        return f'<MangaSource: {self.name} @ {self.root_url}>'

    def __str__(self):
        """Display the name of the source."""
        return self.name

    def _get_slug(self, s):
        """Get the slug of the given string for the URL."""
        if type(s) is not str:
            raise TypeError('Can only slugify a string.')
        clean_s = re.sub(r'[^0-9a-zA-Z ]', '', s.lower())
        return clean_s.replace(' ', self.slug_filler)

    def index_url(self, title):
        """Get the URL for the index of the given title."""
        if type(title) is not str:
            raise TypeError('Manga title must be a string.')

        slug = self._get_slug(title)
        return urllib.parse.urljoin(self.root_url, slug)

    def ping(self):
        """Ping the source website to verify it is online."""
        try:
            response = requests.head(self.root_url)
        except requests.exceptions.RequestException:
            return False

        if response.status_code >= 400:
            return False

        return True
