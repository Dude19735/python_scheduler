# pylint: disable=too-many-lines

"""
Module represents the timer window
"""

import math
from datetime import datetime, date
from PyQt6.QtWidgets import QLabel, QWidget, QDialog
from PyQt6.QtWidgets import QHBoxLayout, QVBoxLayout, QPushButton
from PyQt6.QtWidgets import QProgressBar, QComboBox, QCalendarWidget
from PyQt6.QtGui import QIcon, QPainter
# from PyQt6.QtMultimedia import QSound

# from playsound import playsound

from PyQt6.QtCore import QSize, Qt, QTimer, QDate
from PyQt6.QtCore import QPoint, pyqtSlot
from PyQt6.QtGui import QFont
import dbobj.dbwrapper as dbwrapper
import mainconfigwindow
import random
from helpers.verticalspacer import VerticalSpacer

class VerticalLabel(QPushButton):

    """
    Class represents label with vertical text in it
    """

    def __init__(self, text, size_x, size_y, h_trans, v_trans, context):
        super().__init__()
        self.context = context
        self.text = text
        self.size_x = size_x
        self.size_y = size_y
        self.h_trans = h_trans
        self.v_trans = v_trans
        self.setMinimumSize(size_x, size_y)
        self.setFont(context.font)
        self.setStyleSheet("background-color: #F0F0F0; border: 0px; min-height: " + str(size_y) + "px;")

    def paintEvent(self, event): # pylint: disable=invalid-name, unused-argument

        """paint event for the vertical label"""

        try:
            r = random.randint(0,100)
            super().paintEvent(event)
            painter = QPainter(self)
            painter.setPen(Qt.GlobalColor.black)
            painter.translate(self.size_x*self.h_trans, self.size_y*self.v_trans)
            painter.rotate(-90)
            painter.drawText(0, 0, self.text)
            res = painter.end()
        except:
            print("weird exception 4")

    def set_active(self):

        """paint button with active color"""

        self.setStyleSheet("background-color: rgb(" +\
            self.context.active_indicator_button_color +\
                "); border: 0px; min-height: " + str(self.size_y) + "px;")

    def set_inactive(self):

        """paint button with inactive color"""

        self.setStyleSheet("background-color: rgb(" +\
            self.context.inactive_indicator_button_color +\
                "); border: 0px; min-height: " + str(self.size_y) + "px;")

class DatePicker(QDialog):

    """class represents a date calendar to pick date of data collection"""

    def __init__(self, communicator, context, parent):
        super().__init__(parent=parent)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Dialog)
        self.setStyleSheet("QDialog{border:2px solid black}")

        self.context = context
        self.communicator = communicator
        self.parent = parent
        self.calendar = QCalendarWidget(parent=parent)
        today = datetime.today().date()
        self.calendar.setSelectedDate(QDate(today.year, today.month, today.day))
        self.calendar.setStyleSheet(self.context.date_picker_style)

        ok_button = QPushButton("Ok", parent=parent)
        cancel_button = QPushButton("Cancel", parent=parent)

        ok_button.clicked.connect(self.ok_button)
        cancel_button.clicked.connect(self.cancel_button)

        button_layout = QHBoxLayout()
        button_layout.addWidget(cancel_button)
        button_layout.addWidget(ok_button)

        layout = QVBoxLayout()
        layout.addWidget(self.calendar)
        layout.addLayout(button_layout)

        self.communicator.SIGNAL_TIMER_MOVED.connect(self.move_slot)

        self.setLayout(layout)
        self.move_slot()
        self.show()

    @pyqtSlot()
    def move_slot(self):

        """user moved timer window, make this window follow it"""

        geo = self.parent.rect()
        pos = self.parent.mapToGlobal(QPoint(geo.x(), geo.y() + geo.height()))
        self.move(pos.x(), pos.y())

    @pyqtSlot()
    def ok_button(self):

        """ok button slot"""

        calendar_value = self.calendar.selectedDate()
        self.context.current_work_day = date(\
            calendar_value.year(), calendar_value.month(), calendar_value.day())
        self.communicator.SIGNAL_CURRENT_WORKDAY_CHANGED.emit()
        self.close()
        self.communicator.SIGNAL_TIMER_ENABLE_DATE_BUTTON.emit()

    @pyqtSlot()
    def cancel_button(self):

        """cancel button slot"""

        self.close()
        self.communicator.SIGNAL_TIMER_ENABLE_DATE_BUTTON.emit()

