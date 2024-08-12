# pylint: disable=too-many-lines
"""
ScheduleCanvas with methodes to crate grid with stuff on it
"""

import random
from datetime import datetime, time, date, timedelta
from PyQt6.QtWidgets import QWidget, QDialog, QComboBox, QCheckBox
from PyQt6.QtWidgets import QHBoxLayout, QVBoxLayout, QPushButton
from PyQt6.QtWidgets import QLineEdit, QLabel, QDateEdit, QTimeEdit
from PyQt6.QtWidgets import QSpacerItem, QSizePolicy
from PyQt6.QtGui import QWheelEvent
from PyQt6.QtGui import QPainter, QBrush, QPalette, QFont
from PyQt6.QtCore import Qt, QRect, pyqtSlot, QPoint, QDate, QTime
import dbobj.dbwrapper as dbwrapper
from dbobj.helperfunctions import HelperFunctions as HF
from helpers.canvasgrid import CanvasGrid
from helpers.verticalspacer import VerticalSpacer

class SelectRect(QRect):

    """
    Class represents the select rectangle created with the mouse
    """

    # TODO: better suport for mouse moves in upwards direction

    def __init__(self, initX, initY, context):
        self.context = context

        self.init_x = int((initX) / self.context.box_width) *\
                self.context.box_width

        self.init_y = int((initY - self.context.top_offset) /\
            self.context.box_height) *\
                self.context.box_height +\
                    self.context.top_offset

        super().__init__(self.init_x, self.init_y, self.context.box_width, self.context.box_height)

        self.repaint = True

    def update(self, y_coord):

        """Update rect with new height"""

        rect_height = self.getRect()[3]

        h_new = int((y_coord - self.init_y) / self.context.box_height) *\
            self.context.box_height + self.context.box_height

        if rect_height != h_new:
            self.setHeight(h_new)
            self.repaint = True

    def paint(self, painter, brush):

        """Paint methode"""

        brush.setColor(self.context.select_rect_color)
        painter.fillRect(self, brush)
        self.repaint = False

    def to_repaint(self):

        """Return True if rect needs repaint in main canvas"""

        return self.repaint

class WorkUnitRect(QRect):

    """
    Class represents one single work unit including color and stuff
    """

    def __init__(self, work_unit, from_x, from_y, width, height, context):

        break_time = dbwrapper.UnitTypes.BREAK_TIME
        work_time = dbwrapper.UnitTypes.WORK_TIME
        coffee_time = dbwrapper.UnitTypes.COFFEE_TIME
        school_time = dbwrapper.UnitTypes.SCHOOL_TIME
        tus_width = context.time_unit_rect_subject_width
        bb_width = context.box_border_width

        if work_unit.unit_type == work_time:
            self.color = context.display_work_unit_color
        elif work_unit.unit_type == break_time:
            self.color = context.display_break_unit_color
        elif work_unit.unit_type == coffee_time:
            self.color = context.display_coffee_unit_color
        elif work_unit.unit_type == school_time:
            self.color = context.display_school_unit_color

        self.context = context
        self.work_unit = work_unit

        if self.work_unit.unit_type in (work_time, break_time):
            self.subject_rect = QRect(\
                from_x + bb_width, from_y, tus_width - 2*bb_width, height)
            super().__init__(\
                from_x + tus_width, from_y, width - tus_width, height)
        else:
            self.subject_rect = None
            super().__init__(from_x, from_y, width, height)


    def paint(self, painter, brush):

        """paints single time unit with corresponding color"""

        brush.setColor(self.color)
        painter.fillRect(self, brush)

        if self.subject_rect is not None:
            brush.setColor(self.context.subjects[self.work_unit.subject_id].color)
            painter.fillRect(self.subject_rect, brush)

class WorkUnitDisplay():

    """
    Class represents one day of consecutive work units
    Only displays something if the time is at least one minute
    """

    def __init__(self, work_units, communicator, context):
        self.communicator = communicator
        self.context = context
        self.work_day = work_units[0].start_date
        self.work_unit_rects = list()

        for i in work_units:
            self.work_unit_rects.append(self.to_rect(i, context))

    def to_rect(self, work_unit, context):

        """
        translate date and time to coordinates on canvas
        no need for to_x because the width of a field is given by schedule_box_width
        """

        day_index = (work_unit.start_date - self.context.start_date).days

        # if an entry runs from 00:00 to 04:59 the next day (over midnight)
        # we need some offset in order to map it correctly to the displayed range
        # also go one day back from the start_date
        net_over_midnight_offset = 0 # take into account the offset

        # if we only work longer than midnight and one session happenes to go over
        # the threshhold, the start time may be 23:50 and the end time 00:15
        # => add some offset to the end_time
        real_over_midnight_offset = 0 # real time is over midnight

        if work_unit.start_date != work_unit.load_date:
            net_over_midnight_offset = (1440 - work_unit.start_offset) * self.context.minute_height
            day_index = day_index - 1
        elif work_unit.end_time < work_unit.start_time:
            real_over_midnight_offset = 1440 * self.context.minute_height

        from_y = ((work_unit.start_time.hour - work_unit.start_offset)*60 +\
            work_unit.start_time.minute)*self.context.minute_height + self.context.top_offset

        to_y = ((work_unit.end_time.hour - work_unit.start_offset)*60 +\
            work_unit.end_time.minute)*self.context.minute_height + self.context.top_offset

        from_x = day_index*self.context.box_width + self.context.scheduled_box_width

        to_x = from_x + self.context.box_width - self.context.box_border_width -\
            self.context.scheduled_box_width

        return WorkUnitRect(\
            work_unit,\
                from_x, from_y + net_over_midnight_offset,\
                    to_x - from_x, (real_over_midnight_offset + to_y - from_y),\
                        context)

    def paint(self, painter, brush):

        """paints the current work units"""

        for i in self.work_unit_rects:
            i.paint(painter, brush)

