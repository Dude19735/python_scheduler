"""
Module provides head bar for calendars that contains the dates of the
displayed days
"""

from datetime import timedelta, datetime
from PyQt6.QtCore import Qt, QRect, pyqtSlot
from PyQt6.QtWidgets import QWidget
from PyQt6.QtGui import QPainter, QBrush

class HeadBarRect(QRect):

    """
    Class represents head bar for calendar
    """

    def __init__(self, x_coord, y_coord, width, height, context):
        super().__init__(x_coord, y_coord, width, height)
        self.context = context
        self.context.date_list = list()
        self.day_names = list()

        current_day = datetime.today().date()
        self.current_day_index = 0

        for i in range(0, self.context.day_count):
            c_date = self.context.start_date + timedelta(days=i)
            if c_date == current_day:
                self.current_day_index = i
            self.day_names.append((c_date.strftime("%a"), c_date.weekday()))
            self.context.date_list.append(c_date.strftime("%d.%m.%Y"))

    def paint(self, painter, brush):

        """paints the head bar"""

        painter.setPen(Qt.GlobalColor.black)
        brush.setColor(self.context.canvas_background_color)
        painter.fillRect(self, brush)

        height = self.context.head_bar_height
        width = self.context.box_width
        x_coord = self.context.time_column_width + self.context.left_offset
        y_coord = 0

        b_width = self.context.box_border_width
        date_list = self.context.date_list
        day_names = self.day_names
        len_list = len(date_list)

        current_day_index = self.current_day_index
        for i in range(0, len_list):
            rect = QRect(x_coord + b_width, y_coord + b_width,\
                width - 2*b_width, height - 2*b_width)

            if i == current_day_index:
                brush.setColor(self.context.head_bar_color_currend_day)
            elif day_names[i][1] != 6:
                brush.setColor(self.context.head_bar_color)
            else:
                brush.setColor(self.context.head_bar_color_sunday)

            painter.fillRect(rect, brush)
            painter.drawText(rect, Qt.AlignmentFlag.AlignCenter, day_names[i][0] + " / " + date_list[i])
            x_coord = x_coord + width

class HeadBar(QWidget):

    """
    Class represents head bar with dates listed on it
    """

    def __init__(self, communicator, context, parent):
        super().__init__()
        self.communicator = communicator
        self.context = context
        self.parent = parent

        self.resize_canvas()
        self.communicator.SIGNAL_ENTRY_RESIZED.connect(self.resize_canvas)
        self.communicator.SIGNAL_SCHEDULE_RESIZED.connect(self.resize_canvas)
        self.communicator.SIGNAL_DATES_CHANGED.connect(self.update_canvas)

        self.head_bar_rect = HeadBarRect(0, 0, self.get_width(), self.height(), self.context)

    def paintEvent(self, event): # pylint: disable=invalid-name, unused-argument

        """paint the whole head bar"""

        painter = QPainter(self)
        painter.scale(self.context.scale, self.context.scale)
        painter.setPen(Qt.GlobalColor.black)
        brush = QBrush(Qt.GlobalColor.blue)

        self.head_bar_rect.paint(painter, brush)

    def get_width(self):

        """return current width of the head bar canvas"""

        return self.context.time_column_width + self.context.left_offset +\
            self.context.day_count*self.context.box_width +\
                2*self.context.scroll_bar_offset

    def get_date_by_index(self, index):

        """get date by date list of the HeadBarRect index"""

        return self.context.date_list[index]

    @pyqtSlot()
    def update_canvas(self):

        """update the whole window with new information from context"""

        self.head_bar_rect = None
        self.head_bar_rect = HeadBarRect(0, 0, self.get_width(), self.height(), self.context)
        self.resize_canvas()
        self.update()

    @pyqtSlot()
    def resize_canvas(self):

        """resize canvas according to scale"""
        scale = self.context.scale
        width = int((self.get_width())*scale)
        height = int(self.context.head_bar_height*scale)
        self.setFixedSize(width, height)

        self.parent.setFixedHeight(height + 2*self.context.box_border_width)
