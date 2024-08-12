"""
Module offers a todo list with movable tasks
"""

from datetime import datetime, date
from PyQt6.QtWidgets import QWidget, QDialog
from PyQt6.QtWidgets import QHBoxLayout, QVBoxLayout, QPushButton
from PyQt6.QtWidgets import QLineEdit, QLabel
from PyQt6.QtWidgets import QScrollArea, QSizePolicy, QSpacerItem, QCalendarWidget
from PyQt6.QtGui import QPalette, QIcon, QFont
from PyQt6.QtCore import Qt, pyqtSlot, QPoint, QDate, QSize
import dbobj.dbwrapper as dbwrapper

from itemlist.listitemplaceholder import ListItemPlaceholder
from itemlist.listitem import ListItem

class ConfigNewItem(QDialog):

    """
    Class represents config widget for new items
    """

    def __init__(self, width, height, communicator, context, parent):
        super().__init__(parent=parent)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Dialog)
        self.setStyleSheet("QDialog{border:2px solid black}")

        self.parent = parent
        self.context = context
        self.communicator = communicator

        layout = QVBoxLayout()

        self.entry = QLineEdit("Enter new task")
        self.entry.setFixedHeight(height)
        self.entry.selectAll()

        self.calendar = QCalendarWidget()
        today = datetime.today().date()
        self.calendar.setSelectedDate(QDate(today.year, today.month, today.day))

        ok_button = QPushButton("Ok")
        cancel_button = QPushButton("Cancel")

        ok_button.clicked.connect(self.ok_button)
        cancel_button.clicked.connect(self.cancel_button)

        button_layout = QHBoxLayout()
        button_layout.addWidget(cancel_button)
        button_layout.addWidget(ok_button)
        ok_button.activateWindow()

        layout.addWidget(self.entry, stretch=1)
        layout.addWidget(self.calendar)
        layout.addLayout(button_layout, stretch=1)

        self.setFixedWidth(width)

        self.setLayout(layout)
        self.move_slot()
        self.show()


    @pyqtSlot()
    def move_slot(self):

        """move widget to correct position"""

        geo = self.parent.rect()
        pos = self.parent.mapToGlobal(QPoint(geo.x(), geo.y() + geo.height()))
        self.move(pos.x(), pos.y() + 2)

    @pyqtSlot()
    def ok_button(self):

        """ok button slot"""

        deadline = self.calendar.selectedDate()
        self.communicator.SIGNAL_LISTITEM_ADDED.emit(self.entry.text(), deadline)
        self.close()

    @pyqtSlot()
    def cancel_button(self):

        """cancel button slot"""

        self.close()


class FunctionalBar(QWidget):

    """
    Class provides functional space for the item list
    """

    def __init__(self, width, height, communicator, context, parent):
        super().__init__(parent=parent)
        self.parent = parent
        self.communicator = communicator
        self.context = context
        self.item_width = width
        self.item_height = height

        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.setAlignment(Qt.AlignmentFlag.AlignLeft)

        add_button = QPushButton()
        add_button.setFixedSize(height, height)
        add_button.setIconSize(QSize(height-2, height-2))
        add_button.setIcon(QIcon("./img/additem.png"))
        add_button.setStyleSheet("border: 0px;")

        clean_button = QPushButton()
        clean_button.setFixedSize(height, height)
        clean_button.setIconSize(QSize(height-2, height-2))
        clean_button.setIcon(QIcon("./img/removefinishedtasks.png"))
        clean_button.setStyleSheet("border: 0px;")

        new_font = QFont("MS Shell Dlg 2", 12)
        self.task_count = QLabel()
        self.task_count.setFont(new_font)
        self.task_count.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        self.task_count.setStyleSheet(\
            "padding-right: " + str(self.context.scroll_bar_offset) + "px;")

        # set initial amount for list (empty)
        self.set_listitem_count(0)

        add_button.clicked.connect(self.add_button_clicked)
        clean_button.clicked.connect(self.clean_button_clicked)

        layout.addWidget(add_button)
        layout.addWidget(clean_button)
        layout.addItem(QSpacerItem(10, 10, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum))
        layout.addWidget(self.task_count)

        self.setLayout(layout)
        self.setFixedSize(width, height)

    @pyqtSlot()
    def add_button_clicked(self):

        """add button slot"""

        ConfigNewItem(self.item_width, self.item_height,\
            self.communicator, self.context, self)

    @pyqtSlot()
    def clean_button_clicked(self):

        """clean button slot"""

        self.communicator.SIGNAL_ITEMLIST_CLEAN.emit()

    def set_listitem_count(self, listitem_count):

        """one listitem removed itself, update itemlist"""

        self.task_count.setText(str(listitem_count) + " active tasks")

