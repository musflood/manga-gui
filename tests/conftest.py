"""Fixtures for testing the manga_saver package."""
from datetime import datetime

from bs4 import BeautifulSoup
import pytest
import requests

from .context import mangasource
from .context import seriescache


TEST_PAGE = '''
<head>{}</head>
<body>
<select>
    <option>1</option>
    <option>2</option>
    <option>3</option>
    <option>4</option>
</select>

<a href="/001/page/2"><img src="http://files.co/test.png" id="1"></a>
<a href="/001/page/3"><img src="http://files.co/test.png" id="2"></a>
<a href="/001/page/4"><img src="http://files.co/test.png" id="3"></a>
<a href="/002/page/1"><img src="http://files.co/test.png" id="4"></a>
</body>
'''


def requests_patch(**kwargs):
    """Patch for any requests method."""
    def req(url):
        if not url.startswith('http'):
            raise requests.exceptions.MissingSchema

        class Response(object):
            def __init__(self, **kwargs):
                for key, value in kwargs.items():
                    try:
                        value = next(value)
                    except TypeError:
                        try:
                            value = value(url)
                        except TypeError:
                            pass
                    setattr(self, key, value)

        return Response(**kwargs)

    return req


@pytest.fixture(autouse=True)
def offline_requests(monkeypatch):
    """Ensure that no HTTP requests are made when pinging URLs."""
    req = requests_patch(status_code=200, text=TEST_PAGE.format,
                         content=b'\x00\x00\x00\x00\x00\x00')

    monkeypatch.setattr(requests, 'head', req)
    monkeypatch.setattr(requests, 'get', req)


@pytest.fixture
def dummy_source():
    """Create a basic MangaSource."""
    return mangasource.MangaSource(
        'test source', 'http://www.source.com/', '_')


@pytest.fixture(params=[400, 403, 404, 500, 'error'])
def fail_response(request):
    """Create a Response with a failing status code or exception."""
    def req(url):
        if request.param == 'error':
            raise requests.exceptions.ConnectionError

        class Response(object):
            status_code = request.param

        return Response

    return req


@pytest.fixture(params=[200, 302])
def conn_response(request):
    """Create a Response with a connected status code."""
    def req(url):
        class Response(object):
            status_code = request.param

        return Response

    return req


@pytest.fixture
def dummy_soup():
    """Create a BeautifulSoup from offline_requests text."""
    return BeautifulSoup(TEST_PAGE, 'html.parser')


@pytest.fixture
def empty_cache():
    """Create an empty series cache."""
    return seriescache.SeriesCache('empty test')


@pytest.fixture
def filled_cache(dummy_source):
    """Create an filled series cache.

    Has data for the following:
        dummy_source -> Chp 1 only, last updated now
        MangaSource: -> Chps 4 and 5, last updated 2 hours ago
            name: source2
            url: http://www.another.com/
            slug: -
        MangaSource: -> No chapters, last updated 12 hours ago, custom url
            name: old-source
            url: http://old.net/
            slug:
    """
    now = datetime.utcnow().timestamp()

    cache = seriescache.SeriesCache('test series')
    cache._index_pages = {
        repr(dummy_source): '<a href="/test_series/1">Chapter link</a>',
        '<MangaSource: source2 @ http://www.another.com/>': '''
            <a href="/test-series/5">Chapter link</a>
            <a href="/test-series/4">Chapter link</a>''',
        '<MangaSource: old-source @ http://old.net/>': '<p>No chapters</p>'
    }
    cache._custom_urls = {
        '<MangaSource: source2 @ http://www.another.com/>':
            'http://another.net/TestSeries',
        '<MangaSource: old-source @ http://old.net/>':
            'https://old.chap.net/TestSeries'
    }
    cache._last_updated = {
        repr(dummy_source): now,
        '<MangaSource: source2 @ http://www.another.com/>': now - 7200,
        '<MangaSource: old-source @ http://old.net/>': now - 43200
    }

    return cache
