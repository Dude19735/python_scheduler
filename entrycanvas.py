"""
Module defines a schedule layout with a first column
that shows subjects and a grid where work hours can
be entered
"""

import random
from datetime import timedelta
from PyQt6.QtWidgets import QWidget, QLineEdit, QLabel, QHBoxLayout
from PyQt6.QtGui import QPainter, QBrush, QPalette, QFont
from PyQt6.QtCore import Qt, pyqtSlot
import dbobj.dbwrapper as dbwrapper
from dbobj.helperfunctions import HelperFunctions as HF

from helpers.entrycanvasgrid import EntryCanvasGrid
from helpers.entrycanvasvalues import EntryCanvasValues

class GridEntry(QWidget):

    """
    Class represents one field on the entry grid
    """

    def __init__(self, parent, x_coord, y_coord, width, height,\
        index_tupel, entry, percentage, subject, at_date,\
            entry_work_gradient, communicator, context):

        super().__init__(parent=parent)
        self.context = context
        self.parent = parent
        self.subject = subject
        self.at_date = at_date
        self.communicator = communicator
        self.index_tupel = index_tupel
        self.entry_work_gradient = entry_work_gradient

        self.layout = QHBoxLayout()
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)

        self.entry = entry
        self.percentage = percentage

        # TODO: disable subject entry fields if they are out of date

        self.entry_values = None
        self.calculate_times()
        self.entry_label = QLabel(self.entry_values.work_balance, font=context.font, parent=self)
        self.entry_edit = QLineEdit(self.entry_values.work_time, font=context.font, parent=self)

        background_color = None
        background_color = self.entry_values.gradient_color
        self.total_label = QLabel(self.entry_values.total_time, font=context.font, parent=self)
        font = self.total_label.font()
        font.setBold(True)
        self.total_label.setFont(font)

        self.label_layout = QHBoxLayout()
        self.label_layout.setContentsMargins(0, 0, 0, 0)
        self.label_layout.setSpacing(0)

        self.label_font_size = 8
        self.total_label.setStyleSheet("padding-left: 5px;")
        self.total_label.setAlignment(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft)
        self.entry_label.setStyleSheet("padding-right: 2px;")
        self.entry_label.setAlignment(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignRight)
        self.label_layout.addWidget(self.total_label)
        self.label_layout.addWidget(self.entry_label)
        self.layout.addLayout(self.label_layout)

        self.entry_edit.setStyleSheet("border: 2px solid black; background-color: white")
        self.entry_edit.setFixedSize(0, 0)
        self.entry_edit.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.layout.addWidget(self.entry_edit)

        self.setLayout(self.layout)

        self.base_x_coord = x_coord + self.context.box_border_width
        self.base_y_coord = y_coord + self.context.box_border_width
        self.base_width = width - 2*self.context.box_border_width
        self.base_height = height - 2*self.context.box_border_width

        self.x_coord = 0
        self.y_coord = 0
        self.width = 0
        self.height = 0
        self.set_coordinates()

        self.setFixedSize(self.width, self.height)
        self.move(self.x_coord, self.y_coord)

        palette = QPalette()
        palette.setColor(QPalette.ColorRole.Window, background_color)
        self.setAutoFillBackground(True)
        self.setPalette(palette)

        self.communicator.SIGNAL_PARENT_RESIZED.connect(self.scale)

        self.setFocusPolicy(Qt.FocusPolicy.ClickFocus)

    def __del__(self):
        pass

    def sec_2_hours(self, seconds):

        """transform seconds to hours with decimal places"""

        return round(seconds / 3600.0, 2)

    def set_coordinates(self):

        """set class variables including current global scale"""

        scale = self.context.scale
        self.x_coord = int(self.base_x_coord*scale)
        self.y_coord = int(self.base_y_coord*scale)
        self.width = int(self.base_width*scale)
        self.height = int(self.base_height*scale)
        if self.entry_edit.width() != 0:
            self.entry_edit.setFixedSize(self.width, self.height)
        else:
            self.entry_label.setFixedSize(int(self.width/2), self.height)
            self.total_label.setFixedSize(int(self.width/2), self.height)

    def calculate_times(self):

        """
        calculate work_time, time_diff, total_time_diff and work_percent
        (time_diff, total_time_diff, work_time, work_percent)
        """

        time_diff = ""
        work_percent = -1
        total_time_diff = ""
        if self.percentage is not None:
            if self.percentage.time_diff != 0:
                time_diff = str(round(self.percentage.time_diff, 2))
            if self.percentage.total_time_diff != 0:
                total_time_diff = str(round(self.percentage.total_time_diff, 2))
            if self.percentage.work_percent > 0:
                work_percent = self.percentage.work_percent

        work_time = ""
        if self.entry is not None:
            work_time = str(self.entry.work_time)
        background_color = self.entry_work_gradient.gradient(work_percent)

        work_balance = ""
        if time_diff == "" and work_time != "":
            work_balance = work_time
        if time_diff != "":
            if work_time == "":
                work_balance = time_diff + " / --- "
            else:
                work_balance = time_diff + " / " + work_time

        self.entry_values = EntryCanvasValues(\
            total_time_diff,\
                work_time,\
                    work_balance,\
                        work_percent,\
                            background_color)

    def change_gradient(self):

        """update color gradient depending on registered planed work"""

        # (total_time, work_balance, work_percent)
        self.calculate_times()
        background_color = self.entry_values.gradient_color
        self.total_label.setText(self.entry_values.total_time)
        self.entry_label.setText(self.entry_values.work_balance)

        palette = QPalette()
        palette.setColor(QPalette.ColorRole.Window, background_color)
        self.setAutoFillBackground(True)
        self.setPalette(palette)

        self.update()

    @pyqtSlot()
    def scale(self):

        """scale and move current field according to current scale"""

        self.set_coordinates()
        self.setFixedSize(self.width, self.height)
        self.move(self.x_coord, self.y_coord)
        QFont()
        new_font_total =\
            QFont("MS Shell Dlg 2", int(self.label_font_size*self.context.scale), 10, False)
        new_font_entry =\
            QFont("MS Shell Dlg 2", int(self.label_font_size*self.context.scale))

        self.total_label.setFont(new_font_total)
        self.entry_label.setFont(new_font_entry)
        self.entry_edit.setFont(new_font_entry)
        self.focusOutEvent(None)

    def focus_out_handler(self):

        """pseudo handler to remove focus from a cell"""

        text = self.entry_edit.text()
        self.entry_label.setFixedSize(int(self.width/2), self.height)
        self.total_label.setFixedSize(int(self.width/2), self.height)
        self.entry_edit.setFixedSize(0, 0)

        if self.entry_values.work_time != text:
            if text != "":
                if self.entry is None:
                    self.entry = dbwrapper.SubjectWorkUnit.new(\
                        self.subject.subject_id,\
                            float(text),\
                                self.context.start_of_week,\
                                    self.at_date,\
                                        "")
                    dbwrapper.SubjectWorkUnit.to_db(\
                        self.entry,\
                            self.context.subject_work_units,\
                                self.context.db_file_name)

                    if self.percentage is not None:
                        self.percentage.update_percent(float(text))
                    self.change_gradient()

                    self.communicator.SIGNAL_ENTRY_WORK_PLAN_CHANGED.emit(\
                        self.index_tupel[1], 0.0, float(text))
                    self.communicator.SIGNAL_SUBJECT_WORK_PLAN_CHANGED.emit(\
                        self.subject.subject_id, 0.0, float(text))
                else:
                    old_work_time = self.entry.work_time
                    self.entry.work_time = float(text)

                    if self.percentage is not None:
                        self.percentage.update_percent(float(text))
                    self.change_gradient()

                    self.communicator.SIGNAL_ENTRY_WORK_PLAN_CHANGED.emit(\
                        self.index_tupel[1], old_work_time, float(text))
                    self.communicator.SIGNAL_SUBJECT_WORK_PLAN_CHANGED.emit(\
                        self.subject.subject_id, old_work_time, float(text))

                    dbwrapper.SubjectWorkUnit.update_by_db_id(self.entry,\
                        self.context.db_file_name)
            else:
                if self.entry is None:
                    pass # do nothing
                else:
                    old_work_time = self.entry.work_time
                    dbwrapper.SubjectWorkUnit.delete_by_db_id(\
                        self.entry,\
                            self.context.subject_work_units,\
                                self.context.db_file_name)
                    self.entry = None

                    if self.percentage is not None:
                        self.percentage.update_percent(0.0)
                    self.change_gradient()

                    self.communicator.SIGNAL_ENTRY_WORK_PLAN_CHANGED.emit(\
                        self.index_tupel[1], old_work_time, 0.0)
                    self.communicator.SIGNAL_SUBJECT_WORK_PLAN_CHANGED.emit(\
                        self.subject.subject_id, old_work_time, 0.0)

        self.calculate_times()
        self.entry_label.setText(self.entry_values.work_balance)

    def focusInEvent(self, event): # pylint: disable=invalid-name, unused-argument

        """field has lost focus event handler"""

        # if something was selected before, remove focus from that
        if self.parent.last_index_tupel != (-1, -1):
            self.parent.entry_boxes[self.parent.last_index_tupel].focus_out_handler()

        self.entry_edit.setFocus()
        self.entry_edit.setText(self.entry_values.work_time)
        self.entry_label.setFixedSize(0, 0)
        self.total_label.setFixedSize(0, 0)
        self.entry_edit.setFixedSize(self.width, self.height)
        self.entry_edit.selectAll()
        self.parent.last_index_tupel = self.index_tupel
        self.parent.focusInEvent(event)

    def keyPressEvent(self, event): # pylint: disable=invalid-name

        """capture the keyboard input event"""

        return_keys = (Qt.Key.Key_Enter, Qt.Key.Key_Return, Qt.Key.Key_Escape,\
            Qt.Key.Key_Down, Qt.Key.Key_Left, Qt.Key.Key_Right, Qt.Key.Key_Up)
        key = event.key()
        if key == Qt.Key.Key_Control:
            super().keyPressEvent(event)
            return
        if key in return_keys:
            self.focus_out_handler()
            self.parent.keyPressEvent(event)
            return
        if key == Qt.Key.Key_Alt:
            self.parent.keyPressEvent(event)
        self.entry_edit.keyPressEvent(event)

