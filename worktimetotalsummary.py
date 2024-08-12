"""
Module offers a summary over all work times for a selected date range
"""

from PyQt6.QtWidgets import QWidget
from PyQt6.QtGui import QPainter, QBrush, QPalette
from PyQt6.QtCore import Qt, pyqtSlot
import dbobj.dbwrapper as dbwrapper
from helpers.percentbar import PercentBar

class WorkTimeTotalSummary(QWidget):

    """
    Class represents a widget with a work times summary display
    """

    def __init__(self, width, top_height, bottom_height,\
        entry_work_gradient, subject_entry_communicator,\
        communicator, context, parent):

        super().__init__()
        self.communicator = communicator
        self.context = context
        self.parent = parent
        self.entry_work_gradient = entry_work_gradient
        self.subject_entry_communicator = subject_entry_communicator
        self.width = width
        self.top_height = top_height
        self.bottom_height = bottom_height

        self.total = None
        self.subjects = None
        self.total_p_bar = None

        self.communicator.SIGNAL_ENTRY_RESIZED.connect(self.resize_canvas)
        self.communicator.SIGNAL_SCHEDULE_RESIZED.connect(self.resize_canvas)
        self.communicator.SIGNAL_DATES_CHANGED.connect(self.update_canvas)

        self.communicator.SIGNAL_WORK_PLAN_CHANGED.connect(\
            self.update_work_plan)

        self.communicator.SIGNAL_WORK_TIME_CHANGED.connect(\
            self.update_work_time)

        self.communicator.SIGNAL_TOTAL_WORK_CHANGED.connect(\
            self.update_total)

        palette = QPalette()
        palette.setColor(QPalette.ColorRole.Window, self.context.canvas_background_color)
        self.setAutoFillBackground(True)
        self.setPalette(palette)

        self.load_data()
        self.update_canvas()
        self.resize_canvas()

    def paintEvent(self, event): # pylint: disable=invalid-name, unused-argument

        """paint event for this widget"""

        painter = QPainter(self)
        painter.scale(1, self.context.scale)
        painter.setPen(Qt.GlobalColor.black)
        brush = QBrush(Qt.GlobalColor.blue)

        self.total_p_bar.paint(painter, brush, True)

    def load_data(self):

        """load data from db"""

        # load total work times
        self.total = dbwrapper.WorkTotalTimePercentage.get_work_total_time_percentage(\
            self.context.start_date, self.context.end_date, self.context.db_file_name)

        # load per subject work time
        self.subjects = dbwrapper.WorkSubjectTimePercentage.get_work_subject_time_percentage(\
            self.context.start_date, self.context.end_date,\
                self.context.db_file_name)

    # pylint: disable=unused-argument
    @pyqtSlot(float, float)
    def update_work_plan(self, old_value, new_value):

        """
        Slot gets a call from entrycanvas if the user changes one value in the
        entrycanvas
        """

        self.total.work_time = self.total.work_time - old_value
        self.total.work_time = self.total.work_time + new_value

        self.update_canvas_data()
        self.update()

    @pyqtSlot(float)
    def update_work_time(self, time_diff):

        """
        Slot gets a call from entrycanvas if the user changes one value in the
        entrycanvas
        """

        self.total.time_diff = self.total.time_diff + time_diff
        self.total.total_time_diff = self.total.total_time_diff + time_diff

        self.update_canvas_data()
        self.update()

    @pyqtSlot(float, float)
    def update_total(self, old_value, new_value):

        """
        Slot gets a call from entrycanvas if the user changes one value in the
        entrycanvas
        """

        self.total.total_time_diff = self.total.total_time_diff - old_value
        self.total.total_time_diff = self.total.total_time_diff + new_value

        self.update_canvas_data()
        self.update()

    @pyqtSlot()
    def update_canvas(self):

        """update canvas with new data from db"""

        self.total_p_bar = None
        self.load_data()
        self.update_canvas_data()

    def update_canvas_data(self):

        """update canvas with new data"""

        # create plot bar for total
        self.total_p_bar = PercentBar(\
            self.context.left_offset, self.context.top_offset,\
                self.width - 2*self.context.left_offset,\
                    self.top_height + self.bottom_height -\
                        2*self.context.top_offset + self.context.box_border_width,\
                            self.total.work_time, self.total.time_diff,\
                                self.total.work_time, self.total.time_diff,\
                                    self.total.total_time_diff,\
                                        self.entry_work_gradient,\
                                            self.communicator, self.context,\
                                                self.parent)

        self.update()

    @pyqtSlot()
    def resize_canvas(self):

        """resize the canvas according to new scale"""

        self.setFixedSize(\
            self.width, int((self.top_height + self.bottom_height)*self.context.scale))
        self.update()
