"""Widgets for the list of a user's favorite series."""
from datetime import datetime

from PyQt5.QtWidgets import (QListWidget, QAbstractItemView, QListWidgetItem,
                             QWidget, QHBoxLayout, QLabel, QVBoxLayout)
from PyQt5.QtGui import QPixmap, QFont

from manga_saver.views import ICONS


class FavSeriesListWidget(QListWidget):
    """List area for user's chosen favorite series."""

    def __init__(self):
        """List the user's chosen favorite series."""
        super(FavSeriesListWidget, self).__init__()

        self.init_ui()

    def init_ui(self):
        """Build the list area for the fav series."""
        self.setDragDropMode(QAbstractItemView.InternalMove)
        self.setStyleSheet('''
            QListWidget::item:focus {
                background: #4594EE;
            }
            QListWidget::item:selected {
                background: #4594EE;
            }
        ''')
        self.currentItemChanged.connect(self._change_highlighted_item)

    def _change_highlighted_item(self, current, previous):
        """Change the highlighed list item when the selection changes."""
        if current:
            current = self.itemWidget(current)
            current.set_highlighted(True)
        if previous:
            previous = self.itemWidget(previous)
            previous.set_highlighted(False)

    def add_series(self, title):
        """Add a favorite series to the list."""
        item_widget = FavSeriesListWidgetItem(title)
        list_item = QListWidgetItem()
        list_item.setSizeHint(item_widget.sizeHint())
        self.addItem(list_item)
        self.setItemWidget(list_item, item_widget)
        return item_widget


class FavSeriesListWidgetItem(QWidget):
    """Details for a favorite series in the fav series list."""

    TITLE_FONT = QFont()
    TITLE_FONT.setPointSize(15)

    UPDATED_FONT = QFont()
    UPDATED_FONT.setPointSize(10)
    UPDATED_FONT.setItalic(True)

    def __init__(self, title):
        """Create an entry for the fav series list."""
        super(FavSeriesListWidgetItem, self).__init__()
        self.title = title
        self.last_updated = None

        self.check_icon = QPixmap(ICONS['OUTLINE_CHECK'])
        self.white_check_icon = QPixmap(ICONS['OUTLINE_CHECK_WHITE'])

        self.init_ui()

    def init_ui(self):
        """Build the list entry."""
        self.setStyleSheet('''
            QLabel {
                padding: 0;
            }
        ''')

        self.layout = QHBoxLayout(self)
        vbox = QVBoxLayout()
        vbox.setSpacing(0)

        self.title_label = QLabel(self.title)
        self.title_label.setFont(self.TITLE_FONT)
        self.title_label.setWordWrap(True)
        vbox.addWidget(self.title_label)

        self.updated_label = QLabel('Never updated')
        self.updated_label.setFont(self.UPDATED_FONT)
        self.updated_label.setWordWrap(True)
        vbox.addWidget(self.updated_label)

        self.layout.addLayout(vbox)
        self.layout.addStretch(1)

        self.check_label = QLabel()
        self.check_label.setPixmap(self.check_icon)
        self.layout.addWidget(self.check_label)

        self.check_label.setVisible(False)

    def set_highlighted(self, active):
        """Highlight the item if the list item is active."""
        stylesheet = '''
            QLabel {{
                color: {color}
            }}
        '''
        if active:
            self.setStyleSheet(stylesheet.format(color='white'))
            self.check_label.setPixmap(self.white_check_icon)
        else:
            self.setStyleSheet(stylesheet.format(color='black'))
            self.check_label.setPixmap(self.check_icon)

    def set_complete(self, complete):
        """Add a checkmark to the series if it is completely downloaded."""
        self.check_label.setVisible(complete)

    def set_last_updated(self, last_updated):
        """Set the last time the series was checked from the source."""
        if last_updated is None:
            return self.updated_label.setText('Never updated')

        now = datetime.now()
        d = now - last_updated

        if d.days:
            text = f'Updated {d.days} day{"s" if d.days > 1 else ""} ago'
        elif d.seconds > 3600:
            hours = d.seconds // 3600
            text = f'Updated {hours} hour{"s" if hours > 1 else ""} ago'
        elif d.seconds > 60:
            mins = d.seconds // 60
            text = f'Updated {mins} minute{"s" if mins > 1 else ""} ago'
        else:
            text = 'Updated just now'

        self.updated_label.setText(text)
