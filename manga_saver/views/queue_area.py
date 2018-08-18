"""Widget for the queue of items to download or convert."""
from PyQt5.QtWidgets import (QScrollArea, QVBoxLayout, QFrame, QLabel,
                             QWidget, QProgressBar, QStyleFactory, QHBoxLayout)
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt

from manga_saver.views import ICONS


class QueueArea(QScrollArea):
    """Scrollable area for items in the queue."""

    def __init__(self):
        """Display the current items in the queue."""
        super(QueueArea, self).__init__()

        self.init_ui()

    def init_ui(self):
        """Build an empty queue."""
        self.setFrameStyle(QFrame.NoFrame)

        self.setWidget(QWidget())
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setWidgetResizable(True)

        self.layout = QVBoxLayout(self.widget())
        self.layout.setAlignment(Qt.AlignTop)

    def add_queue_item(self, series_title, chapter):
        """Add a queue item to the queue area."""
        item = QueueAreaItem(series_title, chapter)
        self.layout.addWidget(item)
        return item


class QueueAreaItem(QFrame):
    """Item to display in the queue."""

    def __init__(self, series_title, chapter):
        """Create an item for the queue."""
        super(QueueAreaItem, self).__init__()

        self.series_title = series_title
        self.chapter = chapter

        self.download_icon = QPixmap(ICONS['DARK_DOWNLOAD'])
        self.pdf_icon = QPixmap(ICONS['DARK_PDF'])

        self.init_ui()

    def init_ui(self):
        """Build an inactive item for the queue."""
        self.setFrameStyle(QFrame.StyledPanel)

        self.layout = QVBoxLayout(self)
        hbox = QHBoxLayout()
        hbox.addWidget(QLabel(f'{self.series_title} - {self.chapter}'))
        hbox.addStretch(1)

        icon = QLabel()
        icon.setPixmap(self.download_icon)
        hbox.addWidget(icon)
        icon = QLabel()
        icon.setPixmap(self.pdf_icon)
        hbox.addWidget(icon)
        self.layout.addLayout(hbox)

        self.status_label = QLabel()
        self.layout.addWidget(self.status_label)

        progress_bar = QProgressBar()
        progress_bar.setStyle(QStyleFactory.create('Fusion'))
        progress_bar.setFormat('%v / %m')
        progress_bar.setTextVisible(True)
        progress_bar.setMinimum(0)
        progress_bar.setMaximum(1)
        # use .setValue() to update the current page number
        self.layout.addWidget(progress_bar)
        self.progress_bar = progress_bar

    def start_download(self):
        """Display start of download status."""
        self.status_label.setText('Downloading...')
        self.progress_bar.setMaximum(0)

    def start_conversion(self):
        """Display start of conversion status."""
        self.status_label.setText('Converting...')
        self.progress_bar.setMaximum(0)
