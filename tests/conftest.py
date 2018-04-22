"""Fixtures for testing the manga_saver package."""
from bs4 import BeautifulSoup
import pytest
import requests

from .context import mangasource as ms


TEST_PAGE = '''
<select>
    <option>1</option>
    <option>2</option>
    <option>3</option>
    <option>4</option>
</select>

<a href="/next/page"><img src="http://files.co/test.png" id="1"></a>
<a href="/next/page"><img src="http://files.co/test.png" id="2"></a>
<a href="/next/page"><img src="http://files.co/test.png" id="3"></a>
<a href="/next/page"><img src="http://files.co/test.png" id="4"></a>
'''


@pytest.fixture(autouse=True)
def offline_requests(monkeypatch):
    """Ensure that no HTTP requests are made when pinging URLs."""
    def req(url):
        if not url.startswith('http'):
            raise requests.exceptions.MissingSchema

        class Response(object):
            status_code = 200
            text = TEST_PAGE
            content = b'\x00\x00\x00\x00\x00\x00'

        return Response

    monkeypatch.setattr(requests, 'head', req)
    monkeypatch.setattr(requests, 'get', req)


@pytest.fixture
def dummy_source():
    """Create a basic MangaSource."""
    return ms.MangaSource('test source', 'http://www.source.com/', '_')


@pytest.fixture(params=[400, 403, 404, 500, 'error'])
def fail_response(request):
    """Create a Response with a failing status code or exception."""
    def req(url):
        if request.param == 'error':
            from requests.exceptions import ConnectionError
            raise ConnectionError

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
