"""
Module contains a representation for a date picker with a from and a to
date, ok and cancel buttons
"""

from datetime import date
from PyQt6.QtCore import Qt, pyqtSlot, QDate, QSize, QPoint
from PyQt6.QtGui import QIcon, QFont
from PyQt6.QtWidgets import QWidget, QCalendarWidget, QPushButton, QSpacerItem
from PyQt6.QtWidgets import QHBoxLayout, QVBoxLayout, QLabel, QDialog, QSizePolicy

class DatePickerHead(QWidget):

    """
    Class represents head bar for date picker that should be shown
    at the top of the whole window
    """

    def __init__(self, communicator, context, parent):
        super().__init__()
        self.communicator = communicator
        self.context = context
        self.parent = parent

        # define new font and corresponding font metrics
        new_font = QFont("MS Shell Dlg 2", 12)
        from_str = self.context.start_date.strftime(self.context.date_format)
        to_str = self.context.end_date.strftime(self.context.date_format)
        self.setFont(new_font)
        width = max(self.fontMetrics().horizontalAdvance(from_str), self.fontMetrics().horizontalAdvance(from_str)) + 10
        height = self.context.date_picker_head_height

        self.zoom_label = QLabel(str(round(self.context.scale*100)) + "%")
        self.zoom_label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        self.zoom_label.setFixedWidth(50)
        self.zoom_label.setFont(new_font)
        self.communicator.SIGNAL_SCHEDULE_RESIZED.connect(self.update_scale)
        self.communicator.SIGNAL_ENTRY_RESIZED.connect(self.update_scale)

        button = QPushButton()
        button.setIconSize(QSize(height-2, height-2))
        button.setIcon(QIcon("./img/datepicker.png"))
        button.setFixedSize(height, height)
        button.setStyleSheet("background-color: white")
        button.setFlat(True)
        button.clicked.connect(self.button_clicked)

        self.from_label = QLabel()
        self.from_label.setFixedSize(width, height)
        self.from_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.from_label.setFont(new_font)

        self.to_label = QLabel()
        self.to_label.setFixedSize(width, height)
        self.to_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.to_label.setFont(new_font)

        connect_label = QLabel("to")
        connect_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        connect_label.setFont(new_font)

        self.update_date_display()
        self.communicator.SIGNAL_DATES_CHANGED.connect(self.update_date_display)

        layout = QHBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignLeft)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.addWidget(button)
        layout.addWidget(self.from_label)
        layout.addWidget(connect_label)
        layout.addWidget(self.to_label)
        layout.addItem(QSpacerItem(10, 10, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum))
        layout.addWidget(self.zoom_label)

        self.setLayout(layout)

    @pyqtSlot()
    def update_date_display(self):

        """update the dates shown in the dates labels"""

        from_str = self.context.start_date.strftime(self.context.date_format)
        to_str = self.context.end_date.strftime(self.context.date_format)
        self.from_label.setText(from_str)
        self.to_label.setText(to_str)

    @pyqtSlot()
    def update_scale(self):

        """update label with scale indicator"""

        self.zoom_label.setText(str(round(self.context.scale*100)) + "%")

    @pyqtSlot()
    def button_clicked(self):

        """button clicked event"""

        self.parent.setEnabled(False)
        date_picker = DatePicker(
            self.communicator,\
                self.context,\
                    self)
        date_picker.show()

class DatePicker(QDialog):

    """
    Class represents one date picker with two calendars, one ok
    and one cancel button
    """

    def __init__(self, communicator, context, parent):
        super().__init__(parent=parent)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Dialog)
        self.setStyleSheet("QDialog{border:2px solid black}")

        self.communicator = communicator
        self.context = context
        self.parent = parent
        self.from_date_value = self.context.start_date
        self.to_date_value = self.context.end_date

        self.from_date = QCalendarWidget(font=context.font)
        self.from_date.setSelectedDate(QDate(self.from_date_value.year,\
            self.from_date_value.month,\
                self.from_date_value.day))

        self.to_date = QCalendarWidget(font=context.font)
        self.set_min_to_date(self.from_date_value.year,\
            self.from_date_value.month,\
                self.from_date_value.day)
        self.to_date.setSelectedDate(QDate(self.to_date_value.year,\
            self.to_date_value.month,\
                self.to_date_value.day))

        self.communicator.SIGNAL_MAINWINDOW_MOVED.connect(self.move_slot)

        ok_button = QPushButton("Ok", font=context.font)
        cancel_button = QPushButton("Cancel", font=context.font)

        h_layout = QHBoxLayout()
        g_layout = QHBoxLayout()
        v_layout = QVBoxLayout()

        h_layout.addWidget(self.from_date)
        h_layout.addWidget(self.to_date)

        g_layout.addWidget(QWidget())
        g_layout.addWidget(QWidget())
        g_layout.addWidget(ok_button)
        g_layout.addWidget(cancel_button)

        v_layout.addLayout(h_layout)
        v_layout.addLayout(g_layout)

        ok_button.clicked.connect(self.ok_slot)
        cancel_button.clicked.connect(self.cancel_slot)
        self.from_date.selectionChanged.connect(self.from_date_selection_changed)
        self.to_date.selectionChanged.connect(self.to_date_selection_changed)

        self.from_date.setStyleSheet(self.context.date_picker_style)

        self.to_date.setStyleSheet(self.context.date_picker_style)

        self.setLayout(v_layout)
        self.move_slot()
        self.show()

    def set_min_to_date(self, year, month, day):

        """
        set the minimum selectable date for the to_date picker to
        current from_date - 1 day
        """

        self.to_date.setMinimumDate(QDate(year, month, day))

    def closeEvent(self, event): # pylint: disable=invalid-name, unused-argument

        """handle user presses X event"""

        self.cancel_slot()

    @pyqtSlot()
    def move_slot(self):

        """user moved the main window, the datepicker has to follow"""

        geo = self.parent.rect()
        pos = self.parent.mapToGlobal(QPoint(geo.x(), geo.y() + geo.height()))
        self.move(pos.x(), pos.y())

    @pyqtSlot()
    def from_date_selection_changed(self):

        """user clicked different date in from_date picker"""

        from_date_value = self.from_date.selectedDate()
        year = from_date_value.year()
        month = from_date_value.month()
        day = from_date_value.day()
        self.from_date_value = date(year, month, day)

        if self.to_date.selectedDate() < from_date_value:
            self.to_date.setSelectedDate(QDate(year, month, day))

        self.set_min_to_date(year, month, day)

    @pyqtSlot()
    def to_date_selection_changed(self):

        """user clicked different date in to_date picker"""

        to_date_value = self.to_date.selectedDate()
        self.to_date_value = date(to_date_value.year(),\
            to_date_value.month(),\
                to_date_value.day())

    @pyqtSlot()
    def ok_slot(self):

        """ok pushbutton slot"""

        self.context.start_date = self.from_date_value
        self.context.end_date = self.to_date_value
        self.context.day_count = (self.to_date_value - self.from_date_value).days + 1
        self.communicator.SIGNAL_DATES_CHANGED.emit()
        self.close()
        self.parent.parent.setEnabled(True)

    @pyqtSlot()
    def cancel_slot(self):

        """
        cancel pushbutton slot
        also called when user presses X
        basically does nothing
        """

        self.close()
        self.parent.parent.setEnabled(True)