class ScheduleEntryConfig(QDialog):

    """
    Class represents entry dialog for schedule entry configs
    """

    def __init__(self, schedule_rect, schedule_rect_list, communicator, context, parent):

        super().__init__(parent=parent)

        if not context.study_subject:
            # no data in the db, don't show menu
            print("No data in db")
            return

        self.parent = parent
        self.context = context
        self.communicator = communicator
        self.schedule_rect = schedule_rect
        self.schedule_rect_list = schedule_rect_list
        self.work_unit_entry = None

        # TODO: change description field for schedule entry to function as a todo list

        # we need some mapping between the subject_id and the combo box index
        # since the combo box needs something zero based and the subject_id is
        # arbitrary (same for subject_type_id)
        self.subject_index_mapping = dict()
        self.type_index_mapping = dict()

        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Dialog)

        self.setStyleSheet(context.style)
        self.setStyleSheet("QDialog{border:2px solid black}")

        self.communicator.SIGNAL_MAINWINDOW_MOVED.connect(self.move_slot)

        self.scheduled_checkbox = QCheckBox()
        self.scheduled_checkbox.stateChanged.connect(self.check_changed)

        self.ok_button = QPushButton("Ok")
        self.ok_button.setFont(context.font)
        cancel_button = QPushButton("Cancel")
        cancel_button.setFont(context.font)
        self.delete_button = QPushButton("Delete")
        self.delete_button.setFont(context.font)
        self.description = QLineEdit()
        self.description.setFont(context.font)

        self.subject_combo = QComboBox()
        self.subject_combo.setFont(context.font)
        c_index = 0
        study_obj = self.context.study_subject
        self.subject_combo.addItem(\
            study_obj.description, (study_obj.subject_id, study_obj))
        self.subject_index_mapping[self.context.study_subject.subject_id] = c_index
        c_index = 1
        for i in self.context.subjects.items():

            # if the current subject is not within the range of the chosen dates, leave them out
            if not (self.context.start_date <= i[1].end_date\
                and self.context.end_date >= i[1].start_date):
                continue

            self.subject_combo.addItem(i[1].description, i)
            self.subject_index_mapping[i[0]] = c_index
            c_index = c_index + 1

        self.type_combo = QComboBox()
        self.type_combo.setFont(context.font)
        c_index = 0
        for i in self.context.subject_types.items():
            self.type_combo.addItem(i[1].description, i)
            self.type_index_mapping[i[0]] = c_index
            c_index = c_index + 1

        self.ok_button.clicked.connect(self.ok_slot)
        cancel_button.clicked.connect(self.cancel_slot)
        self.delete_button.clicked.connect(self.delete_slot)

        self.from_date_edit = QDateEdit()
        self.from_date_edit.setFont(context.font)
        self.from_date_edit.setEnabled(False)
        self.from_date_edit.setDisplayFormat("dd.MM.yyyy")

        self.to_date_edit = QDateEdit()
        self.to_date_edit.setFont(context.font)
        self.to_date_edit.setEnabled(False) # initially not checked
        self.to_date_edit.setDisplayFormat("dd.MM.yyyy")

        v_layout1 = QVBoxLayout()
        v_layout1.setAlignment(Qt.AlignmentFlag.AlignTop)
        v_layout1.addWidget(self.subject_combo)
        v_layout1.addWidget(self.type_combo)

        h_layout2_0 = QHBoxLayout()
        h_layout2_0.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
        h_layout2_0.addWidget(QLabel("Scheduled", font=context.font))
        h_layout2_0.addWidget(self.scheduled_checkbox)

        h_layout2_1 = QHBoxLayout()
        h_layout2_1.addWidget(QLabel("From", font=context.font), Qt.AlignmentFlag.AlignLeft)
        h_layout2_1.addWidget(self.from_date_edit, Qt.AlignmentFlag.AlignRight)
        h_layout2_2 = QHBoxLayout()
        h_layout2_2.addWidget(QLabel("To", font=context.font), Qt.AlignmentFlag.AlignLeft)
        h_layout2_2.addWidget(self.to_date_edit, Qt.AlignmentFlag.AlignRight)

        h_layout4 = QHBoxLayout()
        h_layout4.setAlignment(Qt.AlignmentFlag.AlignBottom)
        h_layout4.addWidget(self.delete_button)
        h_layout4.addWidget(self.ok_button)
        h_layout4.addWidget(cancel_button)

        book_sublayout1 = QHBoxLayout()
        book_sublayout2 = QHBoxLayout()
        book_layout = QVBoxLayout()
        self.book_button = QPushButton("Book Time")
        self.book_button.setFont(context.font)
        self.delete_time_button = QPushButton("Delete Time")
        self.delete_time_button.setFont(context.font)
        self.from_time = QTimeEdit()
        self.from_time.setFont(context.font)
        self.to_time = QTimeEdit()
        self.to_time.setFont(context.font)
        book_sublayout1.addWidget(self.book_button)
        book_sublayout1.addWidget(QLabel("Start time", font=context.font), Qt.AlignmentFlag.AlignLeft)
        book_sublayout1.addWidget(self.from_time, Qt.AlignmentFlag.AlignRight)
        book_sublayout2.addWidget(self.delete_time_button)
        book_sublayout2.addWidget(QLabel("End time  ", font=context.font), Qt.AlignmentFlag.AlignLeft)
        book_sublayout2.addWidget(self.to_time, Qt.AlignmentFlag.AlignRight)

        book_layout.addLayout(book_sublayout1)
        book_layout.addLayout(book_sublayout2)

        self.book_button.clicked.connect(self.book_button_clicked)
        self.delete_time_button.clicked.connect(self.delete_time_button_clicked)

        line1 = VerticalSpacer(None, 1)
        line1.setStyleSheet("background-color: rgb(" + self.context.base_spacer_color + ")")
        line2 = VerticalSpacer(None, 1)
        line2.setStyleSheet("background-color: rgb(" + self.context.base_spacer_color + ")")
        line3 = VerticalSpacer(None, 1)
        line3.setStyleSheet("background-color: rgb(" + self.context.base_spacer_color + ")")

        v_layout = QVBoxLayout()
        v_layout.addLayout(h_layout2_0, Qt.AlignmentFlag.AlignTop)
        v_layout.addWidget(line1)
        v_layout.addLayout(v_layout1, Qt.AlignmentFlag.AlignTop)
        v_layout.addLayout(h_layout2_1, Qt.AlignmentFlag.AlignTop)
        v_layout.addLayout(h_layout2_2, Qt.AlignmentFlag.AlignTop)
        v_layout.addWidget(QLabel("Description", font=context.font), Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
        v_layout.addWidget(self.description, Qt.AlignmentFlag.AlignTop)
        v_layout.addWidget(line2)
        v_layout.addItem(QSpacerItem(10, 10, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding))
        v_layout.addLayout(book_layout, Qt.AlignmentFlag.AlignBottom)
        v_layout.addItem(QSpacerItem(10, 10, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding))
        v_layout.addWidget(line3)
        v_layout.addLayout(h_layout4, Qt.AlignmentFlag.AlignBottom)
        self.setLayout(v_layout)

        day_ind = self.schedule_rect.schedule_times.day_index
        self.planed_date = datetime.strptime(\
            self.context.date_list[day_ind], self.context.date_format).date()

        if schedule_rect.is_new == 1:
            self.delete_button.setEnabled(False)
            self.set_new_rect_properties()
        else:
            self.set_old_rect_properties()

        self.setFixedSize(\
            self.context.schedule_config_box_width,\
                self.context.schedule_config_box_height)
        self.move_slot()
        self.show()

    def __del__(self):
        pass

    def set_new_rect_properties(self):

        """initialize new config box"""

        from_date = self.planed_date
        to_date = self.planed_date

        from_hour = self.schedule_rect.schedule_times.from_hour
        to_hour = self.schedule_rect.schedule_times.to_hour
        from_minute = self.schedule_rect.schedule_times.from_minute
        to_minute = self.schedule_rect.schedule_times.to_minute

        if from_hour >= 24:
            from_hour = from_hour - 24
            from_date = from_date + timedelta(days=1)

        if to_hour >= 24:
            to_hour = to_hour - 24
            to_date = to_date + timedelta(days=1)

        self.from_date_edit.setDate(\
            QDate(from_date.year, from_date.month, from_date.day))
        self.to_date_edit.setDate(\
            QDate(to_date.year, to_date.month, to_date.day))

        subject_index = self.subject_index_mapping[self.context.study_subject.subject_id]
        type_index = self.type_index_mapping[self.context.free_work_subject_type_key]

        self.subject_combo.setCurrentIndex(subject_index)
        self.type_combo.setCurrentIndex(type_index)

        self.from_time.setTime(QTime(from_hour, from_minute))
        self.to_time.setTime(QTime(to_hour, to_minute))

        self.book_button.setEnabled(False)
        self.delete_time_button.setEnabled(False)
        self.from_time.setEnabled(False)
        self.to_time.setEnabled(False)

        self.work_unit_entry = None

    def set_old_rect_properties(self):

        """initialize config box with old rect properties"""

        schedule_entry = self.schedule_rect.schedule_entry
        series_obj = schedule_entry.series_obj

        # do the scheduled part
        if series_obj.start_date == series_obj.end_date:
            # not scheduled
            self.to_date_edit.setEnabled(False)
            self.from_date_edit.setEnabled(False)
        else:
            # scheduled
            self.scheduled_checkbox.blockSignals(True)
            self.scheduled_checkbox.setChecked(True) # put this at beginning because of signal
            self.scheduled_checkbox.blockSignals(False)

            self.to_date_edit.setEnabled(True)
            self.from_date_edit.setEnabled(True)

        start_date = self.schedule_rect.subject.start_date
        self.from_date_edit.setMinimumDate(\
            QDate(start_date.year, start_date.month, start_date.day)\
                )

        end_date = self.schedule_rect.subject.end_date
        self.to_date_edit.setMaximumDate(\
            QDate(end_date.year, end_date.month, end_date.day)\
                )

        planed_start_date = series_obj.start_date
        planed_end_date = series_obj.end_date
        self.from_date_edit.setDate(planed_start_date)
        self.to_date_edit.setDate(planed_end_date)

        subject_index = self.subject_index_mapping[self.schedule_rect.subject.key()]
        type_index = self.type_index_mapping[self.schedule_rect.subject_type.key()]
        self.subject_combo.setCurrentIndex(subject_index)
        self.type_combo.setCurrentIndex(type_index)

        self.description.setText(self.schedule_rect.schedule_entry.description)

        # load possible old booking
        self.work_unit_entry = None
        self.load_or_assign_booking()

        from_date = self.planed_date
        to_date = self.planed_date

        if self.work_unit_entry.state == 0:

            from_hour = self.schedule_rect.schedule_times.from_hour
            to_hour = self.schedule_rect.schedule_times.to_hour
            from_minute = self.schedule_rect.schedule_times.from_minute
            to_minute = self.schedule_rect.schedule_times.to_minute

            if from_hour >= 24:
                from_hour = from_hour - 24
                from_date = from_date + timedelta(days=1)

            if to_hour >= 24:
                to_hour = to_hour - 24
                to_date = to_date + timedelta(days=1)

            self.set_unbooked_view()

            self.from_time.setTime(\
                QTime(from_hour, from_minute))
            self.to_time.setTime(\
                QTime(to_hour, to_minute))
        else:

            from_hour = self.work_unit_entry.start_time.hour
            to_hour = self.work_unit_entry.end_time.hour
            from_minute = self.work_unit_entry.start_time.minute
            to_minute = self.work_unit_entry.end_time.minute

            if from_hour >= 24:
                from_hour = from_hour - 24
                from_date = from_date + timedelta(days=1)

            if to_hour >= 24:
                to_hour = to_hour - 24
                to_date = to_date + timedelta(days=1)

            self.set_booked_view()

            self.from_time.setTime(\
                QTime(from_hour, from_minute))
            self.to_time.setTime(\
                QTime(to_hour, to_minute))

        # check if the user is supposed to be able to book time
        # should work only for SUBJECT_TIME, not STUDY_TIME
        # this is supposed to override set_book_view or set_unbook_view
        if self.schedule_rect.subject.subject_type == dbwrapper.SubjectTypes.STUDY_TYPE:
            self.set_study_time_view()

    def set_study_time_view(self):

        """
        Configure the config view for study subject where the user
        should not be able to book time afterwards
        """

        self.from_time.setEnabled(False)
        self.to_time.setEnabled(False)
        self.book_button.setEnabled(False)
        self.delete_time_button.setEnabled(False)

    def set_booked_view(self):

        """
        If a time has already been booked, disable everything
        except the delete button
        """

        self.scheduled_checkbox.setEnabled(False)
        self.description.setEnabled(False)
        self.subject_combo.setEnabled(False)
        self.type_combo.setEnabled(False)
        self.from_date_edit.setEnabled(False)
        self.to_date_edit.setEnabled(False)

        self.book_button.setEnabled(False)
        self.ok_button.setEnabled(False)
        self.delete_time_button.setEnabled(True)
        self.from_time.setEnabled(False)
        self.to_time.setEnabled(False)
        self.delete_button.setEnabled(False)

    def set_unbooked_view(self):

        """
        If a time has already been booked, disable everything
        except the delete button
        """

        self.scheduled_checkbox.setEnabled(True)
        self.description.setEnabled(True)
        self.subject_combo.setEnabled(True)
        self.type_combo.setEnabled(True)
        self.from_date_edit.setEnabled(True)
        self.to_date_edit.setEnabled(True)

        self.ok_button.setEnabled(True)
        self.book_button.setEnabled(True)
        self.delete_time_button.setEnabled(False)
        self.from_time.setEnabled(True)
        self.to_time.setEnabled(True)

    def create_booking(self):

        """
        Create a new booking using the current data in the config view
        """

        from_date = self.planed_date
        to_date = self.planed_date
        from_hour = self.schedule_rect.schedule_times.from_hour
        from_minute = self.schedule_rect.schedule_times.from_minute
        to_hour = self.schedule_rect.schedule_times.to_hour
        to_minute = self.schedule_rect.schedule_times.to_minute

        if from_hour >= 24:
            from_hour = from_hour - 24
            from_date = from_date + timedelta(days=1)

        if to_hour >= 24:
            to_hour = to_hour - 24
            to_date = to_date + timedelta(days=1)

        from_datetime = datetime(\
            from_date.year,\
                from_date.month,\
                    from_date.day,\
                        from_hour,\
                            from_minute)

        to_datetime = datetime(\
            to_date.year,\
                to_date.month,\
                    to_date.day,\
                        to_hour,\
                            to_minute)

        booking_properties = dbwrapper.WorkUnitEntry.new(\
            self.schedule_rect.subject_type.subject_type_id,\
                self.schedule_rect.subject.subject_id,\
                    self.schedule_rect.schedule_entry.schedule_entry_id,\
                        dbwrapper.UnitTypes.SCHOOL_TIME,\
                            self.context.start_time_offset,\
                                from_datetime.time(),\
                                    from_datetime.date(),\
                                        to_datetime.time(),\
                                            to_datetime.date(),\
                                                0,\
                                                    "")

        return booking_properties

    def load_or_assign_booking(self):

        """
        Load existing work unit entry or assign a new one. If obj.state = 0
        then the obj is new and needs a to_db, if the obj.state = 2 then it's
        an old one and needs a potential update
        """

        booking_properties = self.create_booking()

        self.work_unit_entry = dbwrapper.WorkUnitEntry.load_entry_from_db(\
            booking_properties, self.context.db_file_name)

        if self.work_unit_entry is None:
            self.work_unit_entry = booking_properties

    @pyqtSlot()
    def check_changed(self):

        """capture check box state changed"""

        if self.scheduled_checkbox.isChecked():
            self.to_date_edit.setEnabled(True)
            self.from_date_edit.setEnabled(True)

            start_date = self.subject_combo.currentData()[1].start_date
            self.from_date_edit.setMinimumDate(\
                QDate(start_date.year, start_date.month, start_date.day)\
                    )
            self.from_date_edit.setDate(start_date)

            end_date = self.subject_combo.currentData()[1].end_date
            self.to_date_edit.setMaximumDate(\
                QDate(end_date.year, end_date.month, end_date.day)\
                    )
            self.to_date_edit.setDate(end_date)

            self.subject_combo.setCurrentIndex(0)
            self.type_combo.setCurrentIndex(0)
        else:
            self.to_date_edit.setEnabled(False)
            self.from_date_edit.setEnabled(False)

            day_date = QDate(self.planed_date.year, self.planed_date.month, self.planed_date.day)
            self.from_date_edit.setDate(day_date)
            self.to_date_edit.setDate(day_date)

            subject_index = self.subject_index_mapping[self.context.study_subject.subject_id]
            type_index = self.type_index_mapping[self.context.free_work_subject_type_key]

            self.subject_combo.setCurrentIndex(subject_index)
            self.type_combo.setCurrentIndex(type_index)

    @pyqtSlot()
    def move_slot(self):

        """capture parents movement and move dialog accordingly"""

        scale = self.context.scale

        # cover horizontal scrollbar value with the minus sign too
        pos_x = (self.schedule_rect.x() - self.parent.horizontalScrollBar().value()/scale)*scale
        diff_x = pos_x +\
            self.context.schedule_config_box_width -\
                self.parent.width()

        if diff_x > 0:
            pos_x = pos_x - diff_x

        # cover horizontal scrollbar value with the minus sign too
        pos_y = (self.schedule_rect.y() - self.parent.verticalScrollBar().value()/scale)*scale
        diff_y = pos_y +\
            self.context.schedule_config_box_height -\
                self.parent.height()

        if diff_y > 0:
            pos_y = pos_y - diff_y

        pos = self.parent.mapToGlobal(QPoint(int(pos_x), int(pos_y)))
        self.move(int(pos.x() - self.context.time_column_width), int(pos.y()))

    def get_hour_time_diff(self, work_unit_entry):

        """
        return time difference in hours of start time and
        end time for a work unit entry
        """

        start_datetime =\
            (datetime.combine(work_unit_entry.start_date, work_unit_entry.start_time) -\
                timedelta(hours=work_unit_entry.start_offset))
        end_datetime =\
            (datetime.combine(work_unit_entry.end_date, work_unit_entry.end_time) -\
                timedelta(hours=work_unit_entry.start_offset))
        time_diff = round((end_datetime - start_datetime).seconds / 3600.0, 2)

        return time_diff

    @pyqtSlot()
    def delete_time_button_clicked(self):

        """button deletes booked time"""

        dbwrapper.WorkUnitEntry.delete_by_db_id(\
            self.work_unit_entry,\
                self.context.work_day_time_units,\
                    self.context.date_format,\
                        self.context.db_file_name)

        # if some entries have been modified, redraw the schedule entries
        self.communicator.SIGNAL_REDRAW_SCHEDULE_CANVAS.emit()

        # remove select placeholder
        self.communicator.SIGNAL_REMOVE_SELECT_PLACEHOLDER.emit()

        subject_type = self.schedule_rect.subject_type.key()
        if subject_type == self.context.free_work_subject_type_key:
            # update subject work time and the day work time and do that
            # before the total work times!
            # update work time of entry
            self.communicator.SIGNAL_SCHEDULE_ENTRY_WORK_CHANGED.emit(
                self.work_unit_entry.subject_id,\
                    HF.date_2_db(self.work_unit_entry.start_date),\
                        -self.get_hour_time_diff(self.work_unit_entry))
        else:
            # update all total work times (take plus time diff)
            self.communicator.SIGNAL_SCHEDULE_TOTAL_WORK_CHANGED.emit(\
                self.work_unit_entry.subject_id,\
                    HF.date_2_db(self.work_unit_entry.start_date),\
                        -self.get_hour_time_diff(self.work_unit_entry))

        self.close()


    @pyqtSlot()
    def book_button_clicked(self):

        """book time button slot"""

        from_time = self.from_time.time()
        to_time = self.to_time.time()

        work_unit_entry = self.create_booking()
        work_unit_entry.state = 2
        work_unit_entry.start_time = time(from_time.hour(), from_time.minute())
        work_unit_entry.end_time = time(to_time.hour(), to_time.minute())

        # allow booking of normal work time if the block is planed with a
        # specific subject but has type FREE_WORK
        # (allow for planed group work that count's towards the planed mount of
        # time for a subject)
        subject_type = self.schedule_rect.subject_type.key()
        if subject_type == self.context.free_work_subject_type_key:
            work_unit_entry.unit_type = dbwrapper.UnitTypes.WORK_TIME

        dbwrapper.WorkUnitEntry.to_db(\
            work_unit_entry,\
                self.context.work_day_time_units,\
                    self.context.db_file_name)

        # if some entries have been modified, redraw the schedule entries
        self.communicator.SIGNAL_REDRAW_SCHEDULE_CANVAS.emit()

        # remove select placeholder
        self.communicator.SIGNAL_REMOVE_SELECT_PLACEHOLDER.emit()
        
        if subject_type == self.context.free_work_subject_type_key:
            # update subject work time and the day work time and do that
            # before the total work times!
            # update work time of entry
            self.communicator.SIGNAL_SCHEDULE_ENTRY_WORK_CHANGED.emit(
                work_unit_entry.subject_id,\
                    HF.date_2_db(work_unit_entry.start_date),\
                        self.get_hour_time_diff(work_unit_entry))
        else:
            # update all total work times (take plus time diff)
            self.communicator.SIGNAL_SCHEDULE_TOTAL_WORK_CHANGED.emit(\
                work_unit_entry.subject_id,\
                    HF.date_2_db(work_unit_entry.start_date),\
                        self.get_hour_time_diff(work_unit_entry))

        self.close()

    @pyqtSlot()
    def ok_slot(self):

        """ok pushbutton slot"""

        sched_rec = self.schedule_rect

        sched_times = sched_rec.schedule_times

        from_time = 0
        from_date = self.planed_date
        if sched_times.from_hour > 23:
            from_time = time(sched_times.from_hour - 24, sched_times.from_minute)
            from_date = from_date + timedelta(hours=24)

        else:
            from_time = time(sched_times.from_hour, sched_times.from_minute)

        to_time = 0
        to_date = self.planed_date
        # adjust for one minute less than full hour
        if sched_times.to_hour > 23:
            to_time = time(sched_times.to_hour - 24, sched_times.to_minute)
            to_date = to_date + timedelta(hours=24)
        else:
            to_time = time(sched_times.to_hour, sched_times.to_minute)

        # if we want some series, change the from and to date
        if self.scheduled_checkbox.isChecked():
            q_from_date = self.from_date_edit.date()
            q_to_date = self.to_date_edit.date()
            from_date = date(q_from_date.year(), q_from_date.month(), q_from_date.day())
            to_date = date(q_to_date.year(), q_to_date.month(), q_to_date.day())

        if sched_rec.is_new == 1:
            sched_rec.subject = self.subject_combo.currentData()[1]
            sched_rec.subject_type = self.type_combo.currentData()[1]

            series_obj = dbwrapper.ScheduleSeries.new(\
                sched_rec.subject_type.subject_type_id,\
                    sched_rec.subject.subject_id,\
                        from_date,\
                            to_date,\
                                "")

            # use planed date here because it's always the selected date no matter the offset
            sched_rec.schedule_entry = dbwrapper.ScheduleEntry.new(\
                series_obj,\
                    self.context.start_time_offset,\
                        from_time,\
                            to_time,\
                                self.planed_date,\
                                    self.description.text())

            sched_rec.is_new = 0
            dbwrapper.ScheduleEntry.series_to_db(\
                sched_rec.schedule_entry,\
                    self.context.schedule_entries,\
                        self.context.db_file_name)

            self.schedule_rect_list.append(sched_rec)
        else:
            sched_rec.subject = self.subject_combo.currentData()[1]
            sched_rec.subject_type = self.type_combo.currentData()[1]

            sched_rec.schedule_entry.start_offset = self.context.start_time_offset
            sched_rec.schedule_entry.start_time = from_time
            sched_rec.schedule_entry.end_time = to_time
            sched_rec.schedule_entry.description = self.description.text()

            sched_rec.schedule_entry.series_obj.type_id = sched_rec.subject_type.subject_type_id
            sched_rec.schedule_entry.series_obj.subject_id = sched_rec.subject.subject_id
            sched_rec.schedule_entry.series_obj.start_date = from_date
            sched_rec.schedule_entry.series_obj.end_date = to_date

            dbwrapper.ScheduleEntry.update_series_by_series_id(\
                sched_rec.schedule_entry,\
                    self.context.schedule_entries,\
                        self.context.db_file_name)

        # if some entries have been modified, redraw the schedule entries
        self.communicator.SIGNAL_REDRAW_SCHEDULE_CANVAS.emit()

        # remove select placeholder
        self.communicator.SIGNAL_REMOVE_SELECT_PLACEHOLDER.emit()
        self.close()

    @pyqtSlot()
    def cancel_slot(self):

        """cancel pushbutton slot"""

        # remove select placeholder
        self.communicator.SIGNAL_REMOVE_SELECT_PLACEHOLDER.emit()
        self.close()

    @pyqtSlot()
    def delete_slot(self):

        """delete button pressed"""

        # remove entry from db

        dbwrapper.ScheduleEntry.delete_series_by_db_id(\
            self.schedule_rect.schedule_entry,\
                self.context.schedule_entries,\
                    self.context.db_file_name)

        # # remove entry from current list
        del_id = self.schedule_rect.schedule_entry.schedule_entry_id
        del_index = 0
        for i in self.schedule_rect_list:
            if i.schedule_entry.schedule_entry_id == del_id:
                del self.schedule_rect_list[del_index]
                break
            del_index = del_index + 1

        # remove select placeholder
        self.communicator.SIGNAL_REMOVE_SELECT_PLACEHOLDER.emit()

        # if some entries have been modified, redraw the schedule entries
        self.communicator.SIGNAL_REDRAW_SCHEDULE_CANVAS.emit()

        self.close()

class ScheduleTime():

    """bounding times for schedule rect"""

    def __init__(self, day_index, from_hour, from_minute, to_hour, to_minute):
        self.day_index = day_index
        self.from_hour = from_hour
        self.from_minute = from_minute
        self.to_hour = to_hour
        self.to_minute = to_minute

class ScheduleRect():

    """bounding coordinates and size for schedule rect"""

    def __init__(self, x_coord, y_coord, width, height):
        self.x_coord = x_coord
        self.y_coord = y_coord
        self.width = width
        self.height = height

class ScheduleEntryRect(QRect):

    """
    Class represents one schedule box with information in it
    """

    def __init__(self, is_new, select_rect, communicator, context, parent):
        self.context = context
        self.parent = parent
        self.communicator = communicator
        self.is_new = is_new

        self.schedule_rect = self.translate_2_coords(select_rect)
        self.schedule_times = self.translate_2_time(select_rect)

        bb_width = self.context.box_border_width
        super().__init__(\
            self.schedule_rect.x_coord + bb_width,\
                self.schedule_rect.y_coord,\
                    self.schedule_rect.width - bb_width,\
                        self.schedule_rect.height)

        x_coord = self.getRect()[0] + self.context.box_text_margin
        y_coord = self.getRect()[1] + self.context.box_text_margin
        text_width = self.schedule_rect.width - 2*self.context.box_text_margin
        text_height = self.schedule_rect.height - 2*self.context.box_text_margin
        self.text_rect = QRect(x_coord, y_coord, text_width, text_height)

        self.subject = None # db Subject()
        self.subject_type = None # db SubjectType()
        self.schedule_entry = None # db ScheduleEntry()

    def __del__(self):
        pass

    def translate_2_time(self, select_rect):

        """translate select rect boundaries to time coords"""

        minute_height = self.context.minute_height

        day_index = int((select_rect.x()) / self.context.box_width)

        offset = self.context.time_interval *\
            self.context.hour_interval *\
                self.context.start_time_offset

        from_minutes = int((select_rect.y() - self.context.top_offset) /\
            (self.context.box_height/minute_height)) * self.context.time_interval + offset

        to_minutes = int((select_rect.y() + select_rect.height() - self.context.top_offset) /\
            (self.context.box_height/minute_height)) * self.context.time_interval + offset

        from_hour = int(from_minutes / 60)
        from_minute = from_minutes - from_hour*60
        to_hour = int(to_minutes / 60)
        to_minute = to_minutes - to_hour*60

        return ScheduleTime(day_index, from_hour, from_minute, to_hour, to_minute)

    def translate_2_coords(self, select_rect):

        """translate select rect boundaries to coords"""

        x_coord = select_rect.x()
        y_coord = select_rect.y()
        width = self.context.scheduled_box_width
        height = select_rect.height()

        return ScheduleRect(x_coord, y_coord, width, height)

    def assign_db_objects(self, subject, subject_type, schedule_entry):

        """assign db objects that represent one entry"""

        self.subject = subject
        self.subject_type = subject_type
        self.schedule_entry = schedule_entry

    def paint(self, painter, brush):

        """paint rect of entry"""

        # color = self.context.planed_time_color
        color = self.subject.color

        brush.setColor(color)
        painter.fillRect(self, brush)
        painter.drawText(self.text_rect,\
            Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop | Qt.TextFlag.TextWordWrap,\
                self.subject.description + " / " + self.subject_type.name)

    @pyqtSlot()
    def move_slot(self):

        """capture parents movement and move dialog accordingly"""

        geo = self.parent.rect()
        pos = self.parent.mapToGlobal(\
            QPoint(geo.x() + self.schedule_coords.x_coord,\
                geo.y() + self.schedule_coords.y_coord))
        self.move(pos.x(), pos.y())

class ScheduleCanvas(QWidget):

    """
    Class represents the main canvas containing the schedule grid
    """

    def __init__(self, schedule_row_count, communicator, context, parent):
        self.context = context
        self.parent = parent
        super().__init__(parent=parent)
        self.schedule_rects = list()
        self.time_unit_rects = list()
        self.linked_vertical_scrollbars = list()
        self.schedule_row_count = schedule_row_count

        self.move_p = QPoint(0, 0)
        self.clicked_at = False

        self.communicator = communicator
        self.communicator.SIGNAL_ENTRY_RESIZED.connect(self.resize_canvas)
        self.communicator.SIGNAL_DATES_CHANGED.connect(self.update_canvas)
        self.communicator.SIGNAL_REMOVE_SELECT_PLACEHOLDER.connect(\
            self.remove_select_place_holder)
        # TODO: check this one out (redraw schedule without reloading...)
        # self.communicator.SIGNAL_REDRAW_SCHEDULE_CANVAS.connect(self.redraw_schedule_canvas)
        self.communicator.SIGNAL_REDRAW_SCHEDULE_CANVAS.connect(self.update_canvas)

        palette = QPalette()
        palette.setColor(QPalette.ColorRole.Window, self.context.canvas_background_color)
        self.setAutoFillBackground(True)
        self.setPalette(palette)

        # self.setFocusPolicy(Qt.FocusPolicy.WheelFocus)

        self.select_rect = None
        self.select_place_holder = None
        self.grid = None
        self.grid_height = 0
        
        self.parent.setVerticalScrollBarPolicy(context.scrollbar_policy)

        self.create_grid()
        self.create_schedule_entries(True)
        self.resize_canvas()
        self.scroll_value = self.parent.verticalScrollBar().value()

    def __del__(self):
        pass

    def link_vertical_scroll_bar(self, scroll_bar):

        """link a scrollbar to the one of this windows parent"""

        self.linked_vertical_scrollbars.append(scroll_bar)

    @pyqtSlot()
    def redraw_schedule_canvas(self):

        """slot redraws the schedule area without reloading stuff from db"""

        self.select_rect = None
        self.grid = None
        self.grid_height = 0

        self.create_grid()
        self.resize_canvas()
        self.create_schedule_entries(False)
        self.update()

    @pyqtSlot()
    def remove_select_place_holder(self):

        """slot removes the select placeholder"""

        self.select_place_holder = None

    @pyqtSlot()
    def update_canvas(self):

        """update whole window with new information from context"""

        try:
            self.schedule_rects.clear()
            self.time_unit_rects.clear()
            self.select_rect = None
            self.grid = None
            self.grid_height = 0

            self.create_grid()
            self.resize_canvas()
            self.create_schedule_entries(True)
            self.update()
        except: # pylint: disable=bare-except
            with open(self.context.output_file_name, "a") as e_file:
                e_file.write(datetime.today().strftime(self.context.output_date_format) + ": " +\
                    "Unexpected error in ScheduleCanvas.update_canvas")

    @pyqtSlot()
    def resize_canvas(self):

        """resize canvas according to scale"""

        scale = self.context.scale
        height = self.grid_height + self.context.top_offset + self.context.scroll_bar_offset
        self.setFixedSize(int(self.get_width()*scale), int(height*scale))

    def get_width(self):

        """return canvas initial width"""

        return self.context.day_count*self.context.box_width +\
            self.context.scroll_bar_offset

    def get_height(self):

        """return canvas initial window height"""

        return self.context.schedule_height

    def create_schedule_entries(self, reload_from_db):

        """
        load scheduled entries within datepickers date borders and add them to schedule_entries
        load planed entries within datepickers date borders and add them to schedule_entries

        both kind of entries should be able to use the same db stmt, just the rendering is
        different

        add scheduled and planed entries to canvas

        use reload_from_db = True if an entry has only been updated and there is nothing
        new to load
        """

        if reload_from_db:
            # load scheduler units
            dbwrapper.ScheduleEntry.reload_from_db(\
                self.context.schedule_entries,\
                    self.context.start_date,\
                        self.context.end_date,\
                            self.context.db_file_name)

            # load recorded time units
            dbwrapper.WorkDayTimeUnits.get_time_unit_list(\
                self.context.work_day_time_units,\
                    self.context.start_date,\
                        self.context.end_date,\
                            self.context.date_format,\
                                self.context.db_file_name)

        for i in self.context.schedule_entries.values():
            rect = ScheduleEntryRect(0,\
                self.trans_datetime_2_coords(i.at_date, i.start_time, i.end_time),\
                    self.communicator,\
                        self.context,\
                            self)

            if i.series_obj.subject_id == self.context.study_subject.subject_id:
                rect.assign_db_objects(\
                self.context.study_subject,\
                    self.context.subject_types[i.series_obj.type_id],\
                        i)
            else:
                rect.assign_db_objects(\
                    self.context.subjects[i.series_obj.subject_id],\
                        self.context.subject_types[i.series_obj.type_id],\
                            i)
            self.schedule_rects.append(rect)

        for i in self.context.work_day_time_units.values():
            self.time_unit_rects.append(\
                WorkUnitDisplay(i, self.communicator, self.context))

        self.update()

    def create_grid(self):

        """create the canvas grid"""

        width = self.context.day_count*self.context.box_width
        height = self.schedule_row_count*self.context.box_height
        startx = 0
        starty = self.context.top_offset
        intervalx = self.context.box_width
        intervaly = self.context.box_height

        self.grid = CanvasGrid(width, height, startx, starty, intervalx, intervaly, self.context)
        self.grid_height = self.grid.get_height()

    def paintEvent(self, event): # pylint: disable=invalid-name, unused-argument

        """paint the whole main canvas"""

        try:
            r = random.randint(0,100)
            val = self.parent.verticalScrollBar().value()
            for i in self.linked_vertical_scrollbars:
                i.setValue(val)

            painter = QPainter()
            b = painter.begin(self)
            painter.scale(self.context.scale, self.context.scale)
            painter.setPen(Qt.GlobalColor.black)
            brush = QBrush(Qt.GlobalColor.blue)

            self.grid.paint(painter, brush)

            if self.select_rect is not None and self.select_rect.to_repaint():
                self.select_rect.paint(painter, brush)

            if self.select_place_holder is not None:
                brush.setColor(self.context.select_place_holder_color)
                painter.fillRect(self.select_place_holder, brush)

            for i in self.schedule_rects:
                i.paint(painter, brush)

            for i in self.time_unit_rects:
                i.paint(painter, brush)
            res = painter.end()

            if self.scroll_value != val:
                self.update()
            self.scroll_value = val
        except:
            print("weird exception 2")

    def inside_grid(self, x_coord, y_coord):

        """return True if (x_coord, y_coord) is inside the grid area of the canvas"""

        return x_coord > 0 and\
            y_coord > self.context.top_offset and\
                x_coord < (self.get_width() - self.context.scroll_bar_offset) and\
                    y_coord < (self.context.top_offset +\
                        self.grid.get_height())

    def trans_time_2_coords(self, day_index, from_hour, from_minute, to_hour, to_minute):

        """
        translate time parameters to coordinates on canvas
        no need for to_x because the width of a field is given by schedule_box_width
        """

        from_y = ((from_hour - self.context.start_time_offset)*60 +\
            from_minute)*self.context.minute_height + self.context.top_offset

        to_y = ((to_hour - self.context.start_time_offset)*60 +\
            to_minute)*self.context.minute_height + self.context.top_offset

        from_x = day_index*self.context.box_width

        return QRect(from_x, from_y, self.context.scheduled_box_width, to_y - from_y)

    def trans_datetime_2_coords(self, at_date, from_time, to_time):

        """
        translate date and time to coordinates on canvas
        no need for to_x because the width of a field is given by schedule_box_width
        """

        # if a time is smaller than the initial time offset (normally 5 hours)
        # it means we need to add 24 hours to the time to calculate the
        # y coord correctly

        from_hour = from_time.hour
        to_hour = to_time.hour
        from_minute = from_time.minute
        to_minute = to_time.minute

        if from_hour < self.context.start_time_offset:
            from_hour = from_hour + 24

        if to_hour < self.context.start_time_offset:
            to_hour = to_hour + 24

        from_y = ((from_hour - self.context.start_time_offset)*60 +\
            from_minute)*self.context.minute_height + self.context.top_offset

        to_y = ((to_hour - self.context.start_time_offset)*60 +\
            to_minute)*self.context.minute_height + self.context.top_offset

        day_index = (at_date - self.context.start_date).days

        from_x = day_index*self.context.box_width

        return QRect(from_x, from_y, self.context.scheduled_box_width, to_y - from_y)

    def mousePressEvent(self, event): # pylint: disable=invalid-name

        """mouse press event handler, update select_rect"""

        self.clicked_at = True

        x_coord = int(event.pos().x()/self.context.scale)
        y_coord = int(event.pos().y()/self.context.scale)

        self.move_p = QPoint(event.pos().x(), event.pos().y())

        if not self.inside_grid(x_coord, y_coord):
            return
        self.select_rect = SelectRect(x_coord, y_coord, self.context)
        if self.select_rect.to_repaint():
            self.update()

    def mouseMoveEvent(self, event): # pylint: disable=invalid-name

        """mouse move event handler, update select_rect"""

        if not self.clicked_at:
            return

        x_coord = int(event.pos().x()/self.context.scale)
        y_coord = int(event.pos().y()/self.context.scale)

        if not self.inside_grid(x_coord, y_coord) or self.select_rect is None:
            return

        # make scrollbar follow mouse position if pressed
        requested_p = QPoint(event.pos().x(), event.pos().y())
        diff = requested_p.y() - self.move_p.y()
        scroll_b = self.parent.verticalScrollBar()
        max_mouse_value = scroll_b.value() + scroll_b.height()
        min_mouse_value = scroll_b.value()
        # down
        if diff > 0 and requested_p.y() > max_mouse_value:
            delta = requested_p.y() - max_mouse_value
            self.cursor().setPos(self.cursor().pos().x(), self.cursor().pos().y() - delta)
            scroll_b.setValue(scroll_b.value() + self.context.box_height)
        # up
        elif diff < 0 and requested_p.y() < min_mouse_value:
            delta = requested_p.y() - min_mouse_value
            self.cursor().setPos(self.cursor().pos().x(), self.cursor().pos().y() - delta)
            scroll_b.setValue(scroll_b.value() - self.context.box_height)

        self.move_p = requested_p

        self.select_rect.update(y_coord)
        if self.select_rect.to_repaint():
            self.update()

    def mouseReleaseEvent(self, event): # pylint: disable=invalid-name, unused-argument

        """mouse release event handler, update select_rect"""

        self.clicked_at = False

        x_coord = int(event.pos().x()/self.context.scale)
        y_coord = int(event.pos().y()/self.context.scale)

        if not self.inside_grid(x_coord, y_coord) or self.select_rect is None:
            return

        # see if the mouse was released on a rect that already exists
        rect = None
        mouse_point = QPoint(x_coord, y_coord)
        for i in self.schedule_rects:
            if i.contains(mouse_point):
                rect = i

        if rect is None:
            rect = ScheduleEntryRect(1,\
                self.select_rect,\
                    self.communicator,\
                        self.context,\
                            self)

        self.select_place_holder = self.select_rect.adjusted(0, 0, 0, 0)
        ScheduleEntryConfig(rect, self.schedule_rects,\
            self.communicator, self.context, self.parent)

        del self.select_rect
        self.select_rect = None
        self.update()

    def wheelEvent(self, event): # pylint: disable=invalid-name

        """mouse wheel event, update canvas size"""

        if not self.context.keys_pressed["ctrl"]:
            return

        angle = event.angleDelta().y()
        if angle < 0:
            self.context.scale = self.context.scale - self.context.scale_delta
        elif angle > 0:
            self.context.scale = self.context.scale + self.context.scale_delta

        if self.context.scale < self.context.min_scale:
            self.context.scale = self.context.min_scale
            return

        if self.context.scale > self.context.max_scale:
            self.context.scale = self.context.max_scale
            return

        self.communicator.SIGNAL_SCHEDULE_RESIZED.emit()
        self.communicator.SIGNAL_PARENT_RESIZED.emit()
        self.resize_canvas()

    def wheelEvent(self, event):
        super().wheelEvent(event)

    def keyPressEvent(self, event): # pylint: disable=invalid-name

        """keyboard key pressed event"""
        if event.key() == Qt.Key.Key_Control:
            self.context.keys_pressed["ctrl"] = True
        else:
            super().keyPressEvent(event)

    def keyReleaseEvent(self, event): # pylint: disable=invalid-name

        """keyboard key released event"""

        if event.key() == Qt.Key.Key_Control:
            self.context.keys_pressed["ctrl"] = False
        else:
            super().keyReleaseEvent(event)

    def get_selected_rect(self, x_coord, y_coord):

        """do nothing"""
