"""
Module provides foot bar for calendars that contains the summary of the
planed and worked time
"""

from datetime import timedelta
from PyQt6.QtCore import Qt, QRect, pyqtSlot
from PyQt6.QtWidgets import QWidget
from PyQt6.QtGui import QPainter, QBrush, QPalette

from dbobj.workdaytimepercentage import WorkDayTimePercentage

class FootBarRect(QRect):

    """
    Class represents head bar for calendar
    """

    def __init__(self, x_coord, y_coord, width, height,\
        day_summaries, entry_work_gradient, communicator, context):

        super().__init__(x_coord, y_coord, width, height)
        self.context = context
        self.day_summaries = day_summaries
        self.entry_work_gradient = entry_work_gradient
        self.communicator = communicator

    def paint(self, painter, brush):

        """paints the head bar"""

        painter.setPen(Qt.GlobalColor.black)
        brush.setColor(self.context.head_bar_color)

        height = self.context.head_bar_height
        width = self.context.box_width
        x_coord = self.context.time_column_width + self.context.left_offset
        y_coord = 0

        b_width = self.context.box_border_width
        len_list = len(self.day_summaries)

        normal_font = painter.font()
        total_font = painter.font()
        total_font.setBold(True)
        for i in range(0, len_list):
            rect1 = QRect(x_coord, y_coord + b_width,\
                width - b_width, height - 2*b_width)

            rect2 = QRect(x_coord + int(width/3), y_coord + b_width,\
                width - b_width - int(width/3) - self.context.box_text_margin,\
                    height - 2*b_width)

            rect3 = QRect(x_coord + self.context.box_text_margin, y_coord + b_width,\
                width - b_width - int(2*width/3) - self.context.box_text_margin,\
                    height - 2*b_width)

            day_s = self.day_summaries[i]
            if day_s.time_diff != 0:
                brush.setColor(self.entry_work_gradient.gradient(day_s.work_percent))
            else:
                brush.setColor(self.context.head_bar_color)

            painter.fillRect(rect1, brush)
            if day_s.work_time != 0 or day_s.time_diff != 0:
                painter.setFont(normal_font)
                painter.drawText(\
                    rect2,\
                        Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter,\
                            str(round(day_s.time_diff, 2)) + " / " + str(day_s.work_time))

            if day_s.total_time_diff != 0:
                painter.setFont(total_font)
                painter.drawText(\
                    rect3,\
                        Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter,\
                            str(round(day_s.total_time_diff, 2)))
            x_coord = x_coord + width

class FootBarTotal(QRect):

    """
    Class represents the furthermost left cell containing the total
    work time for the loaded interval
    """

    def __init__(self, x_coord, y_coord, width, height, total_work_time,\
        communicator, context):

        l_offset = context.left_offset
        b_width = context.box_border_width
        super().__init__(\
            x_coord + l_offset + b_width, y_coord + b_width,\
                width - 2*b_width, height - 2*b_width)

        self.total_work_time = total_work_time
        self.context = context
        self.communicator = communicator

        b_width = self.context.box_border_width
        self.text_rect = QRect(\
            x_coord + b_width + l_offset + self.context.box_text_margin,\
                y_coord + b_width,\
                    width - 2*b_width - self.context.box_text_margin,\
                        height - 2*b_width)

    def paint(self, painter, brush):

        """painter method for this rect"""

        brush.setColor(self.context.head_bar_color)
        painter.fillRect(self, brush)
        font = painter.font()
        font.setBold(True)
        painter.setFont(font)
        painter.drawText(\
            self.text_rect, Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter, str(round(self.total_work_time, 2)))

