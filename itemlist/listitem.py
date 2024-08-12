"""
Module offers list item with specific moving area
"""

from PyQt6.QtWidgets import QWidget, QLabel
from PyQt6.QtWidgets import QHBoxLayout, QPushButton
from PyQt6.QtGui import QIcon
from PyQt6.QtCore import Qt, pyqtSlot, QSize
from PyQt6.QtCore import QPoint

class ListItem(QWidget):

    """
    Test ListItem
    """

    def __init__(self, width, height,\
        list_item_obj, communicator, context, parent):

        super().__init__(parent=parent)
        self.parent = parent
        self.communicator = communicator
        self.context = context
        self.list_item_obj = list_item_obj
        self.clicked_at = False
        self.click_p = QPoint(0, 0)
        self.move_p = QPoint(0, 0)

        # indicates wheather the item is finished or not
        if list_item_obj.task_complete == 0:
            self.task_complete = False
        else:
            self.task_complete = True

        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self.check_button = QPushButton()
        self.check_button.setFixedSize(height, height)
        self.check_button.setIconSize(QSize(height-4, height-4))
        if self.task_complete:
            self.check_button.setIcon(QIcon("./img/check.png"))
        else:
            self.check_button.setIcon(QIcon("./img/todo.png"))
        self.check_button.setStyleSheet(
            """
            background-color: white;
            border: 0px;
            """
        )
        self.check_button.clicked.connect(self.check_button_clicked)

        self.description_label = QLabel(list_item_obj.task_description)
        self.description_label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)

        self.deadline_label =\
            QLabel(list_item_obj.deadline_date.strftime(self.context.date_format))
        self.deadline_label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)

        self.set_fixed()

        layout.addWidget(self.check_button)
        layout.addWidget(self.description_label, stretch=1)
        layout.addWidget(self.deadline_label)

        self.setLayout(layout)
        self.setFixedSize(width, height)

    @pyqtSlot()
    def check_button_clicked(self):

        """handle check event, remove current item from list"""

        self.task_complete = not self.task_complete

        if self.task_complete:
            self.check_button.setIcon(QIcon("./img/check.png"))
            self.list_item_obj.task_complete = 1
        else:
            self.check_button.setIcon(QIcon("./img/todo.png"))
            self.list_item_obj.task_complete = 0

        self.communicator.SIGNAL_LISTITEM_UPDATE.emit(\
            self.list_item_obj.key())

    def set_position(self, position):

        """reset position of item"""

        self.list_item_obj.position = position

    def prepare_move(self):

        """prepare list for item swaps"""

        self.parent.item_place_holder.show()

    def reset_move(self):

        """reset state of list to what it was before the move"""

        self.parent.layout.replaceWidget(\
            self.parent.item_place_holder, self)
        self.parent.moving_item = None
        self.parent.item_place_holder.hide()

    def mousePressEvent(self, event): # pylint: disable=invalid-name

        """mouse press event handler"""

        self.prepare_move()
        self.click_p = QPoint(event.pos().x(), event.pos().y())
        self.move_p = self.mapToParent(QPoint(event.pos().x(), event.pos().y()))
        self.set_moving()
        self.set_moving()
        self.clicked_at = True

    def mouseReleaseEvent(self, event): # pylint: disable=invalid-name, unused-argument

        """mouse press event handler"""

        self.set_fixed()
        self.set_fixed()
        self.clicked_at = False
        self.reset_move()

        self.communicator.SIGNAL_ITEMLIST_REFRESH_POSITION.emit()

    def mouseMoveEvent(self, event): # pylint: disable=invalid-name

        """mouse move event handler"""

        if not self.clicked_at:
            return

        elem_coords = self.mapToParent(QPoint(self.rect().x(), self.rect().y()))
        event_coords = QPoint(event.pos().x(), event.pos().y())
        top_coords = self.parent.item_place_holder.get_top()
        p_coords = self.mapToParent(event_coords) - self.click_p

        height = self.rect().height()

        # use bubble swap technique to switch items in the layout
        if self.parent.moving_item != self:
            if self.parent.moving_item is not None:
                self.parent.layout.replaceWidget(\
                    self.parent.item_place_holder, self.parent.moving_item)
            self.parent.moving_item = self
            self.parent.layout.replaceWidget(self, self.parent.item_place_holder)
            self.raise_()
        else:
            cur = None
            moving_direction = event_coords - self.click_p
            if moving_direction.y() > 0:
                if elem_coords.y() > top_coords.y() + height/2:
                    ind = self.parent.layout.indexOf(self.parent.item_place_holder)
                    count = self.parent.layout.count()
                    if ind < count-1:
                        cur = self.parent.layout.itemAt(ind+1).widget()
            else:
                if elem_coords.y() < top_coords.y() - height/2:
                    ind = self.parent.layout.indexOf(self.parent.item_place_holder)
                    if ind > 0:
                        cur = self.parent.layout.itemAt(ind-1).widget()

            self.parent.layout.replaceWidget(\
                cur, self.parent.item_switcher)
            self.parent.layout.replaceWidget(\
                self.parent.item_place_holder, cur)
            self.parent.layout.replaceWidget(\
                self.parent.item_switcher, self.parent.item_place_holder)

        # follow item with scrollbar
        requested_p = self.mapToParent(event_coords)
        diff = requested_p.y() - self.move_p.y()
        max_mouse_value = self.parent.get_max_mouse_value()
        min_mouse_value = self.parent.get_min_mouse_value()
        # down
        if diff > 0 and requested_p.y() > max_mouse_value:
            delta = requested_p.y() - max_mouse_value
            self.cursor().setPos(self.cursor().pos().x(), self.cursor().pos().y() - delta)
            self.parent.follow_scrollbar(self.context.scroll_delta)
        # up
        elif diff < 0 and requested_p.y() < min_mouse_value:
            delta = requested_p.y() - min_mouse_value
            self.cursor().setPos(self.cursor().pos().x(), self.cursor().pos().y() - delta)
            self.parent.follow_scrollbar(-self.context.scroll_delta)

        self.move_p = requested_p

        self.move(QPoint(elem_coords.x(), p_coords.y()))

    def set_moving(self):

        """reform current list entry to look like moving"""

        self.setStyleSheet(
            """
            padding-left: 5px;
            padding-right: 5px;
            """
        )
        self.description_label.setStyleSheet(
            """
            background-color: white;
            border-left: 2px solid black;
            border-top: 2px solid black;
            border-bottom: 2px solid black;
            """
        )
        self.deadline_label.setStyleSheet(
            """
            background-color: white;
            border-right: 2px solid black;
            border-top: 2px solid black;
            border-bottom: 2px solid black;
            """
        )

    def set_fixed(self):

        """reform current list entry to look like fixed"""

        self.setStyleSheet(
            """
            padding-left: 5px;
            padding-right: 5px;
            """
        )
        self.description_label.setStyleSheet(
            """
            background-color: white;
            border-left: 1px solid gray;
            border-top: 1px solid gray;
            border-bottom: 1px solid gray;
            """
        )
        self.deadline_label.setStyleSheet(
            """
            background-color: white;
            border-right: 1px solid gray;
            border-top: 1px solid gray;
            border-bottom: 1px solid gray;
            """
        )
