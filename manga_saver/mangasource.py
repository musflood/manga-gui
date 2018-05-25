"""A source website from which to pull manga."""
import re
import urllib

import requests


class MangaSource(object):
    """Details for a source website.

    Attributes:
        name: Readable name for the source.
        root_url: URL for a series index, without the title.
        slug_filler: Character used for spaces in the slug.

        is_multipage: Whether the source has each page image on its
            own webpage or not.
        pg_img_attrs: Additional attributes on the HTML tag that contains
            the page image.
        index_tag: The HTML tag that contains the table of contents on
            the index page for a series.
        index_attrs: Additional attributes on the HTML tag that contains
            the table of contents on the index page for a series.

    """

    def __init__(self, name, root_url, slug_filler, is_multipage=True,
                 pg_img_attrs=None, index_tag='table', index_attrs=None):
        """Set up details for a new source.

        Args:
            name: Name to be displayed to the user.
            root_url: URL for a series index, without the title.
            slug_filler: Character used for spaces in the slug for a title.

            is_multipage: (optional) Whether the source has each page image
                on its own webpage or not.
            pg_img_attrs: (optional) Additional attributes on the HTML tag
                that contains the page image. Must be provided in a dict.
            index_tag: (optional) The HTML tag that contains the table of
                contents on the index page for a series.
            index_attrs: (optional) Additional attributes on the HTML tag
                that contains the table of contents on the index page
                for a series. Must be provided in a dict.

        Raises:
            TypeError: For non-string arguments.
            ValueError: For empty name or root_url and for invalid root_url.

        """
        if not all(type(arg) is str for arg in
                   (name, root_url, slug_filler, index_tag)):
            raise TypeError('Must construct a MangaSource with strings.')

        if not all((name, root_url, index_tag)):
            raise ValueError('Cannot use empty strings for a MangaSource.')

        if pg_img_attrs is not None and type(pg_img_attrs) is not dict:
            raise TypeError('Tag attributes must be given as a dict.')

        if index_attrs is not None and type(index_attrs) is not dict:
            raise TypeError('Tag attributes must be given as a dict.')

        # Fundamental source identifiers
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
        self._verified = self.ping()

        self.slug_filler = slug_filler

        # Details for parsing page and chapter HTML
        self.is_multipage = is_multipage

        self.pg_img_attrs = pg_img_attrs

        self.index_tag = index_tag
        self.index_attrs = index_attrs

    def __repr__(self):
        """Display the name and url for the source."""
        return f'<MangaSource: {self.name} @ {self.root_url}>'

    def __str__(self):
        """Display the name of the source."""
        return self.name

    def _slugify(self, s):
        """Get the slug of the given string for the URL."""
        if type(s) is not str:
            raise TypeError('Can only slugify a string.')

        clean_s = re.sub(r'[^0-9a-zA-Z ]', '', s.strip().lower())
        return clean_s.replace(' ', self.slug_filler)

    def index_url(self, title):
        """Get the URL for the index of the given title."""
        if type(title) is not str:
            raise TypeError('Manga title must be a string.')

        slug = self._slugify(title)
        return urllib.parse.urljoin(self.root_url, slug)

    def ping(self):
        """Ping the source website to verify it is online.

        Returns:
            True for 200 and 300 level status codes.
            False for 400 and 500 level status codes and for
            timeout or other errors.

        """
        try:
            response = requests.head(self.root_url)
        except requests.exceptions.RequestException:
            return False

        if response.status_code >= 400:
            return False

        return True
