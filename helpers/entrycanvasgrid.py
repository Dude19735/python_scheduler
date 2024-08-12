"""
Module represents grid of entry canvas and subject canvas
"""

from PyQt6.QtCore import QRect

class EntryCanvasGrid():

    """
    Class represents the grid that can be edited
    """

    def __init__(self, context, width, height, start_x, start_y):
        self.context = context
        self.v_grid = []
        self.h_grid = []
        self.width = width
        self.height = height
        self.start_x = start_x
        self.start_y = start_y

    def add_horizontal_line(self, y_coord):

        """add one horizontal line"""

        self.h_grid.append(QRect(\
            self.start_x,\
                y_coord - self.context.box_border_width,\
                    self.width,\
                        2*self.context.box_border_width\
                            ))

    def add_vertical_line(self, x_coord):

        """add one vertical line"""

        self.v_grid.append(QRect(\
            x_coord - self.context.box_border_width,\
                self.start_y,\
                    2*self.context.box_border_width,\
                        self.height\
                            ))

    def paint(self, painter, brush):

        """paint the grid"""

        brush.setColor(self.context.canvas_grid_color1)
        for i in self.v_grid:
            painter.fillRect(i, brush)
        for i in self.h_grid:
            painter.fillRect(i, brush)
