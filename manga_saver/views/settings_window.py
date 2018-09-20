"""Settings window for the application."""
from PyQt5.QtWidgets import (QTabWidget, QTabBar, QFrame, QLabel,
                             QVBoxLayout, QHBoxLayout, QGroupBox,
                             QFormLayout, QCheckBox, QComboBox,
                             QGridLayout, QLineEdit, QPushButton, QFileDialog)
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt

from manga_saver.views import ICONS, APPLICATION_DIR


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

        general = self._make_general_tab()
        self.set_general_settings()

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

    def get_general_settings(self):
        """Get the current settings in the general tab."""
        return {
            'chapter_download_directory': self.general_dir_le.text(),
            'auto_convert_downloads': self.general_auto_convert_cb.isChecked(),
            'download_new_chaps_only': self.general_download_new_cb.isChecked()
        }

    def set_general_settings(self, chapter_download_directory=APPLICATION_DIR,
                             auto_convert_downloads=False,
                             download_new_chaps_only=True):
        """Set the settings in the general tab."""
        self.general_dir_le.setText(chapter_download_directory)
        self.general_auto_convert_cb.setChecked(auto_convert_downloads)
        self.general_download_new_cb.setChecked(download_new_chaps_only)

    def _make_general_tab(self):
        """Create the general settings tab contents."""
        frame = QFrame()
        frame.setStyleSheet('''
            QCheckBox {
                margin-right: 5px;
            }
        ''')

        vbox = QVBoxLayout(frame)
        hbox = QHBoxLayout()
        vbox.addLayout(hbox)

        hbox.addStretch(1)
        group = QGroupBox()
        hbox.addWidget(group)
        hbox.addStretch(1)

        layout = QGridLayout()

        label = QLabel('Chapter directory:')
        line_edit = QLineEdit()
        line_edit.setReadOnly(True)
        button = QPushButton('Change...')
        button.clicked.connect(self._set_download_folder)
        layout.addWidget(label, 1, 0, alignment=Qt.AlignRight)
        layout.addWidget(line_edit, 1, 1)
        layout.addWidget(button, 1, 2)
        self.general_dir_le = line_edit

        label = QLabel('Automatically convert downloaded chapters to PDF')
        check = QCheckBox()
        layout.addWidget(check, 2, 0, alignment=Qt.AlignRight)
        layout.addWidget(label, 2, 1, 1, 2)
        self.general_auto_convert_cb = check

        label = QLabel('"Download all" only downloads un-downloaded chapters')
        check = QCheckBox()
        layout.addWidget(check, 3, 0, alignment=Qt.AlignRight)
        layout.addWidget(label, 3, 1, 1, 2)
        self.general_download_new_cb = check

        group.setLayout(layout)
        group.setMinimumSize(group.sizeHint())
        group.setMaximumSize(group.sizeHint())

        hbox = QHBoxLayout()
        vbox.addLayout(hbox)
        hbox.addStretch(1)
        save_button = QPushButton('Apply')
        save_button.clicked.connect(lambda: print(self.get_general_settings()))
        hbox.addWidget(save_button)

        return frame

    def _set_download_folder(self):
        """Show a file dialogue to set the chapter download destination."""
        dest_dir = QFileDialog.getExistingDirectory(self, 'Choose destination')
        if dest_dir:
            self.general_dir_le.setText(dest_dir)
