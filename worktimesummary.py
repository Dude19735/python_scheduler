"""
Module offers a summary over all work times for a selected date range
"""

from PyQt6.QtWidgets import QWidget
from PyQt6.QtGui import QPainter, QBrush, QPalette
from PyQt6.QtCore import Qt, pyqtSlot
import dbobj.dbwrapper as dbwrapper
from helpers.percentbar import PercentBar

class WorkTimeSummary(QWidget):

    """
    Class represents a widget with a work times summary display
    """

    def __init__(self, width, entry_work_gradient, subject_entry_communicator,\
        communicator, context, parent):

        super().__init__()
        self.communicator = communicator
        self.context = context
        self.parent = parent
        self.entry_work_gradient = entry_work_gradient
        self.subject_entry_communicator = subject_entry_communicator
        self.linked_scroll_bars = list()
        self.width = width
        self.height =\
            subject_entry_communicator.grid_height +\
                self.context.scroll_bar_offset +\
                    self.context.top_offset

        self.total = None
        self.subjects = None
        self.subject_p_bars = dict()
        self.subject_render_list = list()

        self.communicator.SIGNAL_ENTRY_RESIZED.connect(self.resize_canvas)
        self.communicator.SIGNAL_SCHEDULE_RESIZED.connect(self.resize_canvas)
        self.communicator.SIGNAL_DATES_CHANGED.connect(self.update_canvas)

        self.communicator.SIGNAL_SUBJECT_WORK_PLAN_CHANGED.connect(\
            self.update_subject_work_plan)

        self.communicator.SIGNAL_SUBJECT_WORK_TIME_CHANGED.connect(\
            self.update_subject_work_time)

        self.communicator.SIGNAL_SUBJECT_TOTAL_WORK_CHANGED.connect(\
            self.update_subject_total)

        palette = QPalette()
        palette.setColor(QPalette.ColorRole.Window, self.context.canvas_background_color)
        self.setAutoFillBackground(True)
        self.setPalette(palette)

        self.load_data()
        self.update_canvas_data()
        self.resize_canvas()

    def link_vertical_scroll_bar(self, scroll_bar):

        """link vertical scroll bar to own vertical scroll bar"""

        self.linked_scroll_bars.append(scroll_bar)

    def paintEvent(self, event): # pylint: disable=invalid-name, unused-argument

        """paint event for this widget"""

        painter = QPainter(self)
        painter.scale(1, self.context.scale)
        painter.setPen(Qt.GlobalColor.black)
        brush = QBrush(Qt.GlobalColor.blue)

        for i in self.subject_render_list:
            i.paint(painter, brush)

        for i in self.linked_scroll_bars:
            i.setValue(self.parent.verticalScrollBar().value())

    def load_data(self):

        """load data from db"""

        # load total work times
        self.total = dbwrapper.WorkTotalTimePercentage.get_work_total_time_percentage(\
            self.context.start_date, self.context.end_date, self.context.db_file_name)

        # load per subject work time
        self.subjects = dbwrapper.WorkSubjectTimePercentage.get_work_subject_time_percentage(\
            self.context.start_date, self.context.end_date,\
                self.context.db_file_name)

    @pyqtSlot(int, float, float)
    def update_subject_work_plan(self, subject_id, old_value, new_value):

        """
        Slot gets a call from entrycanvas if the user changes one value in the
        entrycanvas
        """

        sub = self.subjects[subject_id]
        sub.work_time = sub.work_time - old_value
        sub.work_time = sub.work_time + new_value
        self.total.work_time = self.total.work_time - old_value
        self.total.work_time = self.total.work_time + new_value

        self.communicator.SIGNAL_WORK_PLAN_CHANGED.emit(old_value, new_value)

        self.update_canvas_data()
        self.update()

    @pyqtSlot(int, float)
    def update_subject_work_time(self, subject_id, time_diff):

        """
        Slot gets a call from entrycanvas if the user changes one value in the
        entrycanvas
        """

        sub = self.subjects[subject_id]
        sub.time_diff = sub.time_diff + time_diff
        sub.total_time_diff = sub.total_time_diff + time_diff
        self.total.total_time_diff = self.total.total_time_diff + time_diff

        self.communicator.SIGNAL_WORK_TIME_CHANGED.emit(time_diff)

        self.update_canvas_data()
        self.update()

    @pyqtSlot(int, float, float)
    def update_subject_total(self, subject_id, old_value, new_value):

        """
        Slot gets a call from entrycanvas if the user changes one value in the
        entrycanvas
        """

        sub = self.subjects[subject_id]
        sub.total_time_diff = sub.total_time_diff - old_value
        sub.total_time_diff = sub.total_time_diff + new_value
        self.total.work_time = self.total.work_time - old_value
        self.total.work_time = self.total.work_time + new_value

        self.communicator.SIGNAL_TOTAL_WORK_CHANGED.emit(old_value, new_value)

        self.update_canvas_data()
        self.update()

    @pyqtSlot()
    def update_canvas(self):

        """update canvas with new data from db"""

        self.subject_p_bars.clear()
        self.subject_render_list.clear()
        self.load_data()
        self.update_canvas_data()
        self.resize_canvas()

    def update_canvas_data(self):

        """update canvas with new data"""

        # create plot bars for subjects
        x_coord = self.context.left_offset
        y_coord = self.context.top_offset
        for i in self.subject_entry_communicator.subject_boxes:
            work_time = 0
            time_diff = 0
            total = 0
            if i.subject.subject_id in self.subjects.keys():
                subject = self.subjects[i.subject.subject_id]
                work_time = subject.work_time
                time_diff = subject.time_diff
                total = subject.total_time_diff
            sub =\
                PercentBar(\
                    x_coord, y_coord, self.width - 2*self.context.left_offset,\
                        i.get_height(),\
                            self.total.work_time, self.total.time_diff,\
                                work_time, time_diff, total,\
                                    self.entry_work_gradient,\
                                        self.communicator, self.context,\
                                            self.parent)
            self.subject_p_bars[i.subject.subject_id] = sub
            self.subject_render_list.append(sub)
            y_coord = y_coord + i.get_height()

        self.update()

    @pyqtSlot()
    def resize_canvas(self):

        """resize the canvas according to new scale"""

        self.height =\
            self.subject_entry_communicator.grid_height +\
                self.context.scroll_bar_offset +\
                    self.context.top_offset
        self.setFixedSize(self.width, int(self.height*self.context.scale))
        self.parent.setFixedWidth(self.width)
        self.update()
