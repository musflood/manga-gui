from setuptools import setup, find_packages

requires = [
    'beautifulsoup4',
    'Pillow == 9.0.1',
    'PyPDF2',
    'requests'
]

test_requires = [
    'pytest',
    'pytest-cov',
    'pytest-mock',
    'pytest-watch'
]

setup(
    name='manga_saver',
    version="0.0.0",
    author='Megan Flood',
    author_email='mak.flood@comcast.net',
    description='Save chapters of manga from the internet to your computer.',
    packages=find_packages(exclude=('tests')),
    install_requires=requires,
    extras_require={
        'testing': test_requires,
    },
)
