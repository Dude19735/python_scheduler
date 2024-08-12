"""
Module offers list item placeholder to switch items in list
"""

from PyQt6.QtWidgets import QWidget
from PyQt6.QtCore import QPoint

class ListItemPlaceholder(QWidget):

    """
    ListItem placeholder in order to move the current list item well
    """

    def __init__(self, width, height, parent):
        super().__init__(parent=parent)
        self.parent = parent
        self.setFixedSize(width, height)

    def get_top(self):

        """get top and bottom edge points"""

        x_coord = self.rect().x()
        y_coord = self.rect().y()
        top = self.mapToParent(QPoint(x_coord, y_coord))

        return top
