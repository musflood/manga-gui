"""Widget for the list of chapters for a series."""
from PyQt5.QtWidgets import (QFrame, QVBoxLayout, QGridLayout, QLabel,
                             QScrollArea, QCheckBox, QHBoxLayout, QFormLayout,
                             QWidget)
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt


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
        frame = QFrame()

        vbox = QVBoxLayout(frame)
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

        self.box_layout.addWidget(frame, stretch=1)

        return frame

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
            vbox.addWidget(QLabel('things'))

        self.box_layout.addWidget(scroll_area, stretch=4)

        return scroll_area
