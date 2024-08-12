"""
Module offers list item with specific moving area
(This is a prototype that looks really bad)
"""

from PyQt6.QtWidgets import QWidget, QLabel
from PyQt6.QtWidgets import QHBoxLayout, QPushButton
from PyQt6.QtCore import QPoint

class ItemMover(QPushButton):

    """
    Test item mover
    """

    def __init__(self, size_x, size_y, parent):
        super().__init__(parent=parent)
        self.parent = parent
        self.setFixedSize(size_x, size_y)
        self.set_fixed()

    def set_moving(self):

        """reform entry to look like moving"""

        self.setStyleSheet(\
            """
            background-color: red;
            """)

    def set_fixed(self):

        """reform entry to look like fixed"""

        self.setStyleSheet(\
            """
            background-color: green;
            """)

    def mousePressEvent(self, event): # pylint: disable=invalid-name

        """mouse press event handler"""

        self.parent.prepare_move()
        self.parent.click_p = self.mapToParent(QPoint(event.pos().x(), event.pos().y()))
        self.set_moving()
        self.parent.set_moving()
        self.parent.clicked_at = True

    def mouseReleaseEvent(self, event): # pylint: disable=invalid-name, unused-argument

        """mouse press event handler"""

        self.set_fixed()
        self.parent.set_fixed()
        self.parent.clicked_at = False
        self.parent.reset_move()

class ListItemWithMover(QWidget):

    """
    Test ListItem
    """

    def __init__(self, size_x, size_y, text, parent):
        super().__init__(parent=parent)
        self.parent = parent
        self.clicked_at = False

        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self.mover = ItemMover(30, size_y, self)

        self.label = QLabel(text)
        self.set_fixed()

        layout.addWidget(self.mover)
        layout.addWidget(self.label)

        self.setLayout(layout)
        self.setFixedSize(size_x, size_y)

    def set_moving(self):

        """reform current list entry to look like moving"""

        self.label.setStyleSheet(\
            """
            background-color: green;
            margin-left: 2px;
            padding-left: 5px;
            """)
        self.setStyleSheet("border: 2px solid black;")

    def set_fixed(self):

        """reform current list entry to look like fixed"""

        self.label.setStyleSheet(\
            """
            background-color: red;
            margin-left: 2px;
            padding-left: 5px;
            """)
        self.setStyleSheet("border: 0px;")

    def prepare_move(self):

        """prepare list for item swaps"""

        self.parent.item_place_holder.show()

    def reset_move(self):

        """reset state of list to what it was before the move"""

        self.parent.layout.replaceWidget(\
            self.parent.item_place_holder, self)
        self.parent.moving_item = None
        self.parent.item_place_holder.hide()

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

        self.move(QPoint(elem_coords.x(), p_coords.y()))