class FootBar(QWidget):

    """
    Class represents head bar with dates listed on it
    """

    def __init__(self, entry_work_gradient, communicator, context, parent):
        super().__init__()
        self.communicator = communicator
        self.context = context
        self.parent = parent
        self.entry_work_gradient = entry_work_gradient
        self.day_summaries = list()
        self.work_percent = 0
        self.total_work_time = 0
        self.foot_bar_rect = None
        self.foot_bar_total = None

        palette = QPalette()
        palette.setColor(QPalette.ColorRole.Window, self.context.canvas_background_color)
        self.setAutoFillBackground(True)
        self.setPalette(palette)

        self.resize_canvas()
        self.communicator.SIGNAL_ENTRY_RESIZED.connect(self.resize_canvas)
        self.communicator.SIGNAL_SCHEDULE_RESIZED.connect(self.resize_canvas)
        self.communicator.SIGNAL_DATES_CHANGED.connect(self.update_canvas)
        self.communicator.SIGNAL_REDRAW_FOOT_BAR.connect(self.update_canvas)

        self.communicator.SIGNAL_ENTRY_WORK_PLAN_CHANGED.connect(self.update_day_summary)
        self.communicator.SIGNAL_ENTRY_TOTAL_WORK_CHANGED.connect(self.update_day_total)
        self.communicator.SIGNAL_ENTRY_WORK_TIME_CHANGED.connect(self.update_day_work_time)

        self.update_canvas()

    @pyqtSlot(int, float, float)
    def update_day_summary(self, date_index, old_value, new_value):

        """
        slot gets a call from entrycanvas if the user changes
        one value in the entry canvas
        gets some real time change in the gradient colors
        """

        entry = self.day_summaries[date_index]
        entry.work_time = entry.work_time - old_value
        entry.work_time = entry.work_time + new_value

        if entry.work_time == 0:
            entry.work_percent = 100
        else:
            entry.work_percent = min(100.0, 100.0 / entry.work_time * entry.time_diff)

        self.update()

    @pyqtSlot(int, float)
    def update_day_total(self, date_index, time_diff):

        """
        Gets a call from entry canvas if the user books something in
        the schedule and a canvas entry gets modified as a result
        """

        entry = self.day_summaries[date_index]
        entry.total_time_diff = entry.total_time_diff + time_diff
        self.total_work_time = self.total_work_time + time_diff
        self.foot_bar_total.total_work_time = self.total_work_time

        self.update()

    @pyqtSlot(int, float)
    def update_day_work_time(self, date_index, time_diff):

        """
        Gets a call from entry canvas if the user books something in
        the schedule and a canvas entry gets modified as a result
        """

        entry = self.day_summaries[date_index]
        entry.total_time_diff = entry.total_time_diff + time_diff
        entry.time_diff = entry.time_diff + time_diff
        self.total_work_time = self.total_work_time + time_diff
        self.work_percent = self.total_work_time + time_diff
        self.foot_bar_total.total_work_time = self.total_work_time

        if entry.work_time == 0:
            entry.work_percent = 100
        else:
            entry.work_percent = min(100.0, 100.0 / entry.work_time * entry.time_diff)

        self.update()

    def sum_total_work_time(self):

        """sum up the total work time diff for all day_summaries"""

        total = 0
        for i in self.day_summaries:
            total = total + i.total_time_diff

        self.total_work_time = total

    def paintEvent(self, event): # pylint: disable=invalid-name, unused-argument

        """paint the whole head bar"""

        painter = QPainter(self)
        painter.scale(self.context.scale, self.context.scale)
        painter.setPen(Qt.GlobalColor.black)
        brush = QBrush(Qt.GlobalColor.blue)

        self.foot_bar_rect.paint(painter, brush)
        self.foot_bar_total.paint(painter, brush)

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

        WorkDayTimePercentage.get_work_day_time_percentage(\
            self.context.work_day_summaries,\
                self.context.start_date,\
                    self.context.end_date,\
                        self.context.db_file_name)

        self.day_summaries.clear()
        day_count = self.context.day_count
        start_date = self.context.start_date
        for i in range(0, day_count):
            if i in self.context.work_day_summaries.keys():
                self.day_summaries.append(self.context.work_day_summaries[i])
            else:
                self.day_summaries.append(\
                    WorkDayTimePercentage.new(\
                        start_date,\
                            start_date + timedelta(hours=24*i),\
                                0, 0, 0, 0))

        self.sum_total_work_time()

        self.foot_bar_rect = None
        self.foot_bar_rect = FootBarRect(\
            0, 0, self.get_width(), self.height(),\
                self.day_summaries,\
                    self.entry_work_gradient,\
                        self.communicator, self.context)

        self.foot_bar_total = None
        self.foot_bar_total = FootBarTotal(\
            0, 0, self.context.time_column_width,\
                self.height(),\
                    self.total_work_time,\
                        self.communicator, self.context)

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
