"""
Module offers subject boxes for entry canvas
"""

import math
import random
from PyQt6.QtWidgets import QWidget
from PyQt6.QtGui import QPainter, QBrush, QPalette
from PyQt6.QtCore import Qt, QRect, pyqtSlot

from helpers.entrycanvasgrid import EntryCanvasGrid

import dbobj.dbwrapper as dbwrapper

class SubjectBox(QRect):

    """
    Class represents one box containing one subject and it's properties
    """

    def __init__(self, subject, x_coord, y_coord, width, height, font_metrics_width, context):

        self.subject = subject
        self.context = context
        self.text_rect = None

        text_width = self.context.time_column_width - 2*self.context.box_text_margin
        factor = math.ceil(font_metrics_width / text_width)
        height = int(math.ceil(self.context.box_height*max(2, factor)))

        super().__init__(x_coord + self.context.box_border_width,\
            y_coord + self.context.box_border_width,\
                width - 2*self.context.box_border_width,\
                    height)

        x_coord = self.getRect()[0] + self.context.box_text_margin
        y_coord = self.getRect()[1]

        self.text_rect = QRect(x_coord, y_coord, text_width, height)

    def __del__(self):
        pass

    def paint(self, painter, brush):

        """paint the subject box"""

        painter.setPen(Qt.GlobalColor.black)
        brush.setColor(self.context.subject_box_background_color)
        painter.fillRect(self, brush)
        painter.drawText(self.text_rect,\
            Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter | Qt.TextFlag.TextWordWrap,\
                self.subject.description)

    def get_height(self):

        """
        return real height of box after painting
        may be different from initial height because of thext
        """

        return self.getRect()[3] + 2*self.context.box_border_width

    def reset_position(self, y_coord):

        """
        reset y-coord and height to accomodate text space requirements
        of previous subject boxes
        """

        self.setY(y_coord + self.context.box_border_width)

    def get_subject(self):

        """get linked subject"""

        return self.subject

class SubjectCanvas(QWidget):

    """
    Class represents subject boxes for all valid subjects
    """

    def __init__(self, subject_entry_communicator, communicator, context, parent):
        super().__init__(parent=parent)
        self.parent = parent
        self.communicator = communicator
        self.context = context
        self.subject_entry_communicator = subject_entry_communicator

        self.communicator.SIGNAL_SCHEDULE_RESIZED.connect(self.resize_canvas)
        self.communicator.SIGNAL_ENTRY_RESIZED.connect(self.resize_canvas)
        self.communicator.SIGNAL_DATES_CHANGED.connect(self.update_canvas)

        self.subject_boxes = list()
        self.linked_vertical_scrollbars = list()

        palette = QPalette()
        palette.setColor(QPalette.ColorRole.Window, self.context.canvas_background_color)
        self.setAutoFillBackground(True)
        self.setPalette(palette)

        self.grid = None
        self.grid_height = 0

        self.create_subject_fields()
        self.resize_canvas()

        self.scroll_value = self.parent.verticalScrollBar().value()

    def update_canvas(self):

        """update canvas"""

        self.subject_boxes = list()
        self.grid = None
        self.grid_height = 0
        self.create_subject_fields()
        self.resize_canvas()

    def get_subjects(self):

        """get subjects list"""

        return self.subject_boxes

    def create_subject_fields(self):

        """create first column containing all subject fields"""

        width = self.context.time_column_width
        height = self.grid_height
        start_x = self.context.left_offset
        start_y = self.context.top_offset
        interval_x = int(self.context.time_column_width/2)
        # interval_y = self.context.box_height

        self.grid = EntryCanvasGrid(self.context, width, height, start_x, start_y)
        for x_coord in range(start_x, int(width + interval_x/2), interval_x):
            self.grid.add_vertical_line(x_coord)

        dbwrapper.Subject.reload_from_db(\
            self.context.subjects,\
                dbwrapper.SubjectTypes.SUBJECT_TYPE,\
                    1,\
                        self.context.db_file_name)

        width = self.context.time_column_width
        line_height = self.context.box_height
        x_coord = self.context.left_offset
        y_coord = self.context.top_offset
        grid_height = 0

        self.grid.add_horizontal_line(y_coord)
        for sub in self.context.subjects.values():

            # if the current subject is not within the range of the chosen dates, leave them out
            if not (self.context.start_date <= sub.end_date\
                and self.context.end_date >= sub.start_date):
                continue

            # get width of text based on newlines and stuff
            split_description = sub.description.split()
            font_width = 0
            font_width_sentinel = 0
            line_width = self.context.time_column_width - 2*self.context.box_text_margin
            for split_desc in split_description:
                font_width_i = self.fontMetrics().horizontalAdvance(split_desc)

                if font_width_sentinel + font_width_i > line_width:
                    font_width = font_width + (line_width - font_width_sentinel) + font_width_i
                else:
                    font_width = font_width + font_width_i

                font_width_sentinel = font_width_i

            #font_width = self.fontMetrics().width(sub.description)
            box = SubjectBox(sub, x_coord, y_coord, width, line_height, font_width, self.context)
            y_coord = y_coord + box.get_height()
            self.subject_boxes.append(box)
            grid_height = grid_height + box.get_height()
            self.grid.add_horizontal_line(y_coord)

        self.grid_height = grid_height
        self.subject_entry_communicator.grid_height = grid_height
        self.subject_entry_communicator.subject_boxes = self.subject_boxes
        self.communicator.SIGNAL_SUBJECT_ENTRY_COMM_UPDATED.emit()

    def paintEvent(self, event): # pylint: disable=invalid-name, unused-argument

        """paint event for container widget"""

        try:
            val = self.parent.verticalScrollBar().value()
            for i in self.linked_vertical_scrollbars:
                i.setValue(val)

            painter = QPainter(self)
            painter.scale(self.context.scale, self.context.scale)
            painter.setPen(Qt.GlobalColor.black)
            brush = QBrush(Qt.GlobalColor.blue)

            y_coord = self.context.top_offset
            height = 0
            for i in self.subject_boxes:
                i.reset_position(y_coord)
                i.paint(painter, brush)
                y_coord = y_coord + i.get_height()
                height = height + i.get_height()

            self.grid.paint(painter, brush)

            res = painter.end()

            if self.scroll_value != val:
                self.update()

            self.scroll_value = val
        except:
            print("weird exception 3")

    def link_vertical_scroll_bar(self, scroll_bar):

        """link a scrollbar to the one of this windows parent"""

        self.linked_vertical_scrollbars.append(scroll_bar)

    @pyqtSlot()
    def resize_canvas(self):

        """resize canvas according to scale"""

        scale = self.context.scale
        width = self.context.left_offset + self.context.time_column_width
        height = self.grid_height + self.context.top_offset + self.context.scroll_bar_offset
        self.setFixedSize(int(width*scale), int(height*scale))

        self.parent.setFixedWidth(int(width*scale))
