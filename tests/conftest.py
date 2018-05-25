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


@pytest.fixture(params=[
    {'tag': 'table', 'attr': {'class': 'table'}, 'index':
     """<div class="col-sm-8">

    <h1>My Hero Academia</h1>

    <table class="table table-striped">
        <tbody><tr>
            <th style="width: 70%">Chapter</th>
            <th style="width: 30%">Released</th>
        </tr>
                <tr>
                <td><a href="/r/my_hero_academia/182/5059/1">182 - Discharge! The Culture Festival!</a></td>
                <td>May 11th, 2018</td>
            </tr>
                <tr>
                <td><a href="/r/my_hero_academia/181/5048/1">181 - For Another's Sake</a></td>
                <td>Apr 29th, 2018</td>
            </tr>
                <tr>
                <td><a href="/r/my_hero_academia/180/5028/1">180 - Secret</a></td>
                <td>Apr 20th, 2018</td>
            </tr>
                <tr>
                <td><a href="/r/my_hero_academia/179/5017/1">179 - The Culture Festival commences!</a></td>
                <td>Apr 13th, 2018</td>
            </tr>
                <tr>
                <td><a href="/r/my_hero_academia/178/5001/1">178 - The Girl Named LoveLover</a></td>
                <td>Apr 6th, 2018</td>
            </tr>
                <tr>
                <td><a href="/r/my_hero_academia/177/4990/1">177 - At the Construction Site</a></td>
                <td>Mar 30th, 2018</td>
            </tr>
                <tr>
                <td><a href="/r/my_hero_academia/176/4973/1">176 - Deku vs. Gentle Criminal</a></td>
                <td>Mar 23rd, 2018</td>
            </tr>
                <tr>
                <td><a href="/r/my_hero_academia/175/4961/1">175 - Morning of the Big Day</a></td>
                <td>Mar 16th, 2018</td>
            </tr>
                <tr>
                <td><a href="/r/my_hero_academia/174/4944/1">174 - Gold-Tips Imperial</a></td>
                <td>Mar 9th, 2018</td>
            </tr>
                <tr>
                <td><a href="/r/my_hero_academia/173/4935/1">173 - The Funnest Part of Culture Festivals is Preparing for Them! Part 2</a></td>
                <td>Mar 3rd, 2018</td>
            </tr>
        </tbody></table>

    <p>
        <strong>Where's the complete list?</strong><br>
        In respect to the publishers, we only translate and host a small number of the most recent chapters for any series
        that will have an English volume released at some point. We encourage you to go out and support the growth of the industry by
        purchasing these volumes if you're able to.
        <br><br>

        Don't miss a release! Check Manga Stream every week and read your favorite series in glorious uncompressed high quality
        before we remove the chapters.
    </p><div class="modal fade" tabindex="-1" role="dialog" id="login-modal">
        <div class="modal-dialog" role="document">
            <div class="modal-content">
                <div class="modal-header">
                    <button type="button" class="close" data-dismiss="modal" aria-label="Close"><span aria-hidden="true">×</span></button>
                    <h4 class="modal-title">Log into MangaStream account</h4>
                </div>
                <div class="modal-body">
                    <p class="info">
                        Don't have an account yet? <a href="javascript:;" id="login-to-register">Create one</a> now, it's free and quick!
                    </p>

                    <form class="login-form" novalidate="novalidate">
                        <div class="form-group">
                            <label for="email">Email</label>
                            <input type="email" class="form-control" id="login-email" placeholder="Your registered email address" required="">
                            <span class="login-error" id="login-email-required">Your email is required, please fill out this field.</span>
                        </div>
                        <div class="form-group">
                            <label for="password">Password</label>
                            <input type="password" class="form-control" id="login-password" placeholder="Password" required="">
                            <span class="login-error" id="login-password-required">Password is required, please fill out this field.</span>
                        </div>

                        <div class="login-error" id="login-error">The email/password you entered doesn't match anything in our records, check your details.</div>

                        <button type="submit" class="btn btn-default" id="login-btn">Log in</button>

                        <a href="javascript:;" id="login-to-forgot">I forgot my password</a>
                    </form>
                </div>

                <div class="external">
                    <a class="google-launch" id="google-launch" href="javascript:;"><i class="fa fa-google"></i> Google</a>
                    <a class="facebook-launch" href="javascript:;"><i class="fa fa-facebook"></i> Facebook</a>
                    <a class="twitter-launch" href="javascript:;"><i class="fa fa-twitter"></i> Twitter</a>
                </div>
            </div>
        </div>
    </div>
    <div class="modal fade" tabindex="-1" role="dialog" id="register-modal">
        <div class="modal-dialog" role="document">
            <div class="modal-content">
                <div class="modal-header">
                    <button type="button" class="close" data-dismiss="modal" aria-label="Close"><span aria-hidden="true">×</span></button>
                    <h4 class="modal-title">Account Registration</h4>
                </div>
                <div class="modal-body">
                    <p class="info">
                        Making an account on MangaStream is fast and easy. Your account lets you comment on releases &amp; news,
                        and you can show your support by subscribing (ad-free MangaStream!). Already have an account? <a href="javascript:;" id="register-to-login">please log in </a> instead.
                    </p>

                    <div id="register-external">
                        You are about to link a third party social media account to a new MangaStream account. Once you
                        make the account, you can use your social media account to log in instantly in the future. If you
                        already have a MangaStream account, log in and link the social media account from your settings.
                    </div>

                    <form class="register-form" novalidate="novalidate">
                        <div class="form-group">
                            <label for="username">Username</label>
                            <input type="text" class="form-control" maxlength="28" id="username" placeholder="Desired username (publicly viewable)" required="">
                            <span class="register-error" id="username-unique">That username is already taken. Please choose something different.</span>
                            <span class="register-error" id="username-required">Username is required, please fill out this field.</span>
                            <span class="register-error" id="username-gte">Username must be at least 3 characters long.</span>
                            <span class="register-error" id="username-lte">Username cannot be more than 28 characters long.</span>
                            <span class="register-error" id="username-alphanum">Username can only contain alphanumeric characters (a-z and 0-9).</span>
                        </div>
                        <div class="form-group">
                            <label for="email">Email</label>
                            <input type="email" class="form-control" id="email" placeholder="Valid email address" required="">
                            <p class="help-block">A valid email is required (you'll be sent a verification link).</p>
                            <span class="register-error" id="email-unique">That email is already associated with a different account.</span>
                            <span class="register-error" id="email-required">A valid email is required, please fill out this field.</span>
                        </div>
                        <div class="form-group">
                            <label for="password">Password</label>
                            <input type="password" class="form-control" id="password" placeholder="Password" required="">
                            <span class="register-error" id="password-required">Password is required, please fill out this field.</span>
                            <span class="register-error" id="password-gte">Password must be at least 8 characters long.</span>
                        </div>
                        <div class="form-group">
                            <label for="password_conf">Password Confirmation</label>
                            <input type="password" class="form-control" id="password_conf" placeholder="Password (again)" required="">
                            <span class="register-error" id="password-mismatch">The passwords you entered don't match.</span>
                        </div>

                        <button type="submit" class="btn btn-default" id="register-btn">Create Account</button>
                    </form>
                </div>
            </div>
        </div>
    </div>
    <div class="modal fade" tabindex="-1" role="dialog" id="forgot-modal">
        <div class="modal-dialog" role="document">
            <div class="modal-content">
                <div class="modal-header">
                    <button type="button" class="close" data-dismiss="modal" aria-label="Close"><span aria-hidden="true">×</span></button>
                    <h4 class="modal-title">Account recovery</h4>
                </div>
                <div class="modal-body">
                    <p class="info">
                        If you have a MangaStream account but you've forgotten your password, please enter your email below
                        and we'll send you some instructions to recover it.
                    </p>

                    <form class="forgot-form" novalidate="novalidate">
                        <div class="form-group">
                            <label for="email">Email</label>
                            <input type="email" class="form-control" id="forgot-email" placeholder="Your registered email address" required="">
                            <span class="forgot-error" id="forgot-email-required">Your email is required, please fill out this field.</span>
                        </div>

                        <button type="submit" class="btn btn-default" id="forgot-btn">Begin recovery</button>
                    </form>
                </div>
            </div>
        </div>
    </div>
    <div class="modal fade" tabindex="-1" role="dialog" id="forgot-success-modal">
        <div class="modal-dialog" role="document">
            <div class="modal-content">
                <div class="modal-header">
                    <button type="button" class="close" data-dismiss="modal" aria-label="Close"><span aria-hidden="true">×</span></button>
                    <h4 class="modal-title">Account recovery</h4>
                </div>
                <div class="modal-body">
                    <p class="info">
                        Great! If that email matches an account on MangaStream, expect to receive a message from us in the
                        next few minutes with further instructions.
                    </p>
                </div>
            </div>
        </div>
    </div>

</div>"""},

    {'tag': 'ul', 'attr': {'class': 'chapter_list'}, 'index':
     """<div class="chapter_content">
<h2 class="two_title">Tate no Yuusha no Nariagari Chapters</h2>
<ul class="chapter_list"> <li>
<a href="//www.mangatown.com/manga/tate_no_yuusha_no_nariagari/c040/">
Tate no Yuusha no Nariagari 40 </a>
<span class="time">Jan 31, 2018</span>
</li>
<li>
<a href="//www.mangatown.com/manga/tate_no_yuusha_no_nariagari/c039/">
Tate no Yuusha no Nariagari 39 </a>
<span class="time">Jan 1, 2018</span>
</li>
<li>
<a href="//www.mangatown.com/manga/tate_no_yuusha_no_nariagari/c038/">
Tate no Yuusha no Nariagari 38 </a>
<span class="time">Dec 5, 2017</span>
</li>
<li>
<a href="//www.mangatown.com/manga/tate_no_yuusha_no_nariagari/c037/">
Tate no Yuusha no Nariagari 37 </a>
<span>Carmira Isle</span> <span class="time">Nov 19, 2017</span>
</li>
<li>
<a href="//www.mangatown.com/manga/tate_no_yuusha_no_nariagari/c036/">
Tate no Yuusha no Nariagari 36 </a>
<span>Midnight Showdown</span> <span class="time">Sep 10, 2017</span>
</li>
<li>
<a href="//www.mangatown.com/manga/tate_no_yuusha_no_nariagari/c035/">
Tate no Yuusha no Nariagari 35 </a>
<span class="time">Aug 1, 2017</span>
</li>
<li>
 <a href="//www.mangatown.com/manga/tate_no_yuusha_no_nariagari/c034/">
Tate no Yuusha no Nariagari 34 </a>
<span>Visiting a Grave</span> <span class="time">Jul 2, 2017</span>
</li>
<li>
<a href="//www.mangatown.com/manga/tate_no_yuusha_no_nariagari/c033/">
Tate no Yuusha no Nariagari 33 </a>
<span class="time">May 23, 2017</span>
</li>
<li>
<a href="//www.mangatown.com/manga/tate_no_yuusha_no_nariagari/c032/">
Tate no Yuusha no Nariagari 32 </a>
<span>Sow the Wind, Reap the Tempest</span> <span class="time">Mar 22, 2017</span>
</li>
<li>
<a href="//www.mangatown.com/manga/tate_no_yuusha_no_nariagari/c031.5/">
Tate no Yuusha no Nariagari 31.5 </a>
<span>Accessories</span> <span class="time">Mar 6, 2017</span>
</li>
</ul> </div>"""},

    {'tag': 'table', 'attr': {'id': 'listing'}, 'index':
     """<div id="chapterlist">
<table id="listing">
<tbody><tr class="table_head">
<th class="leftgap">Chapter Name</th>
<th>Date Added</th>
</tr>
<tr>
<td>
<div class="chico_manga"></div>
<a href="/amatsuki/1">Amatsuki 1</a> : Rainy Night Moon</td>
<td>08/17/2009</td>
</tr>
<tr>
<td>
<div class="chico_manga"></div>
<a href="/amatsuki/2">Amatsuki 2</a> : The Distant Capital</td>
<td>08/17/2009</td>
</tr>
<tr>
<td>
<div class="chico_manga"></div>
<a href="/amatsuki/3">Amatsuki 3</a> : The Voice that Speaks to Dogs</td>
<td>08/17/2009</td>
</tr>
<tr>
<td>
<div class="chico_manga"></div>
<a href="/amatsuki/4">Amatsuki 4</a> : Not Quite a YaKou</td>
<td>08/17/2009</td>
</tr>
<tr>
<td>
<div class="chico_manga"></div>
<a href="/amatsuki/5">Amatsuki 5</a> : The Miko's Song</td>
<td>08/17/2009</td>
</tr>
<tr>
<td>
<div class="chico_manga"></div>
<a href="/amatsuki/6">Amatsuki 6</a> : A Ghostly Journey</td>
<td>08/17/2009</td>
</tr>
<tr>
<td>
<div class="chico_manga"></div>
<a href="/amatsuki/7">Amatsuki 7</a> : Turn Back or Keep Going</td>
<td>08/17/2009</td>
</tr>
<tr>
<td>
<div class="chico_manga"></div>
<a href="/amatsuki/8">Amatsuki 8</a> : The Dog God and the Holy Princess</td>
<td>08/17/2009</td>
</tr>
<tr>
<td>
<div class="chico_manga"></div>
<a href="/amatsuki/9">Amatsuki 9</a> : Coming into Bloom</td>
<td>08/17/2009</td>
</tr>
<tr>
<td>
<div class="chico_manga"></div>
<a href="/amatsuki/10">Amatsuki 10</a> : Faded Flowers</td>
<td>08/17/2009</td>
</tr>
</tbody></table>
</div>"""},

    {'tag': 'div', 'attr': {'class': 'main'}, 'index':
     """<div class="main">
    <div class="p-2 d-flex flex-column flex-md-row item">
        <a href="/chapter/1207786" class="chapt"><b>Ch.359</b> - Read Online</a>
        <div class="extra"><i class="pl-3">7 days ago</i></div>
    </div>

    <div class="p-2 d-flex flex-column flex-md-row item">
        <a href="/chapter/1206449" class="chapt"><b>Ch.358</b> - Read Online</a>
        <div class="extra"><i class="pl-3">13 days ago</i></div>
    </div>

    <div class="p-2 d-flex flex-column flex-md-row item">
        <a href="/chapter/1204823" class="chapt"><b>Ch.357</b> - Read Online</a>
        <div class="extra"><i class="pl-3">19 days ago</i></div>
    </div>

    <div class="p-2 d-flex flex-column flex-md-row item">
        <a href="/chapter/1202983" class="chapt"><b>Ch.356</b> - Read Online</a>
        <div class="extra"><i class="pl-3">a month ago</i></div>
    </div>

    <div class="p-2 d-flex flex-column flex-md-row item">
        <a href="/chapter/1200995" class="chapt"><b>Ch.355</b> - Read Online</a>
        <div class="extra"><i class="pl-3">a month ago</i></div>
    </div>

    <div class="p-2 d-flex flex-column flex-md-row item">
        <a href="/chapter/1199909" class="chapt"><b>Ch.354</b> - Read Online</a>
        <div class="extra"><i class="pl-3">a month ago</i></div>
    </div>

    <div class="p-2 d-flex flex-column flex-md-row item">
        <a href="/chapter/1195192" class="chapt"><b>Ch.353</b> - Read Online</a>
        <div class="extra"><i class="pl-3">2 months ago</i></div>
    </div>

    <div class="p-2 d-flex flex-column flex-md-row item">
        <a href="/chapter/1193933" class="chapt"><b>Ch.352</b> - Read Online</a>
        <div class="extra"><i class="pl-3">2 months ago</i></div>
    </div>

    <div class="p-2 d-flex flex-column flex-md-row item">
        <a href="/chapter/1190854" class="chapt"><b>Ch.350</b> - Read Online</a>
        <div class="extra"><i class="pl-3">3 months ago</i></div>
    </div>

    <div class="p-2 d-flex flex-column flex-md-row item">
        <a href="/chapter/1189860" class="chapt"><b>Ch.349</b> - Read Online</a>
        <div class="extra"><i class="pl-3">3 months ago</i></div>
    </div>

</div>"""}
])
def various_indexes(request):
    """Parametrized cached index of various types with source."""
    source = mangasource.MangaSource(
        'test source', 'http://www.source.com/', '_',
        index_tag=request.param['tag'], index_attrs=request.param['attr']
        )

    now = datetime.utcnow().timestamp()
    cache = seriescache.SeriesCache('test series')
    cache._index_pages = {repr(source): request.param['index']}
    cache._last_updated = {repr(source): now}

    return cache, source
