"""
Module contains class with a lot of signals that can be used for
intercomponent communication
"""

from PyQt6.QtWidgets import QWidget
from PyQt6.QtCore import QObject, pyqtSignal, QDate

class Communicator(QObject):

    """
    Class represents an interface for communication between
    the different GUI parts
    """

    SIGNAL_ENTRY_RESIZED = pyqtSignal()
    SIGNAL_SCHEDULE_RESIZED = pyqtSignal()
    SIGNAL_PARENT_RESIZED = pyqtSignal()

    SIGNAL_ENTRY_SCROLLED = pyqtSignal()
    SIGNAL_SCHEDULE_SCROLLED = pyqtSignal()

    SIGNAL_DATES_CHANGED = pyqtSignal()
    SIGNAL_MAINWINDOW_MOVED = pyqtSignal()
    SIGNAL_TIMER_MOVED = pyqtSignal()

    SIGNAL_REMOVE_SELECT_PLACEHOLDER = pyqtSignal()

    SIGNAL_REDRAW_SCHEDULE_CANVAS = pyqtSignal()
    SIGNAL_REDRAW_ENTRY_CANVAS = pyqtSignal()
    SIGNAL_REDRAW_FOOT_BAR = pyqtSignal()

    SIGNAL_CURRENT_WORKDAY_CHANGED = pyqtSignal()

    SIGNAL_CURRENT_ROUND_UP = pyqtSignal()
    SIGNAL_CURRENT_SIGNAL_BELL_RINGED = pyqtSignal()

    SIGNAL_ITEMLIST_CLEAN = pyqtSignal()
    SIGNAL_LISTITEM_ADDED = pyqtSignal(str, QDate)
    SIGNAL_LISTITEM_UPDATE = pyqtSignal(int)
    SIGNAL_ITEMLIST_REFRESH_POSITION = pyqtSignal()

    SIGNAL_TIMER_ENABLE_DATE_BUTTON = pyqtSignal()

    SIGNAL_SUBJECT_ENTRY_COMM_UPDATED = pyqtSignal()

    SIGNAL_SCHEDULE_TOTAL_WORK_CHANGED = pyqtSignal(int, int, float)
    SIGNAL_SCHEDULE_ENTRY_WORK_CHANGED = pyqtSignal(int, int, float)

    SIGNAL_ENTRY_WORK_PLAN_CHANGED = pyqtSignal(int, float, float)
    SIGNAL_ENTRY_WORK_TIME_CHANGED = pyqtSignal(int, float)
    SIGNAL_ENTRY_TOTAL_WORK_CHANGED = pyqtSignal(int, float)

    SIGNAL_DAY_WORK_PLAN_CHANGED = pyqtSignal(int, float, float)
    SIGNAL_DAY_WORK_TIME_CHANGED = pyqtSignal(int, float)
    SIGNAL_DAY_TOTAL_WORK_CHANGED = pyqtSignal(int, float)

    SIGNAL_SUBJECT_WORK_PLAN_CHANGED = pyqtSignal(int, float, float)
    SIGNAL_SUBJECT_WORK_TIME_CHANGED = pyqtSignal(int, float)
    SIGNAL_SUBJECT_TOTAL_WORK_CHANGED = pyqtSignal(int, float, float)

    SIGNAL_WORK_PLAN_CHANGED = pyqtSignal(float, float)
    SIGNAL_WORK_TIME_CHANGED = pyqtSignal(float)
    SIGNAL_TOTAL_WORK_CHANGED = pyqtSignal(float, float)

    SIGNAL_SCROLLBAR_CHANGE_REQUIRED = pyqtSignal(int, QWidget)
