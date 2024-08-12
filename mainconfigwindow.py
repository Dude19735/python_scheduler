"""
Module contains definition of main window
"""

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QWidget, QScrollBar, QHBoxLayout, QFrame
from PyQt6.QtWidgets import QScrollArea, QVBoxLayout, QSplitter
from PyQt6.QtGui import QWheelEvent

from itemlist.itemlist import ItemList
from worktimesummary import WorkTimeSummary
from worktimetotalsummary import WorkTimeTotalSummary
import timescanvas
import subjectcanvas
import schedulecanvas
import entrycanvas
import datepicker
import headbar
import footbar
import horizontalscrollbar
from helpers.subjectentrycommunicator import SubjectEntryCommunicator
from helpers.verticalspacer import VerticalSpacer
from helpers.entryworkgradient import EntryWorkGradient
import random

class ScrollArea(QScrollArea):

    """
    Scrollbar area overwrite to catch scroll events and disable them if necessary
    """

    def __init__(self, context):
        super().__init__()
        self.context = context

    def eventFilter(self, obj, event): # pylint: disable=invalid-name

        """filter out the scroll event if ctrl is pressed"""
        # if ctrl is pressed, ignore scroll events, else don't
        if self.context.keys_pressed["ctrl"] and isinstance(obj, QScrollBar) and isinstance(event, QWheelEvent):
            return True
        else:
            return super().eventFilter(obj, event)

