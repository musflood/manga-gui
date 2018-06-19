"""Widget for the list of chapters for a series."""
import os

from PyQt5.QtWidgets import (QFrame, QVBoxLayout, QLabel,
                             QScrollArea, QCheckBox, QHBoxLayout,
                             QWidget, QPushButton, QMenu)
from PyQt5.QtGui import QFont, QPixmap, QPainter
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

        for n in range(30):
            vbox.addLayout(ChapterListEntryLayout(f'things {n}'))
            vbox.addWidget(HorizontalLine())

        self.box_layout.addWidget(scroll_area, stretch=4)

        return scroll_area


class ChapterListEntryLayout(QHBoxLayout):
    """Details about a specific chapter for the manga chapter list."""

    def __init__(self, chapter):
        """Create an entry for the chapter list."""
        super(ChapterListEntryLayout, self).__init__()

        self.LIGHT_DOWNLOAD_ICON = os.path.join(ICON_DIR, 'download_light.png')
        self.LIGHT_PDF_ICON = os.path.join(ICON_DIR, 'book_light.png')

        self.DARK_DOWNLOAD_ICON = os.path.join(ICON_DIR, 'download_dark.png')
        self.DARK_PDF_ICON = os.path.join(ICON_DIR, 'book_dark.png')

        self.CHECK_ICON = QPixmap(os.path.join(ICON_DIR, 'check_solid.png'))

        self.chapter = chapter
        self.init_ui()

    def init_ui(self):
        """Build a chapter list entry with icons."""
        self.addWidget(QLabel(self.chapter))
        self.addStretch(1)

        self.addWidget(self.make_download_icon())
        self.addWidget(self.make_pdf_icon())

    def make_download_icon(self):
        """Make a download icon to add to the chapter list entry."""
        download_label = QLabel()
        download_label.setCursor(Qt.PointingHandCursor)
        download_label.setToolTip('Download')

        download_menu = QMenu()
        download_menu.addAction('Download and convert to PDF')
        download_menu.addSeparator()
        download_menu.addAction('Download all above')
        download_menu.addAction('Download all above and convert to PDF')

        download_label.setContextMenuPolicy(Qt.CustomContextMenu)
        download_label.customContextMenuRequested.connect(
            lambda p: download_menu.exec_(download_label.mapToGlobal(p))
        )
        # download_label.mousePressEvent = lambda event: print(self.chapter)

        download_img = QPixmap(self.LIGHT_DOWNLOAD_ICON)
        download_label.setPixmap(download_img)

        return download_label

    def make_pdf_icon(self):
        """Make a pdf convert icon to add to the chapter list entry."""
        pdf_label = QLabel()
        pdf_label.setCursor(Qt.PointingHandCursor)
        pdf_label.setToolTip('Convert to PDF')

        pdf_menu = QMenu()
        pdf_menu.addAction('Convert all above to PDF')

        pdf_label.setContextMenuPolicy(Qt.CustomContextMenu)
        pdf_label.customContextMenuRequested.connect(
            lambda p: pdf_menu.exec_(pdf_label.mapToGlobal(p))
        )

        pdf_img = QPixmap(self.LIGHT_PDF_ICON)
        pdf_label.setPixmap(pdf_img)

        return pdf_label

    def paint_checkmark(self, pixmap):
        """Paint a checkmark on the given pixmap."""
        painter = QPainter()
        painter.begin(pixmap)
        painter.drawPixmap(5, 5, 10, 10, self.CHECK_ICON)
        painter.end()
        return pixmap


class HorizontalLine(QFrame):
    """Horizontal bar that extends across the parent area."""

    def __init__(self):
        """Create a horizontal line."""
        super(HorizontalLine, self).__init__()
        self.setFrameShape(QFrame.HLine)
        self.setFrameShadow(QFrame.Sunken)
