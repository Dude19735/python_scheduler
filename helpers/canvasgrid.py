"""
Module offers grid for schedule canvas

This is a helper class that is shared between the timescanvas and the
schedulecanvas
"""

from PyQt6.QtCore import QRect

class CanvasGrid():

    """
    Class represents the grid that can be edited
    """

    def __init__(self, width, height, startx, starty, intervalx, intervaly, context):
        self.height = height
        self.width = width
        self.startx = startx
        self.starty = starty
        self.intervalx = intervalx
        self.intervaly = intervaly
        self.context = context

        self.v_grid = []
        for x_coord in range(self.startx, int(self.width + self.intervalx/2), self.intervalx):
            self.v_grid.append(QRect(\
                x_coord-self.context.box_border_width,\
                    self.context.top_offset,\
                        2*self.context.box_border_width,\
                            self.height\
                            ))

        self.h_grid = []
        for y_coord in range(self.starty, int(self.height + self.intervaly/2), self.intervaly): # pylint: disable=line-too-long
            self.h_grid.append(QRect(\
                startx,\
                    y_coord-self.context.box_border_width,\
                        self.width,\
                            2*self.context.box_border_width\
                                ))

        self.context.grid_height = (len(self.h_grid)-1)*self.context.box_height

    def __del__(self):
        pass

    def get_height(self):

        """return height of whole grid"""

        return self.height

    def paint(self, painter, brush):

        """Paint methode"""

        brush.setColor(self.context.canvas_grid_color1)
        for i in self.v_grid:
            painter.fillRect(i, brush)
        height = 0
        for i in self.h_grid:
            if height%self.context.hour_interval == 0:
                brush.setColor(self.context.canvas_grid_color2)
                painter.fillRect(i, brush)
                brush.setColor(self.context.canvas_grid_color1)
            else:
                painter.fillRect(i, brush)
            height = height+1
