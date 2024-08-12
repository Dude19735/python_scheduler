"""
Module offers unified color gradient to color work percentages
"""

from PyQt6.QtGui import QColor

class EntryWorkGradient():

    """
    Class represents structure to implement unified gradients
    to color the cells containing work hours
    """

    def __init__(self, context):
        self.context = context

    def gradient(self, percentage):

        """return QColor with percentage gradient"""

        if percentage < 0:
            return QColor(255, 255, 255, self.context.a_255)

        if percentage > 100:
            percentage = 100

        index = int(percentage//(100/(len(self.context.r_part)-1)))
        return QColor(\
            self.context.r_part[index],\
                self.context.g_part[index],\
                    self.context.b_part[index],\
                        self.context.a_90)
