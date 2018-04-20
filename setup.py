from setuptools import setup

setup(
    name='manga_gui',
    version="0.0.0",
    author='Megan Flood',
    author_email='mak.flood@comcast.net',
    description='Scrape the pages of a manga and save the files using a GUI.',
    package_dir={'': 'src'},
    py_modules=['scraper'],
    install_requires=['requests', 'beautifulsoup4', 'Pillow', 'PyPDF2']
)
