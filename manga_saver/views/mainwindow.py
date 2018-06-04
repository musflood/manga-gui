"""Main window frame for the GUI."""
import os

from PyQt5.QtWidgets import (QMainWindow, QHBoxLayout, QFrame, QScrollArea,
                             QAction, QDockWidget, QListWidget, QSplitter,
                             QComboBox, QWidget, QSizePolicy, QLineEdit)
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt, QSize

from manga_saver.views import ICON_DIR


class MainWindow(QMainWindow):
    """Main window frame.

    Has top source bar with search bar, series side bar, queue side bar,
    main series chapter list, status bar.
    """

    def __init__(self):
        """Display the main window."""
        super(MainWindow, self).__init__()

        self.init_ui()
        self.show()

    def init_ui(self):
        """Create a main window skeleton."""
        self.source_input, self.refresh_act = self.add_top_bar()

        self.statusBar().showMessage('Choose a source')

        self.fav_series_area, self.chapter_area = self.add_main_area()

        self.queue_dock, self.queue_area = self.add_queue_area()

        self.add_menubar()

        self.setMinimumSize(700, 500)

    def add_top_bar(self):
        """Add the top bar with source dropdown and search bar."""
        self.toolbar = self.addToolBar('')
        self.toolbar.setMovable(False)

        self.toolbar.addWidget(QWidget())

        source_input = QComboBox()
        source_input.setMinimumWidth(150)
        source_input.setToolTip('Manga Source')
        self.toolbar.addWidget(source_input)

        red_icon = QIcon(os.path.join(ICON_DIR, 'reddot.png'))
        # green_icon = QIcon(os.path.join(ICON_DIR, 'greendot.png'))

        refresh_act = QAction(red_icon, 'Refresh Source', self)
        # refresh_act.triggered.connect(self.refresh_source)
        self.toolbar.addAction(refresh_act)

        spacer = QWidget()
        spacer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.toolbar.addWidget(spacer)

        search_bar = QLineEdit()
        search_bar.setMaximumWidth(150)
        search_bar.setPlaceholderText('Search Series...')
        self.toolbar.addWidget(search_bar)

        search_icon = QIcon(os.path.join(ICON_DIR, 'search.png'))
        search_act = QAction(search_icon, 'Search by Title', self)

        # search_act.triggered.connect(self.refresh_source)
        self.toolbar.addAction(search_act)

        self.toolbar.addWidget(QWidget())

        self.toolbar.setIconSize(QSize(20, 20))

        return source_input, refresh_act

    def add_main_area(self):
        """Add the main area with the series list and chapter list areas."""
        main_area = QFrame(self)

        fav_series_area = QListWidget()
        chapter_area = QFrame()

        splitter = QSplitter(Qt.Horizontal)
        splitter.addWidget(fav_series_area)
        splitter.addWidget(chapter_area)

        hbox = QHBoxLayout()
        hbox.addWidget(splitter)
        main_area.setLayout(hbox)

        self.setCentralWidget(main_area)

        return fav_series_area, chapter_area

    def add_queue_area(self):
        """Add the dock area for the download queue."""
        queue_dock = QDockWidget('Queue')
        queue_dock.setAllowedAreas(Qt.RightDockWidgetArea)
        queue_area = QScrollArea()
        queue_dock.setWidget(queue_area)
        self.addDockWidget(Qt.RightDockWidgetArea, queue_dock)

        return queue_dock, queue_area

    def add_menubar(self):
        """Add the menubar to the application."""
        menubar = self.menuBar()
        file_menu = menubar.addMenu('File')
        pref_act = QAction('Preferences', self)
        file_menu.addAction(pref_act)

        view_menu = menubar.addMenu('View')

        view_menu.addAction(self.queue_dock.toggleViewAction())
