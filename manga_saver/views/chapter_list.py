"""Widgets for the list of chapters for a series."""
from PyQt5.QtWidgets import (QFrame, QVBoxLayout, QLabel,
                             QScrollArea, QCheckBox, QHBoxLayout,
                             QWidget, QPushButton, QMenu, QToolButton)
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

    def init_ui(self):
        """Build the chapter list framework."""
        self.layout = QVBoxLayout(self)

        self._add_top_frame()
        self.chapter_area_layout = self._add_bottom_frame()

    def _add_top_frame(self):
        """Add top frame with series details."""
        vbox = QVBoxLayout()

        hbox = QHBoxLayout()
        title_label = QLabel(self.series_title)
        title_label.setFont(self.TITLE_FONT)
        hbox.addWidget(title_label)
        hbox.addStretch(1)
        hbox.addWidget(self._make_favorite_checkbox())
        vbox.addLayout(hbox)

        hbox = QHBoxLayout()
        hbox.addWidget(QLabel('Last Updated:'))
        date_label = QLabel('minutes ago')
        hbox.addWidget(date_label)
        hbox.addStretch(1)
        hbox.addLayout(self._make_download_button())
        vbox.addLayout(hbox)

        vbox.setAlignment(Qt.AlignBottom)

        self.layout.addLayout(vbox)

        return vbox

    def _make_favorite_checkbox(self):
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

    def _make_download_button(self):
        """Create a menu button for downloading multiple chapters."""
        hbox = QHBoxLayout()
        hbox.setSpacing(0)
        hbox.setContentsMargins(0, 0, 0, 0)

        button = QPushButton('Download all')
        hbox.addWidget(button)

        button = QToolButton()
        button.setArrowType(Qt.DownArrow)
        button.setPopupMode(QToolButton.InstantPopup)
        button.setStyleSheet(f'''
            QToolButton {{
                background: #4594EE;
                border: 0;
                border-radius: 2px;
                margin-top: 2px;
                width: 5px;
                padding-left: 3px;
                padding-right: 3px;
            }}

            QToolButton::down-arrow {{
                image: url({ICONS["DOWN_ARROW"]})
            }}

            QToolButton::menu-indicator {{
                width: 0;
                height: 0;
            }}
        ''')
        hbox.addWidget(button)
        menu = QMenu()
        menu.addAction('Download all available chapters')
        menu.addAction(
            'Download all available chapters and convert to PDF')
        menu.addSeparator()
        menu.addAction('Download all undownloaded chapters')
        menu.addAction(
            'Download all undownloaded chapters and convert to PDF')
        button.setMenu(menu)
        return hbox

    def _add_bottom_frame(self):
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
        return hbox

    def add_chapter_entry(self, chapter):
        """Create an entry for the chapter list."""
        if self.chapter_area_layout.children():
            self.chapter_area_layout.addWidget(HorizontalLine())
        entry = ChapterListEntryLayout(chapter)
        self.chapter_area_layout.addLayout(entry)
        return entry

    def clear_chapters(self):
        """Remove all the chapter entries from the chapter list."""
        while self.chapter_area_layout.count():
            item = self.chapter_area_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
            elif hasattr(item, 'deleteLater'):
                item.deleteLater()


