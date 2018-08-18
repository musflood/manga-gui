"""Add the current file to the PATH and import packages to be tested."""
# -*- coding: utf-8 -*-

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from manga_saver.models import manga_source  # flake8: noqa
from manga_saver import scraper  # flake8: noqa
from manga_saver.models import series_cache  # flake8: noqa
