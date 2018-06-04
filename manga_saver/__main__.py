"""Start the GUI for the manga saver."""

import sys

from PyQt5.QtWidgets import QApplication

from manga_saver.views.mainwindow import MainWindow

app = QApplication(sys.argv)
window = MainWindow()
sys.exit(app.exec_())