class ChapterListEntryLayout(QHBoxLayout):
    """Details about a specific chapter for the manga chapter list."""

    def __init__(self, chapter):
        """Create an entry for the chapter list."""
        super(ChapterListEntryLayout, self).__init__()

        self._download_available = False
        self._has_downloaded = False
        self._convert_available = False
        self._has_converted = False

        self.light_download_icon = QPixmap(ICONS['LIGHT_DOWNLOAD'])
        self.light_pdf_icon = QPixmap(ICONS['LIGHT_PDF'])

        self.dark_download_icon = QPixmap(ICONS['DARK_DOWNLOAD'])
        self.dark_pdf_icon = QPixmap(ICONS['DARK_PDF'])

        self.check_icon = QPixmap(ICONS['SOLID_CHECK'])
        self.pending_icon = QPixmap(ICONS['YELLOW_STATUS'])

        self.chapter = chapter
        self.init_ui()

    @property
    def download_icon(self):
        """Get the current download icon."""
        if self._download_available:
            return self.dark_download_icon
        return self.light_download_icon

    @property
    def pdf_icon(self):
        """Get the current pdf icon."""
        if self._convert_available:
            return self.dark_pdf_icon
        return self.light_pdf_icon

    def init_ui(self):
        """Build a chapter list entry with icons."""
        self.addWidget(QLabel(self.chapter))
        self.addStretch(1)

        self.download_button = self._make_download_icon()
        self.addWidget(self.download_button)
        self.convert_button = self._make_pdf_icon()
        self.addWidget(self.convert_button)

    def _make_download_icon(self):
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
        download_label.setEnabled(False)

        return download_label

    def _make_pdf_icon(self):
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
        pdf_label.setEnabled(False)

        return pdf_label

    def mark_as_complete(self, button_type):
        """Mark the given button type as complete.

        Note that button_type must be either 'download' or 'convert'.
        """
        if button_type == 'download':
            button = self.download_button
            self._has_downloaded = True
        elif button_type == 'convert':
            button = self.convert_button
            self._has_converted = True
        else:
            raise ValueError('Button type must be "download" or "convert".')

        pixmap = button.pixmap()
        self._paint_checkmark(pixmap)
        button.setPixmap(pixmap)

    def _paint_checkmark(self, pixmap):
        """Paint a checkmark on the given pixmap."""
        painter = QPainter()
        painter.begin(pixmap)
        painter.drawPixmap(5, 5, 10, 10, self.check_icon)
        painter.end()
        return pixmap

    def mark_as_pending(self, button_type):
        """Mark the given button type as pending.

        Note that button_type must be either 'download' or 'convert'.
        """
        if button_type == 'download':
            button = self.download_button
        elif button_type == 'convert':
            button = self.convert_button
        else:
            raise ValueError('Button type must be "download" or "convert".')

        pixmap = button.pixmap()
        self._paint_pending(pixmap)
        button.setPixmap(pixmap)

    def _paint_pending(self, pixmap):
        """Paint a pending dot on the given pixmap."""
        painter = QPainter()
        painter.begin(pixmap)
        painter.drawPixmap(5, 5, 10, 10, self.pending_icon)
        painter.end()
        return pixmap

    def mark_as_available(self, button_type):
        """Mark the given button type as available.

        Note that button_type must be either 'download' or 'convert'.
        """
        if button_type == 'download':
            button = self.download_button
            self._download_available = True
            pixmap = self.download_icon
            complete = self._has_downloaded
        elif button_type == 'convert':
            button = self.convert_button
            self._convert_available = True
            pixmap = self.pdf_icon
            complete = self._has_converted
        else:
            raise ValueError('Button type must be "download" or "convert".')

        button.setPixmap(pixmap)
        button.setEnabled(True)
        if complete:
            self.mark_as_complete(button_type)

    def mark_as_unavailable(self, button_type):
        """Mark the given button type as unavailable.

        Note that button_type must be either 'download' or 'convert'.
        """
        if button_type == 'download':
            button = self.download_button
            self._download_available = False
            pixmap = self.download_icon
            complete = self._has_downloaded
        elif button_type == 'convert':
            button = self.convert_button
            self._convert_available = False
            pixmap = self.pdf_icon
            complete = self._has_converted
        else:
            raise ValueError('Button type must be "download" or "convert".')

        button.setPixmap(pixmap)
        button.setEnabled(False)
        if complete:
            self.mark_as_complete(button_type)

    def remove_marks(self, button_type):
        """Remove pending and complete marks from the given button type.

        Note that button_type must be either 'download' or 'convert'.
        """
        if button_type == 'download':
            button = self.download_button
            pixmap = self.download_icon
            self._has_downloaded = False
        elif button_type == 'convert':
            button = self.convert_button
            pixmap = self.pdf_icon
            self._has_converted = False
        else:
            raise ValueError('Button type must be "download" or "convert".')

        button.setPixmap(pixmap)

    def deleteLater(self):
        """Delete the entire list entry widget."""
        while self.count():
            item = self.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        super(ChapterListEntryLayout, self).deleteLater()
