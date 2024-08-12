"""
Module offers class with format for entry canvas values
"""

class EntryCanvasValues():

    """
    Class offers unified values for EntryCanvas field description
    """

    def __init__(self, total_time, work_time, work_balance, work_percent,\
        gradient_color):

        self.work_time = work_time # for the QLineEdit
        self.total_time = total_time
        self.work_balance = work_balance
        self.work_percent = work_percent
        self.gradient_color = gradient_color
