"""
Module represents a canvas containing only a horizontal scrollbar
"""

from PyQt6.QtCore import pyqtSlot
from PyQt6.QtWidgets import QWidget

class HorizontalScrollBar(QWidget):

    """
    Class represents a horizontal scrollbar
    """

    def __init__(self, communicator, context, parent):
        super().__init__()
        self.communicator = communicator
        self.context = context
        self.parent = parent

        # widget that should be updated after a paint event
        # can be registered here
        self.widget = None

        self.linked_scrollbars = list()
        self.linked_vertical_scrollbars = list()

        self.communicator.SIGNAL_ENTRY_RESIZED.connect(self.resize_canvas)
        self.communicator.SIGNAL_SCHEDULE_RESIZED.connect(self.resize_canvas)
        self.communicator.SIGNAL_DATES_CHANGED.connect(self.resize_canvas)
        self.communicator.SIGNAL_SCROLLBAR_CHANGE_REQUIRED.connect(self.add_delta)

        self.resize_canvas()

    def link_scroll_bar(self, scroll_bar):

        """link a scrollbar to the one of this windows parent"""

        self.linked_scrollbars.append(scroll_bar)

    def link_vertical_scroll_bar(self, scroll_bar):

        """link a scrollbar to the one of this windows parent"""

        self.linked_vertical_scrollbars.append(scroll_bar)

    def get_width(self):

        """return current width of the head bar canvas"""

        return self.context.time_column_width + self.context.left_offset +\
            self.context.day_count*self.context.box_width +\
                2*self.context.scroll_bar_offset

    def paintEvent(self, event): # pylint: disable=invalid-name, unused-argument

        """paint the entry canvas"""

        for i in self.linked_scrollbars:
            i.setValue(self.parent.horizontalScrollBar().value())

        for i in self.linked_vertical_scrollbars:
            i.setValue(self.parent.verticalScrollBar().value())

        # update a registered widget if it is not None
        # use this if the scrollbar was changed by some signal
        # from somewhere else and after the original scrollbar was changed
        # the connected widget requires one more update
        if self.widget is not None:
            self.widget.update()
            self.widget = None

    @pyqtSlot(int, QWidget)
    def add_delta(self, delta, widget):

        """set value for scrollbar"""

        scroll_b = self.parent.horizontalScrollBar()
        scroll_b.setValue(scroll_b.value() + delta)
        self.widget = widget

    @pyqtSlot()
    def resize_canvas(self):

        """resize canvas according to scale"""
        scale = self.context.scale
        width = int((self.get_width())*scale)
        height = self.context.scroll_bar_offset + 4
        self.setFixedSize(width, height)

        self.parent.setFixedHeight(height)
