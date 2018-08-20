"""Main window frame for the GUI."""
from PyQt5.QtWidgets import (QMainWindow, QHBoxLayout, QFrame,
                             QAction, QDockWidget, QSplitter, QComboBox,
                             QWidget, QSizePolicy, QLineEdit, QToolBar,
                             QDesktopWidget, QStyleFactory)
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt, QSize

from manga_saver.views import ICONS
from manga_saver.views.chapter_list import ChapterListWidget
from manga_saver.views.queue_area import QueueArea
from manga_saver.views.fav_series_list import FavSeriesListWidget


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
        self.setWindowTitle('Saber')
        self.toolbar = self._add_top_bar()

        self.statusBar().showMessage('Choose a source')

        self.fav_series_area, self.chapter_area = self._add_main_area()

        self.queue_dock, self.queue_area = self._add_queue_area()

        self._add_menubar()

        self.setMinimumSize(800, 600)
        self.center()

    def _add_top_bar(self):
        """Add the top bar with source dropdown and search bar."""
        toolbar = SourceToolBar()
        self.addToolBar(toolbar)
        toolbar.setMovable(False)
        return toolbar

    def _add_main_area(self):
        """Add the main area with the series list and chapter list areas."""
        fav_series_area = QFrame()
        fav_series_area.setMaximumWidth(250)
        box = QHBoxLayout(fav_series_area)
        fav_series_list = FavSeriesListWidget()
        box.addWidget(fav_series_list)

        chapter_area = ChapterListWidget('Series title')

        splitter = QSplitter(Qt.Horizontal)
        splitter.addWidget(fav_series_area)
        splitter.addWidget(chapter_area)
        splitter.setCollapsible(1, False)
        splitter.setSizes([250])

        self.setCentralWidget(splitter)

        return fav_series_list, chapter_area

    def _add_queue_area(self):
        """Add the dock area for the download queue."""
        queue_dock = QDockWidget('Queue')
        queue_dock.setStyle(QStyleFactory.create('Fusion'))
        queue_dock.setMinimumWidth(250)
        queue_dock.setAllowedAreas(Qt.RightDockWidgetArea)
        queue_area = QueueArea()
        queue_dock.setWidget(queue_area)
        self.addDockWidget(Qt.RightDockWidgetArea, queue_dock)

        return queue_dock, queue_area

    def _add_menubar(self):
        """Add the menubar to the application."""
        menubar = self.menuBar()
        file_menu = menubar.addMenu('File')
        pref_act = QAction('Preferences', self)
        file_menu.addAction(pref_act)

        view_menu = menubar.addMenu('View')

        view_menu.addAction(self.queue_dock.toggleViewAction())

    def center(self):
        """Center the window on the screen."""
        frame = self.frameGeometry()
        center_point = QDesktopWidget().availableGeometry().center()
        frame.moveCenter(center_point)
        self.move(frame.topLeft())


class SourceToolBar(QToolBar):
    """Top bar of the main window, which manages sources and searching."""

    def __init__(self):
        """Create and populate the source tool bar."""
        super(SourceToolBar, self).__init__()

        self.yellow_icon = QIcon(ICONS['YELLOW_STATUS'])
        self.red_icon = QIcon(ICONS['RED_STATUS'])
        self.green_icon = QIcon(ICONS['GREEN_STATUS'])

        self.init_ui()

    def init_ui(self):
        """Build an empty source tool bar."""
        self.addWidget(QWidget())

        source_input = QComboBox()
        source_input.setMinimumWidth(150)
        source_input.setToolTip('Manga Source')
        source_input.addItem('No sources added')
        self.addWidget(source_input)

        refresh_act = QAction(self.yellow_icon, 'Refresh Source', self)
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

        search_icon = QIcon(ICONS['SEARCH'])
        search_act = QAction(search_icon, 'Search by Title', self)

        # search_act.triggered.connect(self.search_title)
        self.addAction(search_act)

        self.addWidget(QWidget())

        self.setIconSize(QSize(20, 20))
        self.setEnabled(False)