class ItemList(QWidget):

    """
    Test QListView
    """

    def __init__(self, item_width, item_height, communicator, context, parent):
        super().__init__()
        self.context = context
        self.communicator = communicator
        self.parent = parent

        self.item_width = item_width
        self.item_height = item_height

        self.layout = QVBoxLayout()
        self.layout_spacing = 2
        self.layout.setContentsMargins(0, 2, 0, 0)
        self.layout.setSpacing(self.layout_spacing)
        self.layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        self.item_place_holder = ListItemPlaceholder(\
            self.item_width, self.item_height, self)
        self.item_place_holder.hide()
        self.item_switcher = ListItemPlaceholder(0, 0, self)
        self.item_switcher.hide()
        self.moving_item = None

        self.main_list_widget = QWidget()
        self.main_list_widget.setLayout(self.layout)
        self.set_itemlist_height()

        palette = QPalette()
        palette.setColor(QPalette.ColorRole.Window, Qt.GlobalColor.white)
        self.main_list_widget.setAutoFillBackground(True)
        self.main_list_widget.setPalette(palette)

        self.functional_bar = FunctionalBar(\
            item_width + self.context.scroll_bar_offset,\
                self.context.date_picker_head_height,\
                    communicator, context, self)

        dbwrapper.TodoListItem.reload_from_db(\
            self.context.todo_list_items,\
                self.context.db_file_name)

        temp_list = list(self.context.todo_list_items.values())
        temp_list = sorted(temp_list, key=lambda pos: pos.position)
        for i in temp_list:
            self.layout.insertWidget(i.position, ListItem(\
                self.item_width, self.item_height,\
                    i,\
                        self.communicator, self.context, self))
        self.functional_bar.set_listitem_count(self.layout.count())

        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True) # without this one, it doesn't work!
        self.scroll_area.setWidget(self.main_list_widget)

        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(2)

        main_layout.addWidget(self.functional_bar)
        main_layout.addWidget(self.scroll_area, stretch=1)

        self.communicator.SIGNAL_LISTITEM_ADDED.connect(self.add_listitem_slot)
        self.communicator.SIGNAL_ITEMLIST_CLEAN.connect(self.cleanup_itemlist)
        self.communicator.SIGNAL_LISTITEM_UPDATE.connect(self.update_list_item)
        self.communicator.SIGNAL_ITEMLIST_REFRESH_POSITION.connect(self.refresh_db_position)

        self.setFixedWidth(item_width + self.context.scroll_bar_offset)
        self.setLayout(main_layout)

    def get_max_mouse_value(self):

        """
        Return the max position for the mouse to be inside the
        scroll area
        """

        scroll_b = self.scroll_area.verticalScrollBar()
        return scroll_b.value() + scroll_b.height()

    def get_min_mouse_value(self):

        """
        Return the min position for the mouse to be inside the
        scroll area
        """

        scroll_b = self.scroll_area.verticalScrollBar()
        return scroll_b.value()

    def follow_scrollbar(self, dy_value):

        """set scrollbar to follow the mouse if it goes out of scope"""

        val = self.scroll_area.verticalScrollBar().value()
        self.scroll_area.verticalScrollBar().setValue(val + dy_value)

    def resizeEvent(self, event): # pylint: disable=invalid-name, unused-argument

        """catch parents resize and drag along the scroll widget"""

        self.set_itemlist_height()

    def set_itemlist_height(self):

        """set height of itemlist widget according to item count"""

        height1 = self.layout.count()*\
            (self.item_height + self.layout_spacing) +self.layout_spacing
        height2 = self.height()

        if height1 > height2:
            self.main_list_widget.setFixedHeight(height1)
        else:
            self.main_list_widget.setFixedHeight(height2)

    @pyqtSlot(int)
    def update_list_item(self, todo_list_item_key):

        """update db item with current task_complete state"""

        dbwrapper.TodoListItem.update_by_db_id(\
            self.context.todo_list_items[todo_list_item_key],\
                self.context.db_file_name)

    @pyqtSlot()
    def cleanup_itemlist(self):

        """cleanup itemlist, remove all checked items"""

        to_remove = []
        for i in range(self.layout.count()-1, -1, -1):
            item = self.layout.itemAt(i)
            if item.widget().task_complete:
                to_remove.append(i)
                self.layout.removeItem(item)
                item.widget().setParent(None)

        self.functional_bar.set_listitem_count(self.layout.count())
        self.set_itemlist_height()

        dbwrapper.TodoListItem.delete_all_completed(\
            self.context.todo_list_items,\
                self.context.db_file_name)

    @pyqtSlot()
    def refresh_db_position(self):

        """update position of items in db"""

        for i in range(0, self.layout.count()):
            widget = self.layout.itemAt(i).widget()
            widget.set_position(i)

        dbwrapper.TodoListItem.update_all_positions(\
            self.context.todo_list_items,\
                self.context.db_file_name)

    @pyqtSlot(str, QDate)
    def add_listitem_slot(self, task_description, deadline_date):

        """add one new task at the top of the layout"""

        deadline = date(\
            deadline_date.year(), deadline_date.month(), deadline_date.day())

        obj = dbwrapper.TodoListItem.new(-1, 0, task_description, deadline)
        self.layout.insertWidget(0, ListItem(\
            self.item_width, self.item_height,\
                obj,\
                    self.communicator, self.context, self))

        self.functional_bar.set_listitem_count(self.layout.count())
        self.set_itemlist_height()

        # make sure, db is up to date
        dbwrapper.TodoListItem.to_db(\
            obj, self.context.todo_list_items,\
                self.context.db_file_name)

        self.communicator.SIGNAL_ITEMLIST_REFRESH_POSITION.emit()