class State():

    """
    Class represents the state of the timer
    """

    def __init__(self, context):
        self.state = 0
        self.context = context

        self.dismiss_button_enable = True
        self.work_button_enable = True
        self.break_button_enable = True
        self.coffee_button_enable = True
        self.stop_button_enable = True
        self.date_button_enable = True
        self.config_button_enable = True
        self.combo_box_enable = True

        self.progress_bar_max_range = self.to_time_step(100, self.context.time_step)

        self.timer_is_running = False
        self.session_time = self.context.work_time_interval
        self.current_session_time = 0
        self.session_time_value = self.to_time_step(\
            self.session_time, self.context.time_step)
        self.current_session_time_value = 0
        self.work_time_interval_value = self.to_time_step(\
            self.context.work_time_interval, self.context.time_step)

        # 0 = init work time
        # 1 = work_time
        # 2 = break_time
        # 3 = coffee_time
        self.work_type = dbwrapper.UnitTypes.INIT_TIME
        self.current_subject_id = 0
        self.current_work_unit_entry = None

    def __del__(self):
        pass

    def to_time_step(self, value, time_step):

        """convert value to time step"""

        return (value)*(1000/time_step)

    def to_seconds(self, value, time_step):

        """convert value to seconds"""

        return value/(1000/time_step)

    def enable_all(self):

        """reset everything except the current_subject_id"""

        self.dismiss_button_enable = True
        self.work_button_enable = True
        self.break_button_enable = True
        self.coffee_button_enable = True
        self.stop_button_enable = True
        self.date_button_enable = True
        self.config_button_enable = True
        self.combo_box_enable = True

    def reset_running_state(self, time_interval):

        """reset running state to pre running state"""

        self.timer_is_running = False
        self.work_type = dbwrapper.UnitTypes.INIT_TIME
        self.current_work_unit_entry = None
        self.session_time = time_interval
        self.current_session_time = 0
        self.session_time_value = self.to_time_step(\
            self.session_time, self.context.time_step)
        self.current_session_time_value = 0
        self.work_time_interval_value = self.to_time_step(\
            time_interval, self.context.time_step)

    def disable_work(self):

        """disable work button, enable break and coffee"""

        self.work_button_enable = False
        self.break_button_enable = True
        self.coffee_button_enable = True

    def disable_break(self):

        """disable break button, enable work and coffee"""

        self.work_button_enable = True
        self.break_button_enable = False
        self.coffee_button_enable = True

    def disable_coffee(self):

        """disable coffee button, enable work and break"""

        self.work_button_enable = True
        self.break_button_enable = True
        self.coffee_button_enable = False

