"""Fixtures for testing the manga_saver package."""
from .context import mangasource as ms

import pytest


@pytest.fixture
def source():
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