class EntryCanvas(QWidget):

    """
    Class represents one canvas with a grid where
    each field is editable except for the first column
    which shows subjects
    """

    def __init__(self, entry_work_gradient, subject_entry_communicator,\
        communicator, context, parent):

        super().__init__()
        self.context = context
        self.parent = parent
        self.subject_entry_communicator = subject_entry_communicator
        self.entry_work_gradient = entry_work_gradient

        self.communicator = communicator
        self.communicator.SIGNAL_SCHEDULE_RESIZED.connect(self.resize_canvas)
        self.communicator.SIGNAL_SUBJECT_ENTRY_COMM_UPDATED.connect(self.update_canvas)
        self.communicator.SIGNAL_REDRAW_ENTRY_CANVAS.connect(self.update_canvas)
        self.communicator.SIGNAL_SCHEDULE_TOTAL_WORK_CHANGED.connect(self.update_canvas_entry)
        self.communicator.SIGNAL_SCHEDULE_ENTRY_WORK_CHANGED.connect(self.entry_work_time_changed)

        palette = QPalette()
        palette.setColor(QPalette.ColorRole.Window, self.context.canvas_background_color)
        self.setAutoFillBackground(True)
        self.setPalette(palette)

        # self.setFocusPolicy(Qt.FocusPolicy.WheelFocus)

        self.select_rect = None
        self.entry_boxes = self.init_entry_boxes()
        self.grid = None
        self.linked_scrollbars = list()
        self.linked_vertical_scrollbars = list()
        self.grid_height = 0
        self.last_index_tupel = (-1, -1)

        self.subject_index_mapping = dict()
        self.date_index_mapping = dict()

        self.parent.setVerticalScrollBarPolicy(context.scrollbar_policy)

        self.create_subject_grid()
        self.resize_canvas()

        self.v_scroll_value = self.parent.verticalScrollBar().value()
        self.h_scroll_value = self.parent.horizontalScrollBar().value()

    def init_entry_boxes(self):

        """return empty dict to init entry_boxes"""

        return dict()

    def __del__(self):
        pass

    @pyqtSlot()
    def update_canvas(self):

        """update entire canvas using new context data"""

        children = self.findChildren(QWidget)
        for i in children:
            i.setParent(None)

        for i in self.entry_boxes.values():
            i.setParent(None)

        self.entry_boxes = self.init_entry_boxes()
        self.grid = None
        self.grid_height = self.subject_entry_communicator.grid_height

        self.create_subject_grid()
        self.resize_canvas()
        self.update()

    @pyqtSlot(int, int, float)
    def update_canvas_entry(self, subject_id, db_date, time_diff):

        """update one canvas entry, add new time diff to total time"""

        subject_index = self.subject_index_mapping[subject_id]
        date_index = self.date_index_mapping[db_date]
        key = (subject_index, date_index)

        # this one must be there
        entry = self.entry_boxes[key]

        old_time_diff = 0
        new_time_diff = time_diff
        # but it may be that there is no percentage_obj associated with it
        if entry.percentage is None:
            obj = dbwrapper.WorkDaySubjectTimePercentage.new(\
                subject_id,\
                    self.context.start_date,\
                        HF.date_2_python_date(db_date),\
                            0,\
                                0,\
                                    time_diff)
            self.context.subject_work_percentage[obj.key()] = obj
            entry.percentage = obj
        else:
            old_time_diff = entry.percentage.total_time_diff
            new_time_diff = entry.percentage.total_time_diff + time_diff
            entry.percentage.total_time_diff =\
                entry.percentage.total_time_diff + time_diff
            entry.percentage.update_percent(entry.percentage.work_time)

        entry.calculate_times()
        entry.change_gradient()

        self.communicator.SIGNAL_ENTRY_TOTAL_WORK_CHANGED.emit(date_index, time_diff)
        self.communicator.SIGNAL_SUBJECT_TOTAL_WORK_CHANGED.emit(\
            subject_id, old_time_diff, new_time_diff)

    @ pyqtSlot(int, int, float)
    def entry_work_time_changed(self, subject_id, db_date, time_diff):

        """update the work time for one specific entry"""

        subject_index = self.subject_index_mapping[subject_id]
        date_index = self.date_index_mapping[db_date]
        key = (subject_index, date_index)

        # this one must be there
        entry = self.entry_boxes[key]

        old_time_diff = 0
        new_time_diff = time_diff
        # but it may be that there is no percentage_obj associated with it
        if entry.percentage is None:
            obj = dbwrapper.WorkDaySubjectTimePercentage.new(\
                subject_id,\
                    self.context.start_date,\
                        HF.date_2_python_date(db_date),\
                            time_diff,\
                                0,\
                                    time_diff)
            self.context.subject_work_percentage[obj.key()] = obj
            entry.percentage = obj
        else:
            old_time_diff = entry.percentage.time_diff
            new_time_diff = entry.percentage.time_diff + time_diff
            entry.percentage.time_diff =\
                entry.percentage.time_diff + time_diff

            old_time_diff = entry.percentage.total_time_diff
            new_time_diff = entry.percentage.total_time_diff + time_diff
            entry.percentage.total_time_diff =\
                entry.percentage.total_time_diff + time_diff

            entry.percentage.update_percent(entry.percentage.work_time)

        entry.calculate_times()
        entry.change_gradient()

        self.communicator.SIGNAL_ENTRY_WORK_TIME_CHANGED.emit(\
            date_index, time_diff)

        self.communicator.SIGNAL_SUBJECT_WORK_TIME_CHANGED.emit(\
            subject_id, time_diff)

    @ pyqtSlot(int, float)
    def day_work_time_changed(self, db_date, time_diff):

        """update the work time for one day"""

    def get_width(self):

        """get width of entry canvas"""

        return self.context.width

    def get_height(self):

        """get initial height of canvas (only used at init time)"""

        return self.context.entry_height

    @pyqtSlot()
    def resize_canvas(self):

        """resize canvas according to scale"""

        width = self.context.day_count*self.context.box_width + self.context.scroll_bar_offset
        height = self.grid_height + self.context.top_offset + self.context.scroll_bar_offset
        self.setFixedSize(int(width*self.context.scale), int(height*self.context.scale))

    def create_subject_grid(self):

        """
        create grid for entry canvas
        must be called AFTER subject boxes have been created and painted for the first time
        """

        self.context.subject_work_percentage.clear()
        self.context.subject_work_units.clear()

        start_x = 0
        width = self.context.day_count*self.context.box_width
        interval_x = self.context.box_width

        start_y = self.context.top_offset
        height = self.grid_height

        self.grid = EntryCanvasGrid(self.context, width, height, 0, self.context.top_offset)
        for x_coord in range(start_x, int(width + interval_x/2), interval_x):
            self.grid.add_vertical_line(x_coord)

        # load grid subject work units from db
        dbwrapper.SubjectWorkUnit.reload_from_db(\
            self.context.subject_work_units,\
                self.context.start_date,\
                    self.context.end_date,\
                        self.context.db_file_name)

        # load grid subject work percentages from db
        dbwrapper.WorkDaySubjectTimePercentage.get_work_day_subject_time_percentage(\
            self.context.subject_work_percentage,\
                self.context.start_date,\
                    self.context.end_date,\
                        self.context.db_file_name)

        y_coord = start_y
        self.grid.add_horizontal_line(y_coord)
        date_index = 0
        subject_index = 0
        # register index mappings
        s_date = self.context.start_date
        for x_coord in range(start_x, width, interval_x):
            self.date_index_mapping[\
                HF.date_2_db(s_date + timedelta(days=date_index))] = date_index
            date_index = date_index + 1
        for i in self.subject_entry_communicator.subject_boxes:
            self.subject_index_mapping[i.subject.subject_id] = subject_index
            subject_index = subject_index + 1

        date_index = 0
        subject_index = 0
        for i in self.subject_entry_communicator.subject_boxes:
            date_index = 0
            for x_coord in range(start_x, width, interval_x):
                entry_obj = None
                percentage_obj = None
                key = (i.subject.subject_id, date_index)
                if key in self.context.subject_work_units:
                    entry_obj = self.context.subject_work_units[key]
                if key in self.context.subject_work_percentage:
                    percentage_obj = self.context.subject_work_percentage[key]

                c_date = s_date + timedelta(days=date_index)
                entry = GridEntry(self, x_coord, y_coord,\
                    self.context.box_width, i.get_height(),\
                        (subject_index, date_index),\
                            entry_obj,\
                                percentage_obj,\
                                    i.subject,\
                                        c_date,\
                                            self.entry_work_gradient,\
                                                self.communicator,\
                                                    self.context)
                entry.show()
                self.entry_boxes[(subject_index, date_index)] = entry
                date_index = date_index + 1
            subject_index = subject_index + 1
            date_index = 0

            y_coord = y_coord + i.get_height()
            self.grid.add_horizontal_line(y_coord)

    def link_scroll_bar(self, scroll_bar):

        """link a scrollbar to the one of this windows parent"""

        self.linked_scrollbars.append(scroll_bar)

    def link_vertical_scroll_bar(self, scroll_bar):

        """link a scrollbar to the one of this windows parent"""

        self.linked_vertical_scrollbars.append(scroll_bar)

    def paintEvent(self, event): # pylint: disable=invalid-name, unused-argument

        """paint the entry canvas"""

        try:
            hval = self.parent.horizontalScrollBar().value()
            for i in self.linked_scrollbars:
                i.setValue(hval)

            vval = self.parent.verticalScrollBar().value()
            for i in self.linked_vertical_scrollbars:
                i.setValue(vval)

            painter = QPainter(self)
            painter.scale(self.context.scale, self.context.scale)
            painter.setPen(Qt.GlobalColor.white)
            brush = QBrush(Qt.GlobalColor.white)

            self.grid.paint(painter, brush)

            res = painter.end()

            if self.v_scroll_value != vval or self.h_scroll_value != hval:
                self.update()
                
            self.v_scroll_value = vval
            self.h_scroll_value = hval
        except:
            print("weird exception 1")

    def inside_grid(self, x_coord, y_coord):

        """return True if (x_coord, y_coord) is inside the grid area of the canvas"""

        return x_coord > (self.context.left_offset + self.context.time_column_width) and\
            y_coord > self.context.top_offset and\
                x_coord < (self.context.width - self.context.scroll_bar_offset) and\
                    y_coord < (self.context.top_offset + self.grid_height)

    def wheelEvent(self, event): # pylint: disable=invalid-name

        """mouse wheel event, update canvas size"""

        if not self.context.keys_pressed["ctrl"]:
            super().wheelEvent(event)
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

        self.communicator.SIGNAL_ENTRY_RESIZED.emit()
        self.communicator.SIGNAL_PARENT_RESIZED.emit()
        self.resize_canvas()

    def keyPressEvent(self, event): # pylint: disable=invalid-name

        """keyboard key pressed event"""

        key = event.key()
        li_tupel = self.last_index_tupel
        if key == Qt.Key.Key_Control:
            self.context.keys_pressed["ctrl"] = True
        elif key == Qt.Key.Key_Alt:
            self.context.keys_pressed["alt"] = True
        elif li_tupel != (-1, -1):
            if key in (Qt.Key.Key_Enter, Qt.Key.Key_Return):
                new_key = (li_tupel[0] + 1, li_tupel[1])
                self.focus_next_entry(new_key)
            elif key == Qt.Key.Key_Left and self.context.keys_pressed["alt"]:
                new_key = (li_tupel[0], li_tupel[1] - 1)
                self.focus_next_entry(new_key)
            elif key == Qt.Key.Key_Right and self.context.keys_pressed["alt"]:
                new_key = (li_tupel[0], li_tupel[1] + 1)
                self.focus_next_entry(new_key)
            elif key == Qt.Key.Key_Up and self.context.keys_pressed["alt"]:
                new_key = (li_tupel[0] - 1, li_tupel[1])
                self.focus_next_entry(new_key)
            elif key == Qt.Key.Key_Down and self.context.keys_pressed["alt"]:
                new_key = (li_tupel[0] + 1, li_tupel[1])
                self.focus_next_entry(new_key)
            elif key == Qt.Key.Key_Escape:
                self.last_index_tupel = (-1, -1)
                self.setFocus()
        else:
            super().keyPressEvent(event)

    def focus_next_entry(self, new_key):

        """get entry to focus on"""

        if new_key in self.entry_boxes.keys():
            n_entry = self.entry_boxes[new_key]
            n_entry.focusInEvent(None)

            v_scroll = self.parent.verticalScrollBar()
            h_scroll = self.parent.horizontalScrollBar()

            min_y_val = v_scroll.value()
            max_y_val = v_scroll.value() + v_scroll.height()
            min_x_val = h_scroll.value()
            max_x_val = h_scroll.value() + self.parent.width() - self.context.scroll_bar_offset

            requested_min_x = n_entry.pos().x()
            requested_max_x = n_entry.pos().x() + n_entry.width
            requested_min_y = n_entry.pos().y()
            requested_max_y = n_entry.pos().y() + n_entry.height

            # move left
            if requested_min_x < min_x_val:
                self.communicator.SIGNAL_SCROLLBAR_CHANGE_REQUIRED.emit(\
                    requested_min_x - min_x_val, self)
            # move right
            elif requested_max_x > max_x_val:
                self.communicator.SIGNAL_SCROLLBAR_CHANGE_REQUIRED.emit(\
                    requested_max_x - max_x_val, self)
            # move up
            elif requested_min_y < min_y_val:
                v_scroll.setValue(v_scroll.value() + (requested_min_y - min_y_val))
            # move down
            elif requested_max_y > max_y_val:
                v_scroll.setValue(v_scroll.value() + (requested_max_y - max_y_val))

    def keyReleaseEvent(self, event): # pylint: disable=invalid-name

        """keyboard key released event"""

        if event.key() == Qt.Key.Key_Control:
            self.context.keys_pressed["ctrl"] = False
        elif event.key() == Qt.Key.Key_Alt:
            self.context.keys_pressed["alt"] = False
        else:
            super().keyReleaseEvent(event)