class Timer(QWidget):

    """
    Class represents the timer window with stop/play...
    """

    def get_formated_h_layout(self):

        """get a horizontal layout with spacing and margins set"""

        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        return layout

    def get_formated_v_layout(self):

        """get a vertical layout with spacing and margins set"""

        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        return layout

    def __init__(self, communicator, context):
        super().__init__()
        self.loaded = False

        self.state = State(context)
        self.communicator = communicator
        self.context = context

        self.state.reset_running_state(self.context.work_time_interval)
        self.timer = QTimer()
        self.timer.timeout.connect(self.timer_timeout)

        # dismiss button -----------------
        self.dismiss_button = QPushButton()
        self.dismiss_button.setIcon(QIcon("./img/dismiss.png"))
        self.dismiss_button.setFixedSize(int(self.context.control_button_width/2),\
            int(self.context.control_button_width/2))
        self.dismiss_button.setFlat(True)
        self.dismiss_button.clicked.connect(self.dismiss_button_clicked)

        dismiss_layout = self.get_formated_v_layout()
        dismiss_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        dismiss_layout.addWidget(self.dismiss_button)

        # date and config -----------------
        self.date_button = QPushButton()
        self.date_button.setIcon(QIcon("./img/datepicker.png"))
        self.date_button.setIconSize(QSize(\
            self.context.control_button_icon_width,\
                self.context.control_button_icon_width))
        self.date_button.setFixedSize(\
            self.context.control_button_width,\
                self.context.control_button_width)
        self.date_button.setEnabled(self.state.date_button_enable)
        self.date_button.setFlat(True)
        self.date_button_active = False
        self.date_button.clicked.connect(self.datepicker_button_clicked)
        self.communicator.SIGNAL_TIMER_ENABLE_DATE_BUTTON.connect(\
            self.enable_date_button_slot)

        self.config_button = QPushButton()
        self.config_button.setIcon(QIcon("./img/open_config.png"))
        self.config_button.setIconSize(QSize(\
            self.context.control_button_icon_width,\
                self.context.control_button_icon_width))
        self.config_button.setFixedSize(\
            self.context.control_button_width,\
                self.context.control_button_width)
        self.config_button.setEnabled(self.state.config_button_enable)
        self.config_button.setFlat(True)
        self.config_button.clicked.connect(self.config_button_clicked)

        config_layout = self.get_formated_h_layout()
        config_layout.addWidget(self.date_button)
        config_layout.addWidget(self.config_button)

        # label that displayes the current date ----------------
        self.current_work_day_label = QLabel(\
            self.context.current_work_day.strftime(self.context.date_format))
        self.current_work_day_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # combo to select the subject --------------------------
        self.subject_combo = QComboBox()
        self.subject_combo.setEnabled(self.state.combo_box_enable)
        for i in self.context.subjects.values():
            # only add subject to dropdown if the work_day is
            # inside the subjects valid dates
            if i.start_date <= self.context.current_work_day and\
                i.end_date >= self.context.current_work_day:
                self.subject_combo.addItem(i.name, i)
        self.subject_combo.setFixedWidth(self.context.total_timer_width)

        if self.subject_combo.currentData():
            self.subject_combo_changed(self.subject_combo.currentData().subject_id)
            self.subject_combo.activated.connect(\
                lambda: self.subject_combo_changed(self.subject_combo.currentData().subject_id))
        else:
            self.subject_combo.activated.connect(\
                lambda: self.subject_combo_changed(0))

        # progress bar for timer -----------------
        self.p_bar = QProgressBar(font=context.font)
        self.p_bar.setFormat("00:00:00")
        self.p_bar.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.p_bar.setMaximumWidth(self.context.progress_bar_width)
        self.p_bar.setValue(0)
        self.p_bar.setRange(0, int(self.state.progress_bar_max_range))
        self.p_bar.setTextVisible(True)

        # summary labels -----------------
        self.work_summary_subject_label = QLabel(self.context.work_session_subject_name)
        self.break_summary_subject_label = QLabel(self.context.break_sesson_subject_name)
        self.work_total_summary_label = QLabel(self.context.work_session_total_name)
        self.break_total_summary_label = QLabel(self.context.break_session_total_name)
        self.coffee_total_summary_label = QLabel(self.context.coffee_session_total_name)

        self.work_summary_subject_time = QLabel(self.context.summary_label_init)
        self.break_summary_subject_time = QLabel(self.context.summary_label_init)
        self.work_total_summary_time = QLabel(self.context.summary_label_init)
        self.break_total_summary_time = QLabel(self.context.summary_label_init)
        self.coffee_total_summary_time = QLabel(self.context.summary_label_init)

        self.work_summary_subject_layout = self.get_formated_h_layout()
        self.break_summary_subject_layout = self.get_formated_h_layout()
        self.work_total_summary_layout = self.get_formated_h_layout()
        self.break_total_summary_layout = self.get_formated_h_layout()
        self.coffee_total_summary_layout = self.get_formated_h_layout()

        self.work_summary_subject_layout.addWidget(VerticalSpacer(5, None))
        self.work_summary_subject_layout.addWidget(self.work_summary_subject_label)
        self.work_summary_subject_layout.addWidget(self.work_summary_subject_time)
        self.work_summary_subject_layout.addWidget(VerticalSpacer(5, None))

        self.break_summary_subject_layout.addWidget(VerticalSpacer(5, None))
        self.break_summary_subject_layout.addWidget(self.break_summary_subject_label)
        self.break_summary_subject_layout.addWidget(self.break_summary_subject_time)
        self.break_summary_subject_layout.addWidget(VerticalSpacer(5, None))

        self.work_total_summary_layout.addWidget(VerticalSpacer(5, None))
        self.work_total_summary_layout.addWidget(self.work_total_summary_label)
        self.work_total_summary_layout.addWidget(self.work_total_summary_time)
        self.work_total_summary_layout.addWidget(VerticalSpacer(5, None))

        self.break_total_summary_layout.addWidget(VerticalSpacer(5, None))
        self.break_total_summary_layout.addWidget(self.break_total_summary_label)
        self.break_total_summary_layout.addWidget(self.break_total_summary_time)
        self.break_total_summary_layout.addWidget(VerticalSpacer(5, None))

        self.coffee_total_summary_layout.addWidget(VerticalSpacer(5, None))
        self.coffee_total_summary_layout.addWidget(self.coffee_total_summary_label)
        self.coffee_total_summary_layout.addWidget(self.coffee_total_summary_time)
        self.coffee_total_summary_layout.addWidget(VerticalSpacer(5, None))

        self.stop_button = QPushButton()
        self.stop_button.setIconSize(QSize(\
            self.context.control_button_icon_width,\
                self.context.control_button_icon_width))
        self.stop_button.setIcon(QIcon("./img/stop.png"))
        self.stop_button.setFixedSize(\
            self.context.control_button_width,\
                self.context.control_button_width)
        self.stop_button.setFlat(True)
        self.stop_button.clicked.connect(self.stop_button_clicked)

        run_stop_layout = self.get_formated_h_layout()
        run_stop_layout.addWidget(self.stop_button)

        # work, break and coffee buttons ------------------------------------
        self.work_label = VerticalLabel(\
            self.context.work_description,\
                self.context.vertical_label_width,\
                    self.context.button_height,\
                        0.75, 0.72,\
                            self.context)
        self.work_label.clicked.connect(self.work_label_clicked)

        self.work_button = QPushButton()
        self.work_button.setEnabled(self.state.work_button_enable)
        self.work_button.setIconSize(QSize(\
            self.context.button_icon_width,\
                self.context.button_icon_height))
        self.work_button.setIcon(QIcon("./img/work.png"))
        self.work_button.setFixedSize(self.context.button_width, self.context.button_height)
        self.work_button.setFlat(True)
        self.work_button.clicked.connect(self.work_button_clicked)

        self.work_layout = self.get_formated_h_layout()
        self.work_layout.addWidget(self.work_label)
        self.work_layout.addWidget(self.work_button)

        self.break_label = VerticalLabel(\
            self.context.break_description,\
                self.context.vertical_label_width,\
                    self.context.button_height,\
                        0.75, 0.73,\
                            self.context)
        self.break_label.clicked.connect(self.break_label_clicked)

        self.break_button = QPushButton()
        self.break_button.setEnabled(self.state.break_button_enable)
        self.break_button.setIconSize(QSize(\
            self.context.button_icon_width,\
                self.context.button_icon_height))
        self.break_button.setIcon(QIcon("./img/break.png"))
        self.break_button.setFixedSize(self.context.button_width, self.context.button_height)
        self.break_button.setFlat(True)
        self.break_button.clicked.connect(self.break_button_clicked)

        self.break_layout = self.get_formated_h_layout()
        self.break_layout.addWidget(self.break_label)
        self.break_layout.addWidget(self.break_button)

        self.coffee_label = VerticalLabel(\
            self.context.coffee_description,\
                self.context.vertical_label_width,\
                    self.context.button_height,\
                        0.75, 0.78,\
                            self.context)
        self.coffee_label.clicked.connect(self.coffee_label_clicked)

        self.coffee_button = QPushButton()
        self.coffee_button.setEnabled(self.state.coffee_button_enable)
        self.coffee_button.setIconSize(QSize(\
            self.context.button_icon_width,\
                self.context.button_icon_height))
        self.coffee_button.setIcon(QIcon("./img/coffee.png"))
        self.coffee_button.setFixedSize(self.context.button_width, self.context.button_height)
        self.coffee_button.setFlat(True)
        self.coffee_button.clicked.connect(self.coffee_button_clicked)

        self.coffee_layout = self.get_formated_h_layout()
        self.coffee_layout.addWidget(self.coffee_label)
        self.coffee_layout.addWidget(self.coffee_button)

        # bottom, horizontal bar with a nice, fitting color -----------------
        self.last_vert_spacer = VerticalSpacer(None, 5)
        self.last_vert_spacer.setStyleSheet(\
            "background-color: rgb(" + self.context.base_spacer_color + ")")

        # main layout -----------------
        vbox = self.get_formated_v_layout()
        vbox.setAlignment(Qt.AlignmentFlag.AlignTop)

        vbox.addWidget(VerticalSpacer(None, 15))
        vbox.addLayout(dismiss_layout)
        vbox.addWidget(VerticalSpacer(None, 15))
        vbox.addLayout(config_layout)
        vbox.addWidget(VerticalSpacer(None, 15))
        vbox.addWidget(self.current_work_day_label)
        vbox.addWidget(VerticalSpacer(None, 15))
        vbox.addWidget(self.p_bar)
        vbox.addWidget(VerticalSpacer(None, 15))
        vbox.addWidget(self.subject_combo)
        vbox.addWidget(VerticalSpacer(None, 15))
        vbox.addLayout(self.work_summary_subject_layout)
        vbox.addLayout(self.break_summary_subject_layout)
        vbox.addWidget(VerticalSpacer(None, 15))
        vbox.addLayout(self.work_total_summary_layout)
        vbox.addLayout(self.break_total_summary_layout)
        vbox.addLayout(self.coffee_total_summary_layout)
        vbox.addWidget(VerticalSpacer(None, 15))
        vbox.addLayout(run_stop_layout)
        vbox.addLayout(self.work_layout)
        vbox.addLayout(self.break_layout)
        vbox.addLayout(self.coffee_layout)
        vbox.addWidget(self.last_vert_spacer)

        vbox_widget = QWidget()
        vbox_widget.setLayout(vbox)

        self.communicator.SIGNAL_CURRENT_WORKDAY_CHANGED.connect(\
            self.current_workday_changed_slot)
        self.communicator.SIGNAL_CURRENT_ROUND_UP.connect(self.play_signal_bell)

        vbox_widget.setFixedWidth(self.context.total_timer_width)

        self.main_config_window =\
            mainconfigwindow.MainConfigWindow(self.context, self.communicator)

        self.left_vertical_spacer = VerticalSpacer(1, None)
        self.left_vertical_spacer.setStyleSheet(\
            "background-color: rgb(" + self.context.base_spacer_color + ")")

        hbox = self.get_formated_h_layout()
        hbox.setAlignment(Qt.AlignmentFlag.AlignLeft)
        hbox.addWidget(vbox_widget)
        hbox.addWidget(self.left_vertical_spacer)
        hbox.addWidget(self.main_config_window)
        self.setMaximumWidth(self.context.total_timer_width)
        self.setLayout(hbox)

        self.setWindowTitle("  ")
        self.setWindowIcon(QIcon("./img/title.png"))

        # first assume that we don't want to show config window by default
        self.show_config_widget = False
        self.left_vertical_spacer.hide()
        self.main_config_window.hide()

        self.loaded = True
        self.update_summary_labels()
        self.signal_bell_ringed = False

        # see if we want to show the config window by default
        # this one calls show()
        self.set_timer_only_window_flags()
        if self.context.show_schedule_widget_at_startup:
            # this one may change the windowFlags and call show()
            # again
            self.config_button_clicked()

        self.setFont(context.font)
        self.setStyleSheet(context.style)

    def __del__(self):
        self.timer.stop()
        if self.state.current_work_unit_entry is not None:
            self.close_db_data()

    def reset_q_bar(self):

        """reset progress bar to default state"""

        self.p_bar.setStyleSheet("")
        self.p_bar.setValue(0)
        self.p_bar.setFormat(self.format_time(0))

    def format_time(self, seconds, scale=True, down=True):

        """
        converts seconds to hours:minutes:seconds format
        also makes sure the time is scaled properly and rounded
        properly depending on which way the clock ticks (up or down)
        """

        if scale:
            factor = (1000/self.context.time_step)
        else:
            factor = 1

        if seconds < 0:
            sec = (self.state.session_time - seconds)/factor + 1
        else:
            sec = seconds/factor

        hours, remainder = divmod(sec, 3600)
        minutes, seconds = divmod(remainder, 60)

        if down:
            if seconds > 59:
                minutes = minutes + 1
                seconds = 0
                if minutes == 60:
                    minutes = 0
                    hours = hours + 1

            time_str = "{:02}:{:02}:{:02}".format(\
                int(math.ceil(hours)),\
                    int(math.ceil(minutes)),\
                        int(math.ceil(seconds)))
        else:
            time_str = "{:02}:{:02}:{:02}".format(\
                int(math.floor(hours)),\
                    int(math.floor(minutes)),\
                        int(math.floor(seconds)))

        return time_str

    def update_ui(self):

        """set buttons and other stuff enabled or disabled"""

        self.dismiss_button.setEnabled(self.state.dismiss_button_enable)
        self.work_button.setEnabled(self.state.work_button_enable)
        self.break_button.setEnabled(self.state.break_button_enable)
        self.coffee_button.setEnabled(self.state.coffee_button_enable)
        self.stop_button.setEnabled(self.state.stop_button_enable)
        self.date_button.setEnabled(self.state.date_button_enable)
        self.config_button.setEnabled(self.state.config_button_enable)
        self.subject_combo.setEnabled(self.state.combo_box_enable)

        if self.state.work_type == dbwrapper.UnitTypes.WORK_TIME:
            self.work_label.set_active()
            self.break_label.set_inactive()
            self.coffee_label.set_inactive()
        elif self.state.work_type == dbwrapper.UnitTypes.BREAK_TIME:
            self.work_label.set_inactive()
            self.break_label.set_active()
            self.coffee_label.set_inactive()
        elif self.state.work_type == dbwrapper.UnitTypes.COFFEE_TIME:
            self.work_label.set_inactive()
            self.break_label.set_inactive()
            self.coffee_label.set_active()
        else:
            self.work_label.set_inactive()
            self.break_label.set_inactive()
            self.coffee_label.set_inactive()

    def update_summary_labels(self):

        """update information displayed in the summary slots"""

        if not self.loaded:
            return

        self.work_summary_subject_time.setText(self.format_time(\
            dbwrapper.Summary.total_work_for_subject_and_workday(\
                self.context.current_work_day,\
                    self.state.current_subject_id,\
                        self.context.db_file_name),\
                            False, False))
        self.break_summary_subject_time.setText(self.format_time(\
            dbwrapper.Summary.total_break_for_subject_and_workday(\
                self.context.current_work_day,\
                    self.state.current_subject_id,\
                        self.context.db_file_name),\
                            False, False))
        self.work_total_summary_time.setText(self.format_time(\
            dbwrapper.Summary.total_work_for_workday(\
                self.context.current_work_day,\
                    self.context.db_file_name),\
                        False, False))
        self.break_total_summary_time.setText(self.format_time(\
            dbwrapper.Summary.total_break_for_workday(\
                self.context.current_work_day,\
                    self.context.db_file_name),\
                        False, False))
        self.coffee_total_summary_time.setText(self.format_time(\
            dbwrapper.Summary.total_coffee_for_workday(\
                self.context.current_work_day,\
                    self.context.db_file_name),\
                        False, False))

    def get_new_work_unit_entry_obj(self):

        """
        return a new work_unit_entry object with current state
        and time specs
        """

        return dbwrapper.WorkUnitEntry.new(\
                self.context.free_work_subject_type_key,\
                    self.state.current_subject_id,\
                        0,\
                            self.state.work_type,\
                                self.context.start_time_offset,\
                                    datetime.now().time(),\
                                        datetime.now().date(),\
                                            datetime.now().time(),\
                                                datetime.now().date(),\
                                                    0,\
                                                        "")

    def update_db_data(self):

        """update db data (store or update)"""

        if self.state.current_work_unit_entry is None:
            self.state.current_work_unit_entry = self.get_new_work_unit_entry_obj()
            dbwrapper.WorkUnitEntry.to_db(self.state.current_work_unit_entry,\
                self.context.work_unit_entries,\
                    self.context.db_file_name)
        else:
            cur_wue = self.state.current_work_unit_entry
            cur_wue.subject_id = self.state.current_subject_id
            cur_wue.unit_type = self.state.work_type
            cur_wue.end_time = datetime.now().time()
            cur_wue.end_date = datetime.now().date()
            cur_wue.state = 1

            dbwrapper.WorkUnitEntry.update_by_db_id(\
                self.state.current_work_unit_entry,\
                    self.context.db_file_name)

        self.update_summary_labels()

        # redraw schedule view if it is open
        if self.show_config_widget:
            self.communicator.SIGNAL_DATES_CHANGED.emit()

    def close_db_data(self):

        """close data set in db"""

        cur_wue = self.state.current_work_unit_entry
        cur_wue.subject_id = self.state.current_subject_id
        cur_wue.unit_type = self.state.work_type
        cur_wue.end_time = datetime.now().time()
        cur_wue.end_date = datetime.now().date()
        cur_wue.state = 2

        dbwrapper.WorkUnitEntry.update_by_db_id(\
            self.state.current_work_unit_entry,\
                self.context.db_file_name)

        self.update_summary_labels()

        # redraw schedule view if it is open
        if self.show_config_widget:
            self.communicator.SIGNAL_DATES_CHANGED.emit()

    def update_progress_bar(self, value, seconds, down):

        """
        update the progessbar so that time interval <= 25 min are
        nice and green and times > 25 min are red with no progress
        """

        if value >= 0 and value <= self.state.progress_bar_max_range:
            self.p_bar.setValue(int(value))
            self.p_bar.setStyleSheet("")
        else:
            self.p_bar.setValue(int(self.state.progress_bar_max_range))
            self.p_bar.setStyleSheet("QProgressBar::chunk{background-color: red}")
        self.p_bar.setFormat(self.format_time(seconds, True, down))

    def moveEvent(self, event): # pylint: disable=invalid-name, unused-argument

        """event handler for when the timer is moved by the user"""

        self.communicator.SIGNAL_TIMER_MOVED.emit()

    def closeEvent(self, event): # pylint: disable=invalid-name, unused-argument

        """clean up unfinished busines"""

        if self.state.current_work_unit_entry is not None:
            self.close_db_data()

    @pyqtSlot()
    def play_signal_bell(self):

        """play the bell when work or break is finished"""

        # QSound.play("signal.wav")
        # playsound("signal.wav", block=False)

    @pyqtSlot()
    def current_workday_changed_slot(self):

        """change text in current work day label"""

        # the context.current_work_day is changed in the date picker
        self.current_work_day_label.setText(\
            self.context.current_work_day.strftime(self.context.date_format))

        if self.state.timer_is_running:
            self.update_db_data()

        self.subject_combo.clear()
        for i in self.context.subjects.values():
            # only add subject to dropdown if the work_day is
            # inside the subjects valid dates
            if i.start_date <= self.context.current_work_day and\
                i.end_date >= self.context.current_work_day:
                self.subject_combo.addItem(i.name, i)

        self.update_summary_labels()

    @pyqtSlot()
    def datepicker_button_clicked(self):

        """display datepicker window slot"""

        if self.date_button_active:
            return

        self.date_button_active = True
        DatePicker(self.communicator, self.context, self.date_button)

    @pyqtSlot()
    def enable_date_button_slot(self):

        """enable datepicker button"""

        self.date_button_active = False

    @pyqtSlot()
    def config_button_clicked(self):

        """display config window slot"""

        if not self.show_config_widget:
            self.config_button.setIcon(QIcon("./img/close_config.png"))
            self.config_button.setIconSize(QSize(\
                self.context.control_button_icon_width,\
                    self.context.control_button_icon_width))

            self.left_vertical_spacer.show()
            self.main_config_window.show()

            # remove the bottom gray bar
            self.last_vert_spacer.hide()
            # first set maximum width to the biggest possible value
            self.setMaximumWidth(16777215)
            # then set the minimum size to the one that should be shown initially
            self.setMinimumSize(\
                self.context.initial_window_width, self.context.initial_window_height)
            # change the mode of the window to normal to enable maximizing
            self.set_timer_config_window_flags()
            # then reset the minimum size to 0 to have a totally resizable window
            self.setMinimumSize(0, 0)
        else:
            self.config_button.setIcon(QIcon("./img/open_config.png"))
            self.config_button.setIconSize(QSize(\
                self.context.control_button_icon_width,\
                    self.context.control_button_icon_width))

            self.left_vertical_spacer.hide()
            self.main_config_window.hide()
            if self.isMaximized():
                self.showNormal()

            # make the window have minimum size of 0
            self.setMinimumSize(0, 0)
            # and maximum width of the timer
            self.setMaximumWidth(self.context.total_timer_width)
            # show the bottom gray bar
            self.last_vert_spacer.show()
            # then set the window mode to have only the close-X
            self.set_timer_only_window_flags()

        self.show_config_widget = not self.show_config_widget

        # redraw schedule view if it is open
        if self.show_config_widget:
            self.communicator.SIGNAL_DATES_CHANGED.emit()

    def set_timer_only_window_flags(self):

        """set flags for timer-only window"""

        self.setWindowFlags(\
            Qt.WindowType.WindowStaysOnTopHint |\
                Qt.WindowType.WindowCloseButtonHint)
        self.show()

    def set_timer_config_window_flags(self):

        """set flags for timer-only window"""

        self.setWindowFlags(\
            Qt.WindowType.WindowCloseButtonHint |\
                Qt.WindowType.WindowMinMaxButtonsHint)
        self.show()

    @pyqtSlot()
    def timer_timeout(self):

        """timer slot"""

        progress_value = 0
        if self.state.work_time_interval_value > 0:
            progress_value = int(((self.state.work_time_interval_value -\
                self.state.current_session_time_value) /\
                    self.state.work_time_interval_value) * self.state.progress_bar_max_range)
        else:
            progress_value = -1

        if progress_value == 0 and not self.signal_bell_ringed:
            self.communicator.SIGNAL_CURRENT_ROUND_UP.emit()
            self.signal_bell_ringed = True
            QTimer.singleShot(5000, self.allow_signal_bell_ring)

        if progress_value == self.state.progress_bar_max_range:
            progress_value = progress_value - 1

        if self.state.session_time_value > 0:
            self.update_progress_bar(progress_value, self.state.session_time_value, True)
        else:
            self.update_progress_bar(progress_value, self.state.current_session_time_value, False)

        self.state.session_time_value = self.state.session_time_value - 1
        self.state.current_session_time_value = self.state.current_session_time_value + 1

    @pyqtSlot()
    def allow_signal_bell_ring(self):

        """set signal_bell_ringed to false, so that it can ring again"""

        self.signal_bell_ringed = False

    @pyqtSlot()
    def dismiss_button_clicked(self):

        """dismiss button clicked"""

        if self.state.timer_is_running:
            self.timer.stop()
            dbwrapper.WorkUnitEntry.delete_by_db_id(\
                self.state.current_work_unit_entry,\
                    self.context.work_unit_entries,\
                        self.context.db_file_name,\
                            self.context.db_file_name)
            self.state.reset_running_state(self.context.work_time_interval)
            self.reset_q_bar()
            self.state.enable_all()
            self.update_ui()

    @pyqtSlot()
    def stop_button_clicked(self):

        """stop button clicked"""

        if self.state.timer_is_running:
            self.timer.stop()
            self.close_db_data()
            self.state.reset_running_state(self.context.work_time_interval)
            self.reset_q_bar()
            self.state.enable_all()
            self.update_ui()

    @pyqtSlot()
    def work_label_clicked(self):

        """vertical work label clicked"""

        if self.state.timer_is_running:
            self.state.disable_work()
            self.state.work_type = dbwrapper.UnitTypes.WORK_TIME
            self.update_db_data()
            self.update_ui()

    @pyqtSlot()
    def break_label_clicked(self):

        """vertical break label clicked"""

        if self.state.timer_is_running:
            self.state.disable_break()
            self.state.work_type = dbwrapper.UnitTypes.BREAK_TIME
            self.update_db_data()
            self.update_ui()

    @pyqtSlot()
    def coffee_label_clicked(self):

        """vertical coffee label clicked"""

        if self.state.timer_is_running:
            self.state.disable_coffee()
            self.state.work_type = dbwrapper.UnitTypes.COFFEE_TIME
            self.update_db_data()
            self.update_ui()

    @pyqtSlot()
    def work_button_clicked(self):

        """work button clicked"""

        self.state.disable_work()

        if self.state.timer_is_running:
            self.timer.stop()
            self.close_db_data()
            self.reset_q_bar()

        self.state.reset_running_state(self.context.work_time_interval)
        self.timer.start(self.context.time_step)
        self.state.work_type = dbwrapper.UnitTypes.WORK_TIME
        self.state.timer_is_running = True
        self.update_db_data()
        self.update_ui()

    @pyqtSlot()
    def break_button_clicked(self):

        """break button clicked"""

        self.state.disable_break()

        if self.state.timer_is_running:
            self.timer.stop()
            self.close_db_data()
            self.reset_q_bar()

        self.state.reset_running_state(self.context.break_time_interval)
        self.timer.start(self.context.time_step)
        self.state.timer_is_running = True
        self.state.work_type = dbwrapper.UnitTypes.BREAK_TIME
        self.update_db_data()
        self.update_ui()

    @pyqtSlot()
    def coffee_button_clicked(self):

        """coffee button clicked"""

        self.state.disable_coffee()

        if self.state.timer_is_running:
            self.timer.stop()
            self.close_db_data()
            self.reset_q_bar()

        self.state.reset_running_state(self.context.coffee_time_interval)
        self.timer.start(self.context.time_step)
        self.state.timer_is_running = True
        self.state.work_type = dbwrapper.UnitTypes.COFFEE_TIME
        self.update_db_data()
        self.update_ui()

    @pyqtSlot(int)
    def subject_combo_changed(self, new_subject_id):

        """subject combo changed slot"""

        self.state.current_subject_id = new_subject_id

        if self.state.timer_is_running:
            self.update_db_data()
        else:
            self.update_summary_labels()
