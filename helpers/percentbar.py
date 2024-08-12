"""
Module offers two PercentBar classes
"""

from PyQt6.QtCore import QRect
from PyQt6.QtCore import Qt

class PercentBarTotal(QRect):

    """
    Class represents the total progress bar
    """

    # pylint: disable=unused-argument
    def __init__(self, x_coord, y_coord, width, height,\
        total_planed, total_worked, planed, worked, total,\
            entry_work_gradient, communicator, context, parent):

        self.total_worked = total_worked
        self.total_planed = total_planed
        self.total = total
        self.context = context
        self.parent = parent
        self.communicator = communicator
        self.entry_work_gradient = entry_work_gradient

        super().__init__(x_coord, y_coord, width, height)

    def paint(self, painter, brush):

        """paint the bars"""

        brush.setColor(Qt.red)
        painter.fillRect(self, brush)

class PercentBar(QRect):

    """
    Class represents one progress bar
    """

    def __init__(self, x_coord, y_coord, width, height,\
        total_planed, total_worked, planed, worked, total,\
            entry_work_gradient, communicator, context, parent):

        self.total_worked = total_worked
        self.total_planed = total_planed
        self.worked = worked
        self.planed = planed
        self.total = total
        self.context = context
        self.parent = parent
        self.communicator = communicator
        self.entry_work_gradient = entry_work_gradient

        bar_width = width - self.context.total_work_width
        super().__init__(\
            x_coord, y_coord, bar_width - self.context.left_offset, height)

        # use max of total planed and worked get the geratest width or one bar
        max_hours = max(total_planed, total_worked)

        bb_width = self.context.box_border_width

        # display worked time in top half and planed time in bottom half
        # put planed and worked times for one subject in perspective with the total
        worked_width = 0
        planed_width = 0
        if max_hours != 0:
            worked_width = int(worked / max_hours * bar_width) - self.context.left_offset
            planed_width = int(planed / max_hours * bar_width) - self.context.left_offset
        worked_height = int(height / 2.0) - 2*bb_width
        planed_height = int(height / 2.0) - 2*bb_width

        # calculate percentage of planed time vs worked time
        self.percent = 0
        if planed == 0:
            if worked > 0:
                self.percent = 100.0
            else:
                self.percent = 0
        else:
            self.percent = 100.0 / planed * worked

        # define two rects for work and planed time
        self.worked_rect = QRect(\
            x_coord, y_coord + bb_width, worked_width, worked_height)
        self.planed_rect = QRect(\
            x_coord, y_coord + worked_height + bb_width, planed_width, planed_height)

        self.top = QRect(\
            x_coord, y_coord, width, bb_width)
        self.bottom = QRect(\
            x_coord, y_coord + height - bb_width, width, bb_width)
        self.top_down = QRect(bar_width, y_coord, bb_width, height)

        self.planed_text_rect = QRect(\
            x_coord + self.context.box_text_margin,\
                y_coord + worked_height, bar_width - self.context.box_text_margin,\
                    worked_height)

        self.worked_text_rect = QRect(\
            x_coord + self.context.box_text_margin,\
                y_coord, bar_width - self.context.box_text_margin, worked_height)

        self.total_text_rect = QRect(\
            x_coord + bar_width - self.context.left_offset + bb_width, y_coord,\
                self.context.total_work_width - self.context.box_text_margin - 2*bb_width,\
                    height)

    def paint(self, painter, brush, total=False): #(self, event): # pylint: disable=invalid-name, unused-argument

        """paint the bars"""

        font = painter.font()
        font.setBold(False)
        painter.setFont(font)

        if total:
            brush.setColor(self.context.canvas_grid_color3)
        else:
            brush.setColor(self.context.canvas_background_color)
        painter.fillRect(self, brush)

        brush.setColor(self.entry_work_gradient.gradient(self.percent))
        painter.fillRect(self.worked_rect, brush)
        painter.drawText(\
            self.worked_text_rect, Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter, str(round(self.worked, 2)))

        if total:
            brush.setColor(self.context.canvas_grid_color4)
        else:
            brush.setColor(self.context.canvas_grid_color3)
        painter.fillRect(self.planed_rect, brush)
        painter.drawText(self.planed_text_rect, Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter, str(self.planed))

        if total:
            brush.setColor(self.context.canvas_background_color)
        else:
            brush.setColor(self.context.canvas_background_color)

        font.setBold(True)
        painter.setFont(font)

        painter.fillRect(self.total_text_rect, brush)
        painter.drawText(\
            self.total_text_rect, Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter, str(round(self.total, 2)))

        if total:
            brush.setColor(self.context.canvas_grid_color3)
        else:
            brush.setColor(self.context.canvas_grid_color1)
        painter.fillRect(self.top, brush)
        painter.fillRect(self.bottom, brush)
        painter.fillRect(self.top_down, brush)
