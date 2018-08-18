# Manga Saver
[![Build Status](https://travis-ci.org/musflood/manga-gui.svg?branch=master)](https://travis-ci.org/musflood/manga-gui)
[![Coverage Status](https://coveralls.io/repos/github/musflood/manga-gui/badge.svg?branch=master)](https://coveralls.io/github/musflood/manga-gui?branch=master)

**Author**: Megan Flood

**Version**: 0.3.0

## Overview
Download the chapters of your favorite manga from various sources online to your computer for offline reading.

## Getting Started
Clone this repository to your local machine.
```bash
$ git clone https://github.com/musflood/manga-gui.git
```

Once downloaded, change directory into the `manga-gui` directory.
```bash
$ cd manga-gui
```

Begin a new virtual environment with Python 3 and activate it.
```bash
manga-gui $ python3.6 -m venv ENV
manga-gui $ source ENV/bin/activate
```

Install the application with [`pip`](https://pip.pypa.io/en/stable/installing/).
```bash
(ENV) manga-gui $ pip install -e .
```

## Usage
In order to use the scraper directly, you must create a series and a source to pull from.
```python
>>> from manga_saver.models.manga_source import MangaSource
>>> from manga_saver.models.series_cache import SeriesCache

>>> series = SeriesCache('The Best Series Ever')
>>> source = MangaSource('Top Manga', 'http://www.manga.com', '-')
```

Then, you can get the chapters available on the source for the series.
```python
>>> from manga_saver.scraper import Scraper

>>> Scraper.chapter_list(series, source)

{
    '55': 'http://www.manga.com/best-series-ever/55',
    '54': 'http://www.manga.com/best-series-ever/54',
    '53': 'http://www.manga.com/best-series-ever/53',
    '52': 'http://www.manga.com/best-series-ever/52'
}
```

Or you can get a generator of the binary data of the page images for a chapter.
```python
>>> pages = Scraper.chapter_pages('55', series, source)
>>> next(pages)

(b'\x0b\xb1\x8eV\xf7b(\xe4\xee\x0e...', 'png')
```

## Testing
Make sure you have the `testing` set of dependancies installed.
```bash
(ENV) manga-gui $ pip install -e .[testing]
```

You can test this application by running `pytest` in the same directory as the `setup.py` file.
```bash
(ENV) manga-gui $ pytest
```

## Architecture
Written in [Python 3.6](https://www.python.org/), with [pytest](https://docs.pytest.org/en/latest/) for testing.

Uses [BeautifulSoup4](https://www.crummy.com/software/BeautifulSoup/) for parsing HTML and [Requests](http://docs.python-requests.org/en/master/) to retrieve HTML pages and images.

## Change Log
| Date | &emsp;
| :--- | ---
|**5-27-2018 7:03pm** | Added chapter list caching to SeriesCache and refactored public Scraper methods.
|**5-25-2018 12:26am** | Completed first iteration of Scraper class and SeriesCache model.
|**4-21-2018 11:17pm** | Completed first iteration of MangaSource model.
|**4-21-2018 7:30pm** | Setup testing and automated testing.
|**4-20-2018 10:31am** | Initial file setup.