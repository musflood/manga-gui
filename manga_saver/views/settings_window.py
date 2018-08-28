"""Settings window for the application."""
from PyQt5.QtWidgets import (QTabWidget, QTabBar, QFrame, QLabel,
                             QVBoxLayout, QHBoxLayout)
from PyQt5.QtGui import QIcon

from manga_saver.views import ICONS


class SettingsWindow(QTabWidget):
    """Window to control the application settings."""

    def __init__(self):
        """Create the settings window."""
        super(SettingsWindow, self).__init__()
        self.init_ui()

    def init_ui(self):
        """Build the settings window."""
        self.setWindowTitle('Preferences')
        self.setObjectName('settings-window')
        self.tabBar().setObjectName('settings-tabs')

        self.setStyleSheet('''
            #settings-window {
                background: #DDD;
            }

            #settings-window::pane {
                border-top: 1px solid #BBB;
                background: #ECECEC;
            }

            #settings-window::tab-bar {
                left: 10px;
            }

            #settings-tabs::tab {
                border: none;
                margin-top: 10px;
            }

            #settings-tabs::tab:last {
                margin-right: 15px;
            }

            #settings-tabs::tab::selected {
                background: #BBB;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
            }
        ''')

        general = QFrame()

        sources = QFrame()

        series = QFrame()

        self.addTab(general, QIcon(ICONS['SETTINGS_GENERAL']), 'General')
        self.addTab(sources, QIcon(ICONS['SETTINGS_SOURCE']), 'Sources')
        self.addTab(series, QIcon(ICONS['SETTINGS_SERIES']), 'Series')

    def addTab(self, widget, icon, text):
        """Add a tab with the icon above the text."""
        index = super(SettingsWindow, self).addTab(widget, None)
        frame = QFrame()

        vbox = QVBoxLayout(frame)
        vbox.setSpacing(2)
        vbox.setContentsMargins(7, 12, 10, 0)

        hbox = QHBoxLayout()
        hbox.addStretch(1)
        icon_label = QLabel(frame)
        icon_label.setPixmap(icon.pixmap(30, 30))
        hbox.addWidget(icon_label)
        hbox.addStretch(1)
        vbox.addLayout(hbox)

        hbox = QHBoxLayout()
        hbox.addStretch(1)
        text_label = QLabel(text, frame)
        hbox.addWidget(text_label)
        hbox.addStretch(1)
        vbox.addLayout(hbox)

        self.tabBar().setTabButton(index, QTabBar.LeftSide, frame)
        return index
