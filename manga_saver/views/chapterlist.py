"""Widget for the list of chapters for a series."""
import os

from PyQt5.QtWidgets import (QFrame, QVBoxLayout, QGridLayout, QLabel,
                             QScrollArea, QCheckBox, QHBoxLayout, QFormLayout,
                             QWidget, QPushButton)
from PyQt5.QtGui import QFont, QPixmap
from PyQt5.QtCore import Qt

from manga_saver.views import ICON_DIR


class ChapterListWidget(QFrame):
    """List of chapters for a series."""

    TITLE_FONT = QFont()
    TITLE_FONT.setPointSize(20)

    def __init__(self):  # , series, source):
        """List the chapters for a series."""
        super(ChapterListWidget, self).__init__()

        self.init_ui()

    def init_ui(self):
        """Build the chapter list framework."""
        self.box_layout = QVBoxLayout()
        self.setLayout(self.box_layout)

        self.add_top_frame()
        self.add_bottom_frame()

    def add_top_frame(self):
        """Add top frame with series details."""
        vbox = QVBoxLayout()
        title_label = QLabel('Series Title')
        title_label.setFont(self.TITLE_FONT)
        vbox.addWidget(title_label)

        hbox = QHBoxLayout()

        hbox.addWidget(QLabel('Last Updated:'))
        date_label = QLabel('minutes ago')
        hbox.addWidget(date_label)

        hbox.addStretch(1)
        fav_cb = QCheckBox()
        hbox.addWidget(fav_cb)
        hbox.addWidget(QLabel('Favorite'))

        vbox.addLayout(hbox)

        self.box_layout.addLayout(vbox, stretch=1)

        return vbox

    def add_bottom_frame(self):
        """Add bottom frame with chapter list."""
        scroll_area = QScrollArea()
        scroll_area.setWidget(QWidget())
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        scroll_area.setWidgetResizable(True)

        vbox = QVBoxLayout(scroll_area.widget())
        vbox.setAlignment(Qt.AlignTop)

        for _ in range(30):
            vbox.addLayout(ChapterListEntryLayout('things'))
            vbox.addWidget(HorizontalLine())

        self.box_layout.addWidget(scroll_area, stretch=4)

        return scroll_area


class ChapterListEntryLayout(QHBoxLayout):
    """Details about a specific chapter for the manga chapter list."""

    def __init__(self, chapter):
        """Create an entry for the chapter list."""
        super(ChapterListEntryLayout, self).__init__()

        self.LIGHT_DOWNLOAD_ICON = QPixmap(
            os.path.join(ICON_DIR, 'download_light.png'))
        self.LIGHT_PDF_ICON = QPixmap(os.path.join(ICON_DIR, 'book_light.png'))

        self.DARK_DOWNLOAD_ICON = QPixmap(
            os.path.join(ICON_DIR, 'download_dark.png'))
        self.DARK_PDF_ICON = QPixmap(os.path.join(ICON_DIR, 'book_dark.png'))

        self.chapter = chapter
        self.init_ui()

    def init_ui(self):
        """Build a chapter list entry with icons."""
        self.addWidget(QLabel(self.chapter))
        self.addStretch(1)

        download_label = QLabel()
        download_label.setPixmap(self.LIGHT_DOWNLOAD_ICON)
        self.addWidget(download_label)
        pdf_label = QLabel()
        pdf_label.setPixmap(self.LIGHT_PDF_ICON)
        self.addWidget(pdf_label)


class HorizontalLine(QFrame):
    """Horizontal bar that extends across the parent area."""

    def __init__(self):
        """Create a horizontal line."""
        super(HorizontalLine, self).__init__()
        self.setFrameShape(QFrame.HLine)
        self.setFrameShadow(QFrame.Sunken)
