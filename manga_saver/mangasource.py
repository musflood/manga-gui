"""A source website from which to pull manga."""
# from bs4 import BeautifulSoup
# from PIL import Image
# from PyPDF2 import PdfFileWriter, PdfFileReader
# import requests

# import os
# import re
# import shutil

# SEED = Image.open('seed.jpg')


class MangaSource(object):
    """Details for a source website."""

    def __init__(self, name, root_url, slug_filler):
        """Set up details for a new source."""
        self.name = name
        self.root_url = root_url
        self.slug_filler = slug_filler

    def __repr__(self):
        """Display the name and url for the source."""
        return f'<MangaSource: {self.name} @ {self.root_url}>'

    def __str__(self):
        """Display the name of the source."""
        return self.name
