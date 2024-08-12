"""
Module offers time boxes to use as y axis for the schedule
"""

import random
from PyQt6.QtWidgets import QWidget
from PyQt6.QtGui import QPainter, QBrush, QPalette
from PyQt6.QtCore import Qt, QRect, pyqtSlot
from helpers.canvasgrid import CanvasGrid

class TimeBox(QRect):

    """
    Class represents one box that contains a hh:mm - hh:mm string
    """

    def __init__(self, fromTime, toTime, rowNum, colNum, x, y, width, height, context):
        self.from_time = fromTime
        self.to_time = toTime
        self.row_num = rowNum
        self.col_num = colNum
        self.x_coord = x
        self.y_coord = y
        self.width = width
        self.height = height
        self.context = context

        super().__init__(\
            x+self.context.box_border_width,\
                y+self.context.box_border_width,\
                    width - 2*self.context.box_border_width,\
                        height - 2*self.context.box_border_width)

    def __del__(self):
        pass

    def get_x(self):

        """Return x coordinate"""

        return self.x_coord

    def get_y(self):

        """Return y coordinate"""

        return self.y_coord

    def get_text(self):

        """Return time string separated by a dash"""

        return self.from_time + " - " + self.to_time

    def paint(self, painter, brush):

        """Paint methode"""

        painter.setPen(Qt.GlobalColor.black)
        brush.setColor(self.context.time_box_background_color)
        painter.fillRect(self, brush)
        painter.drawText(self, Qt.AlignmentFlag.AlignCenter, self.get_text())

class TimesCanvas(QWidget):

    """
    Class represents time boxes containing all times from start_offset to
    start_offset + 24 hours
    """

    def __init__(self, communicator, context, parent):
        super().__init__(parent=parent)
        self.parent = parent
        self.context = context
        self.communicator = communicator
        self.time_boxes = list()
        self.linked_vertical_scrollbars = list()

        palette = QPalette()
        palette.setColor(QPalette.ColorRole.Window, self.context.canvas_background_color)
        self.setAutoFillBackground(True)
        self.setPalette(palette)

        self.communicator.SIGNAL_ENTRY_RESIZED.connect(self.resize_canvas)
        self.communicator.SIGNAL_SCHEDULE_RESIZED.connect(self.resize_canvas)

        self.grid = None
        self.grid_height = 0

        self.create_time_boxes()
        self.create_grid()
        self.resize_canvas()

    def link_vertical_scroll_bar(self, scroll_bar):

        """link a scrollbar to the one of this windows parent"""

        self.linked_vertical_scrollbars.append(scroll_bar)

    def get_interval_count(self):

        """return the amount of time boxes to get row count for schedule"""

        return len(self.time_boxes)

    def time_to_string(self, hours, minutes):

        """convert integer hours and minutes to hh:mm formated string"""

        return "{:02}:{:02}".format(int(hours), int(minutes))

    def create_time_boxes(self):

        """
        Create all time boxes containing 'hh:mm - hh:mm'
        These get painted in a container widget, so left and top offset don't count
        """

        row_num = 0
        width = self.context.time_column_width
        height = self.context.box_height
        for hour in range(0 + self.context.start_time_offset, 24 + self.context.start_time_offset):
            if hour > 23:
                hour = hour - 24
            for minute in range(0, 59, self.context.time_interval):
                next_h = hour
                next_m = minute + self.context.time_interval
                if next_m > 59:
                    next_h = hour+1
                    next_m = 0

                x_coord = self.context.left_offset
                y_coord = self.context.top_offset + row_num*self.context.box_height

                self.time_boxes.append(TimeBox(\
                    self.time_to_string(hour, minute),\
                        self.time_to_string(next_h, next_m),\
                            row_num, 0,\
                                x_coord, y_coord,\
                                    width, height,\
                                        self.context\
                                            ))

                row_num = row_num + 1

    def create_grid(self):

        """create the canvas grid"""

        width = self.context.time_column_width
        height = self.get_interval_count()*self.context.box_height
        startx = self.context.left_offset
        starty = self.context.top_offset
        intervalx = self.context.time_column_width
        intervaly = self.context.box_height

        self.grid = CanvasGrid(width, height, startx, starty, intervalx, intervaly, self.context)
        self.grid_height = self.grid.get_height()

    def paintEvent(self, event): # pylint: disable=invalid-name, unused-argument

        """paint event for container widget"""

        try:
            r = random.randint(0,100)
            painter = QPainter(self)
            painter.scale(self.context.scale, self.context.scale)
            painter.setPen(Qt.GlobalColor.black)
            brush = QBrush(Qt.GlobalColor.blue)

            for i in self.time_boxes:
                i.paint(painter, brush)

            self.grid.paint(painter, brush)

            for i in self.linked_vertical_scrollbars:
                i.setValue(self.parent.verticalScrollBar().value())

            res = painter.end()
        except:
            print("weird exception 5")

    @pyqtSlot()
    def resize_canvas(self):

        """resize canvas according to scale"""

        scale = self.context.scale
        width = self.context.left_offset + self.context.time_column_width
        height = self.grid_height + self.context.top_offset + self.context.scroll_bar_offset
        self.setFixedSize(int(width*scale), int(height*scale))

        self.parent.setFixedWidth(int(width*scale))
