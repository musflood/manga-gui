"""Main window frame for the GUI."""
import os

from PyQt5.QtWidgets import (QMainWindow, QHBoxLayout, QFrame, QScrollArea,
                             QAction, QDockWidget, QListWidget, QSplitter,
                             QComboBox, QWidget, QSizePolicy, QLineEdit,
                             QToolBar)
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt, QSize

from manga_saver.views import ICON_DIR
from manga_saver.views.chapterlist import ChapterListWidget


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
        # self.source_input, self.refresh_act = self.add_top_bar()
        self.toolbar = self.add_top_bar()

        self.statusBar().showMessage('Choose a source')

        self.fav_series_area, self.chapter_area = self.add_main_area()

        self.queue_dock, self.queue_area = self.add_queue_area()

        self.add_menubar()

        self.setMinimumSize(700, 500)

    def add_top_bar(self):
        """Add the top bar with source dropdown and search bar."""
        toolbar = SourceToolBar()
        self.addToolBar(toolbar)
        toolbar.setMovable(False)
        return toolbar

    def add_main_area(self):
        """Add the main area with the series list and chapter list areas."""
        fav_series_area = QFrame()
        fav_series_area.setMaximumWidth(200)
        box = QHBoxLayout(fav_series_area)
        fav_series_list = QListWidget()
        box.addWidget(fav_series_list)

        chapter_area = ChapterListWidget()

        splitter = QSplitter(Qt.Horizontal)
        splitter.addWidget(fav_series_area)
        splitter.addWidget(chapter_area)
        splitter.setCollapsible(1, False)

        self.setCentralWidget(splitter)

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


class SourceToolBar(QToolBar):
    """Top bar of the main window, which manages sources and searching."""

    def __init__(self):
        """Create and populate the source tool bar."""
        super(SourceToolBar, self).__init__()

        self.YELLOW_ICON = QIcon(os.path.join(ICON_DIR, 'yellowdot.png'))
        self.RED_ICON = QIcon(os.path.join(ICON_DIR, 'reddot.png'))
        self.GREEN_ICON = QIcon(os.path.join(ICON_DIR, 'greendot.png'))

        self.init_ui()

    def init_ui(self):
        """Build an empty source tool bar."""
        self.addWidget(QWidget())

        source_input = QComboBox()
        source_input.setMinimumWidth(150)
        source_input.setToolTip('Manga Source')
        source_input.addItem('No sources added')
        self.addWidget(source_input)

        refresh_act = QAction(self.YELLOW_ICON, 'Refresh Source', self)
        # refresh_act.triggered.connect(self.refresh_source)
        refresh_act.setVisible(False)
        self.addAction(refresh_act)

        spacer = QWidget()
        spacer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.addWidget(spacer)

        search_bar = QLineEdit()
        search_bar.setMaximumWidth(150)
        search_bar.setPlaceholderText('Search Series...')
        self.addWidget(search_bar)

        search_icon = QIcon(os.path.join(ICON_DIR, 'search.png'))
        search_act = QAction(search_icon, 'Search by Title', self)

        # search_act.triggered.connect(self.refresh_source)
        self.addAction(search_act)

        self.addWidget(QWidget())

        self.setIconSize(QSize(20, 20))
        self.setEnabled(False)