class MainConfigWindow(QWidget):

    """
    Class represents the main widget
    """

    def __init__(self, context, communicator):
        super().__init__()
        self.context = context
        self.communicator = communicator
        self.entry_work_gradient = EntryWorkGradient(context)

        # self.setMinimumSize(self.context.width, self.context.height)

        head_bar_scroll_area = ScrollArea(self.context)
        head_bar = headbar.HeadBar(self.communicator, self.context, head_bar_scroll_area)
        head_bar_scroll_area.setWidget(head_bar)
        head_bar_scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        # schedule scroll area
        schedule_layout = QHBoxLayout()
        schedule_layout.setContentsMargins(0, 0, 0, 0)
        schedule_layout.setSpacing(0)

        schedule_time_scroll_area = ScrollArea(self.context)
        schedule_time_boxes = timescanvas.TimesCanvas(\
            self.communicator,\
                self.context,\
                    schedule_time_scroll_area)

        schedule_time_scroll_area.setWidget(schedule_time_boxes)
        schedule_time_scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        schedule_time_scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        schedule_time_scroll_area.setFrameShape(QFrame.Shape.NoFrame)

        schedule_scroll_area = ScrollArea(self.context)
        schedule_canvas = schedulecanvas.ScheduleCanvas(\
            schedule_time_boxes.get_interval_count(),\
                self.communicator,\
                    self.context,\
                        schedule_scroll_area)

        schedule_scroll_area.setWidget(schedule_canvas)
        schedule_scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        schedule_scroll_area.setFrameShape(QFrame.Shape.NoFrame)
        schedule_canvas.link_vertical_scroll_bar(schedule_time_scroll_area.verticalScrollBar())
        schedule_time_boxes.link_vertical_scroll_bar(schedule_scroll_area.verticalScrollBar())

        schedule_layout.addWidget(schedule_time_scroll_area)
        schedule_layout.addWidget(schedule_scroll_area)

        # entry scroll area
        entry_layout = QHBoxLayout()
        entry_layout.setContentsMargins(0, 0, 0, 0)
        entry_layout.setSpacing(0)

        # communicator for subject and entry canvas
        subject_entry_comm = SubjectEntryCommunicator()

        subject_scroll_area = ScrollArea(self.context)
        subject_canvas = subjectcanvas.SubjectCanvas(\
            subject_entry_comm,\
                self.communicator,\
                    self.context,\
                        subject_scroll_area)

        subject_scroll_area.setWidget(subject_canvas)
        subject_scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        subject_scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        subject_scroll_area.setFrameShape(QFrame.Shape.NoFrame)

        # work time summary widget
        work_time_scroll_area = ScrollArea(self.context)
        work_time_summary = WorkTimeSummary(\
             300 + self.context.scroll_bar_offset,\
                self.entry_work_gradient,\
                    subject_entry_comm,\
                        self.communicator,\
                            self.context,\
                                work_time_scroll_area)
        work_time_scroll_area.setWidget(work_time_summary)
        work_time_scroll_area.setWidgetResizable(True)
        work_time_scroll_area.setFrameShape(QFrame.Shape.NoFrame)
        work_time_scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        work_time_scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        entry_scroll_area = ScrollArea(self.context)
        entry_canvas = entrycanvas.EntryCanvas(
            self.entry_work_gradient,\
                subject_entry_comm,\
                    self.communicator,\
                        self.context,\
                            entry_scroll_area)

        entry_scroll_area.setWidget(entry_canvas)
        entry_scroll_area.setFrameShape(QFrame.Shape.NoFrame)
        entry_scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        entry_scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)

        entry_canvas.link_vertical_scroll_bar(subject_scroll_area.verticalScrollBar())
        subject_canvas.link_vertical_scroll_bar(entry_scroll_area.verticalScrollBar())
        work_time_summary.link_vertical_scroll_bar(entry_scroll_area.verticalScrollBar())
        entry_canvas.link_vertical_scroll_bar(work_time_scroll_area.verticalScrollBar())
        work_time_summary.link_vertical_scroll_bar(subject_scroll_area.verticalScrollBar())
        subject_canvas.link_vertical_scroll_bar(work_time_scroll_area.verticalScrollBar())


        entry_layout.addWidget(subject_scroll_area)
        entry_layout.addWidget(entry_scroll_area)

        # item list
        todo_list = ItemList(300, 31, self.communicator, self.context, self)

        # layout containing todo-widget, headbar and schedule canvas
        top_layout = QHBoxLayout()
        top_layout.setContentsMargins(0, 0, 0, 0)
        top_layout.setSpacing(2)
        top_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)
        top_layout.addWidget(todo_list)

        top_sublayout = QVBoxLayout()
        top_sublayout.setContentsMargins(0, 0, 0, 0)
        top_sublayout.setSpacing(2)

        # top separating line between schedule and entry canvas
        top_spacer = VerticalSpacer(None, 1)
        top_spacer.setStyleSheet("background-color: rgb(" + self.context.base_spacer_color + ")")
        top_v_spacer = VerticalSpacer(1, None)
        top_v_spacer.setStyleSheet(\
            "background-color: rgb(" + self.context.base_spacer_color + ")")

        top_layout.addWidget(top_v_spacer)

        # stick together schedule and datepicker
        top_sublayout.addWidget(datepicker.DatePickerHead(self.communicator, self.context, self))
        top_sublayout.addWidget(head_bar_scroll_area)
        top_sublayout.addLayout(schedule_layout)
        top_sublayout.addWidget(top_spacer)

        top_layout.addLayout(top_sublayout)
        top_widget = QWidget()
        top_widget.setLayout(top_layout)

        # bottom separating line between schedule and entry canvas
        bottom_spacer = VerticalSpacer(None, 1)
        bottom_spacer.setStyleSheet("background-color: rgb(" + self.context.base_spacer_color + ")")
        bottom_v_spacer = VerticalSpacer(1, None)
        bottom_v_spacer.setStyleSheet(\
            "background-color: rgb(" + self.context.base_spacer_color + ")")

        # day summary widget for every day
        foot_bar_scroll_area = ScrollArea(self.context)
        foot_bar = footbar.FootBar(\
            self.entry_work_gradient, self.communicator, self.context, foot_bar_scroll_area)
        foot_bar_scroll_area.setWidget(foot_bar)
        foot_bar_scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        foot_bar_scroll_area.setFrameShape(QFrame.Shape.NoFrame)

        # horizontal scrollbar for all widgets
        scroll_bar_area = ScrollArea(self.context)
        scroll_bar = horizontalscrollbar.HorizontalScrollBar(
            self.communicator,\
                self.context,\
                    scroll_bar_area)
        scroll_bar_area.setWidget(scroll_bar)
        scroll_bar_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll_bar.link_scroll_bar(schedule_scroll_area.horizontalScrollBar())
        scroll_bar.link_scroll_bar(head_bar_scroll_area.horizontalScrollBar())
        scroll_bar.link_scroll_bar(entry_scroll_area.horizontalScrollBar())
        scroll_bar.link_scroll_bar(foot_bar_scroll_area.horizontalScrollBar())

        # total time summary widget
        total_time_summary = WorkTimeTotalSummary(\
            300 + self.context.scroll_bar_offset,\
                foot_bar_scroll_area.height(),\
                    scroll_bar_area.height(),\
                        self.entry_work_gradient,\
                            subject_entry_comm,\
                                self.communicator,\
                                    self.context,\
                                        work_time_scroll_area)

        # stick together the entry canvas part
        bottom_sublayout = QVBoxLayout()
        bottom_sublayout.setContentsMargins(0, 0, 0, 0)
        bottom_sublayout.setSpacing(0)
        bottom_sublayout.addWidget(bottom_spacer)
        bottom_sublayout.addLayout(entry_layout)
        bottom_sublayout.addWidget(foot_bar_scroll_area)
        bottom_sublayout.addWidget(scroll_bar_area)

        work_time_spacer = VerticalSpacer(None, 1)
        work_time_spacer.setStyleSheet(\
            "background-color: rgb(" + self.context.base_spacer_color + ")")

        bottom_sublayout_left = QVBoxLayout()
        bottom_sublayout_left.setContentsMargins(0, 0, 0, 0)
        bottom_sublayout_left.setSpacing(0)
        bottom_sublayout_left.addWidget(work_time_spacer)
        bottom_sublayout_left.addWidget(work_time_scroll_area)
        bottom_sublayout_left.addWidget(total_time_summary)

        bottom_layout = QHBoxLayout()
        bottom_layout.setContentsMargins(0, 0, 0, 0)
        bottom_layout.setSpacing(2)
        bottom_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)
        bottom_layout.addLayout(bottom_sublayout_left)
        bottom_layout.addWidget(bottom_v_spacer)
        bottom_layout.addLayout(bottom_sublayout)

        bottom_widget = QWidget()
        bottom_widget.setLayout(bottom_layout)

        splitter = QSplitter(self)
        splitter.setOrientation(Qt.Orientation.Vertical)
        splitter.addWidget(top_widget)
        splitter.addWidget(bottom_widget)

        layout = QVBoxLayout()
        layout.addWidget(splitter)

        self.setLayout(layout)

    def moveEvent(self, event): # pylint: disable=invalid-name, unused-argument

        """event handler for when the window has been moved by a user"""

        self.communicator.SIGNAL_MAINWINDOW_MOVED.emit()
