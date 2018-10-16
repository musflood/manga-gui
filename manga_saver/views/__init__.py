"""Constants for the views."""
import os

from PyQt5.QtWidgets import QFrame

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
APPLICATION_DIR = os.path.dirname(BASE_DIR)
RESOURCE_DIR = os.path.join(BASE_DIR, 'resources')
ICON_DIR = os.path.join(RESOURCE_DIR, 'icons')
LOGO_DIR = os.path.join(RESOURCE_DIR, 'logos')

# Icon file
ICONS = {
    'DOWN_ARROW': os.path.join(ICON_DIR, 'down_arrow.png'),
    'PLUS': os.path.join(ICON_DIR, 'plus.png'),
    'MINUS': os.path.join(ICON_DIR, 'minus.png'),

    'SEARCH': os.path.join(ICON_DIR, 'search.png'),

    'YELLOW_STATUS': os.path.join(ICON_DIR, 'yellowdot.png'),
    'RED_STATUS': os.path.join(ICON_DIR, 'reddot.png'),
    'GREEN_STATUS': os.path.join(ICON_DIR, 'greendot.png'),

    'LIGHT_DOWNLOAD': os.path.join(ICON_DIR, 'download_light.png'),
    'DARK_DOWNLOAD': os.path.join(ICON_DIR, 'download_dark.png'),

    'LIGHT_PDF': os.path.join(ICON_DIR, 'book_light.png'),
    'DARK_PDF': os.path.join(ICON_DIR, 'book_dark.png'),

    'SOLID_CHECK': os.path.join(ICON_DIR, 'check_solid.png'),
    'OUTLINE_CHECK': os.path.join(ICON_DIR, 'check_outline.png'),
    'OUTLINE_CHECK_WHITE': os.path.join(ICON_DIR, 'check_outline_white.png'),

    'SOLID_STAR': os.path.join(ICON_DIR, 'star_filled.png'),
    'OUTLINE_STAR': os.path.join(ICON_DIR, 'star_outline.png'),

    'SETTINGS_GENERAL': os.path.join(ICON_DIR, 'settings.png'),
    'SETTINGS_SOURCE': os.path.join(ICON_DIR, 'network.png'),
    'SETTINGS_SERIES': os.path.join(ICON_DIR, 'books.png'),
}

LOGOS = {
    '100x100': os.path.join(LOGO_DIR, 'saber_small.png')
}


class HorizontalLine(QFrame):
    """Horizontal bar that extends across the parent area."""

    def __init__(self):
        """Create a horizontal line."""
        super(HorizontalLine, self).__init__()
        self.setFrameShape(QFrame.HLine)
        self.setFrameShadow(QFrame.Sunken)
