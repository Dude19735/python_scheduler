"""
Module contains diverse helper functions for db
"""

from datetime import date, time
from PyQt6.QtGui import QColor

class HelperFunctions():

    """
    Class contains multiple static helper functions
    """

    @staticmethod
    def escape_quote(str_content):

        """replace single quotes (') with two single quotes ('')"""

        return str_content.replace("'", "''")

    # helper functions for store and load operations
    @staticmethod
    def color_2_db_string(qt_color):

        """expects a QColor object and transforms it to a color string"""

        return "{0},{1},{2},{3}".format(\
            str(qt_color.red()),\
                str(qt_color.green()),\
                    str(qt_color.blue()),\
                        str(qt_color.alpha()))

    @staticmethod
    def color_db_string_2_q_color(color_str):

        """expects a db formated color string and transforms it to a QColor"""

        colors = color_str.split(",")
        return QColor(\
            int(colors[0]),\
                int(colors[1]),\
                    int(colors[2]),\
                        int(colors[3]))

    @staticmethod
    def date_2_db(python_date):

        """
        transform a python date object to a date integer for the db
        format: YYYYMMDD (ie. 20191001 for 01.10.2019)
        """

        return python_date.year*10000 + python_date.month*100 + python_date.day

    @staticmethod
    def date_2_python_date(date_value):

        """transform a db date string to a python date object"""

        year = date_value // 10000
        temp = date_value - year*10000
        month = temp // 100
        day = temp - month*100

        return date(year, month, day)

    @staticmethod
    def time_2_db(python_time):

        """
        transform a python time object to a time integer for the db
        format: HHMM (ie. 1412 for 14:12)
        """

        return python_time.hour*100 + python_time.minute

    @staticmethod
    def time_2_python_time(time_value):

        """transform a db time value to a python time object"""

        hours = time_value // 100
        minutes = time_value - hours*100

        return time(hours, minutes)
