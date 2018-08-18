"""Widget for the list of chapters for a series."""
from PyQt5.QtWidgets import (QFrame, QVBoxLayout, QLabel,
                             QScrollArea, QCheckBox, QHBoxLayout,
                             QWidget, QPushButton, QMenu)
from PyQt5.QtGui import QFont, QPixmap, QPainter
from PyQt5.QtCore import Qt

from manga_saver.views import ICONS, HorizontalLine


class ChapterListWidget(QFrame):
    """List of chapters for a series."""

    TITLE_FONT = QFont()
    TITLE_FONT.setPointSize(25)

    def __init__(self, series_title):  # , series, source):
        """List the chapters for a series."""
        super(ChapterListWidget, self).__init__()

        self.series_title = series_title
        self.init_ui()

        self.add_no_chapters_label()

    def init_ui(self):
        """Build the chapter list framework."""
        self.layout = QVBoxLayout(self)

        self.add_top_frame()
        self.chapter_area_layout = self.add_bottom_frame()

    def add_top_frame(self):
        """Add top frame with series details."""
        vbox = QVBoxLayout()

        hbox = QHBoxLayout()
        title_label = QLabel(self.series_title)
        title_label.setFont(self.TITLE_FONT)
        hbox.addWidget(title_label)
        hbox.addStretch(1)
        hbox.addWidget(self.make_favorite_checkbox())
        vbox.addLayout(hbox)

        hbox = QHBoxLayout()
        hbox.addWidget(QLabel('Last Updated:'))
        date_label = QLabel('minutes ago')
        hbox.addWidget(date_label)
        hbox.addStretch(1)
        hbox.addWidget(self.make_download_button())
        vbox.addLayout(hbox)

        vbox.setAlignment(Qt.AlignBottom)

        self.layout.addLayout(vbox)

        return vbox

    def make_favorite_checkbox(self):
        """Create a custom checkbox for marking favorites."""
        checkbox = QCheckBox()
        checkbox.setToolTip('Favorite')
        checkbox.setCursor(Qt.PointingHandCursor)
        checkbox.setStyleSheet(f'''
            QCheckBox::indicator:unchecked {{
                image: url({ICONS["OUTLINE_STAR"]});
            }}
            QCheckBox::indicator:checked {{
                image: url({ICONS["SOLID_STAR"]});
            }}
            QCheckBox {{
                margin-right: 5px;
            }}
        ''')
        return checkbox

    def make_download_button(self):
        """Create a menu button for downloading multiple chapters."""
        button = QPushButton('Download all')
        menu = QMenu()
        menu.addAction('Download all available chapters')
        menu.addAction(
            'Download all available chapters and convert to PDF')
        menu.addSeparator()
        menu.addAction('Download all undownloaded chapters')
        menu.addAction(
            'Download all undownloaded chapters and convert to PDF')
        button.setMenu(menu)
        return button

    def add_bottom_frame(self):
        """Add bottom frame with chapter list."""
        scroll_area = QScrollArea()
        scroll_area.setWidget(QWidget())
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        scroll_area.setWidgetResizable(True)

        vbox = QVBoxLayout(scroll_area.widget())
        vbox.setAlignment(Qt.AlignTop)

        self.layout.addWidget(scroll_area)

        return vbox

    def add_no_chapters_label(self):
        """Create a label for when no chapters are available."""
        hbox = QHBoxLayout()
        hbox.addWidget(QLabel('No chapters yet.'))
        hbox.setAlignment(Qt.AlignHCenter)
        self.chapter_area_layout.addLayout(hbox)

    def add_chapter_entry(self, chapter):
        """Create an entry for the chapter list."""
        if self.chapter_area_layout.children():
            self.chapter_area_layout.addWidget(HorizontalLine())
        self.chapter_area_layout.addLayout(ChapterListEntryLayout(chapter))


class ChapterListEntryLayout(QHBoxLayout):
    """Details about a specific chapter for the manga chapter list."""

    def __init__(self, chapter):
        """Create an entry for the chapter list."""
        super(ChapterListEntryLayout, self).__init__()

        self.light_download_icon = QPixmap(ICONS['LIGHT_DOWNLOAD'])
        self.light_pdf_icon = QPixmap(ICONS['LIGHT_PDF'])

        self.dark_download_icon = QPixmap(ICONS['DARK_DOWNLOAD'])
        self.dark_pdf_icon = QPixmap(ICONS['DARK_PDF'])

        self.check_icon = QPixmap(ICONS['SOLID_CHECK'])

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

        download_label.setPixmap(self.light_download_icon)

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

        pdf_label.setPixmap(self.light_pdf_icon)

        return pdf_label

    def paint_checkmark(self, pixmap):
        """Paint a checkmark on the given pixmap."""
        painter = QPainter()
        painter.begin(pixmap)
        painter.drawPixmap(5, 5, 10, 10, self.check_icon)
        painter.end()
        return pixmap
