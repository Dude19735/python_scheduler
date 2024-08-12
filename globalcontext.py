"""
This module provides a central context class for all to use
"""

from sys import platform as os_type
from datetime import datetime, timedelta
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor
from PyQt6.QtGui import QFont

class GlobalContext:
    """
    Class contains context for whole canvas
    """

    def __init__(self):

        # scale of canvas display
        self.scale = 1.0
        self.max_scale = 3.0
        self.min_scale = 0.1
        self.scale_delta = 0.1

        # these are used to set an initial window width and height
        # if the user expands the timer to show the whole schedule
        self.initial_window_width = 1360
        self.initial_window_height = 740

        # show schedule widget by default
        self.show_schedule_widget_at_startup = True

        # amount of pixels to scroll with pressed mouse in widgets
        self.scroll_delta = 3

        # output file, really only thought as unsynchronized log
        self.output_file_name = "output.txt"
        self.output_date_format = "%d.%m.%Y %H:%M:%S.%f"

        # dictionary of pressed keys
        self.keys_pressed = dict()
        self.keys_pressed["ctrl"] = False
        self.keys_pressed["alt"] = False

        # initial height and width of entry and schedule canvas
        # these parameters are used to calculate some initial sizes
        # changing these will not really affect anything except that it might
        # distort some of the representations of things
        self.width = 1024 # don't change this one!
        self.height = 800 # don't change this one!
        self.schedule_height = 600 # don't change this one!
        self.entry_height = self.height - self.schedule_height # don't change this one!

        # date picker size parameters
        self.date_picker_head_height = 25

        # set initial day count to 7 to cover a week
        self.day_count = 7
        self.date_list = list()
        self.current_date = datetime.now().date()
        self.start_of_week = self.current_date - timedelta(days=self.current_date.weekday())
        self.start_date = self.start_of_week
        self.end_date = self.start_of_week + timedelta(days=6) # monday + 6 = sunday

        # height of one minute in pixel
        self.minute_height = 1

        # height of one row in minutes (real height is minTimeInterval*minuteHeight
        self.time_interval = 15

        # how many time intervals sum up to 1 hour
        self.hour_interval = int(60/self.time_interval)

        # general date format
        self.date_format = "%d.%m.%Y"

        # grid is shown from 5am current day to 5am exclusively next day => 4:59
        self.start_time_offset = 5
        self.stop_time_offset = 5

        # starting x and y coordinate
        self.top_offset = 5
        self.left_offset = 5

        # height of the head bar with the dates
        self.head_bar_height = 25

        # add something to the surface of the widget to account for a scrollbar
        self.scroll_bar_offset = 20

        # with of column with indicated indicated 'hh:mm - hh:mm' time string
        self.time_column_width = 100

        # left margin for boxes containing text where the text is not centered
        self.box_text_margin = 5

        # width of box containing total work hours for one subject in the percent window
        self.total_work_width = 50

        # grid box width and height (use the initial day_count as reference for width)
        # pylint: disable=line-too-long
        self.box_width = int((self.width - self.time_column_width - self.scroll_bar_offset) / self.day_count)
        self.box_height = int(self.minute_height*self.time_interval)
        self.scheduled_box_width = self.time_column_width
        self.planed_box_width = self.box_width - self.scheduled_box_width
        self.time_unit_rect_subject_width = 5

        # width of the border of one grid box
        self.box_border_width = 1

        # width of schedule canvas config box
        self.schedule_config_box_width = self.time_column_width + self.box_width
        self.schedule_config_box_height = int(self.schedule_config_box_width*1.3)

        # all color definitions
        self.a_90 = 90
        self.a_150 = 150
        self.a_255 = 255
        self.time_box_background_color = QColor(240, 240, 240, self.a_150)
        self.subject_box_background_color = QColor(240, 240, 240, self.a_150)
        self.bottom_row_background_color = Qt.GlobalColor.red
        self.canvas_background_color = Qt.GlobalColor.white
        self.canvas_grid_color1 = QColor(240, 240, 240, self.a_255)
        self.canvas_grid_color2 = QColor(200, 200, 200, self.a_255)
        self.canvas_grid_color3 = QColor(180, 180, 180, self.a_255)
        self.canvas_grid_color4 = QColor(93, 90, 88, self.a_255)
        self.select_rect_color = QColor(180, 180, 180, self.a_150)
        self.select_place_holder_color = QColor(180, 180, 180, self.a_150)
        self.head_bar_color = QColor(200, 200, 200, self.a_255)
        self.head_bar_color_sunday = QColor(200, 100, 100, self.a_255)
        self.head_bar_color_currend_day = QColor(7, 177, 38, self.a_150)
        self.scheduled_time_color = QColor(200, 0, 0, self.a_150)
        self.planed_time_color = QColor(0, 200, 0, self.a_150)
        self.display_work_unit_color = QColor(237, 76, 92, self.a_150)
        self.display_break_unit_color = QColor(27, 141, 211, self.a_150)
        self.display_coffee_unit_color = QColor(110, 191, 93, self.a_150)
        self.display_school_unit_color = QColor(105, 105, 105, self.a_150)
        self.active_indicator_button_color = "7, 177, 38"
        self.inactive_indicator_button_color = "240, 240, 240"
        self.base_spacer_color = "93, 90, 88"

        self.r_part = [255, 255, 255, 154, 0]
        self.g_part = [0, 165, 255, 205, 255]
        self.b_part = [0, 0, 0, 50, 0]

        # db fields
        self.subjects = dict() # use name as key
        self.schedule_entries = dict() # use (dow, start_hour, start_minute, end_hour, end_minute) as key
        self.work_unit_entries = dict() # use (day, month, year, start_hour, start_minute, end_hour, end_minute) as key
        self.subject_types = dict() # use id as key
        self.subject_work_units = dict()
        self.subject_work_percentage = dict()
        self.work_day_time_units = dict() # recorded time units, contains list of units for every recorded day
        self.todo_list_items = dict() # all items currently in the todo list
        self.work_day_summaries = dict() # all summaries of work days

        self.study_subject = None # study subject obj
        self.free_work_subject_type_key = 0 # id of subject type for free work

        # db file name
        self.db_file_name = "load from version.py"
        self.db_version = "load from version.py"
        self.db_description = "load from version.py"

        # datepicker styles
        self.date_picker_style =\
        """
        QCalendarWidget QAbstractItemView {
            selection-background-color: rgb(0, 120, 215);
            selection-color: white;
        }
        """

        # timer stuff ---------------------------------------------
        # layout measurements
        self.button_width = 60
        self.button_height = 60
        self.button_icon_height = self.button_height - 6
        self.button_icon_width = self.button_width - 6
        self.vertical_label_width = 22
        self.vertical_spacer_width = 6
        self.control_button_width = int((self.vertical_label_width + self.button_height)/2)
        self.control_button_height = int((self.vertical_label_width + self.button_height)/2)
        self.control_button_icon_width = self.control_button_width - 6
        self.control_button_icon_height = self.control_button_height - 6
        self.total_timer_width = self.vertical_label_width + self.button_height

        # timer progess bar
        self.time_step = 125
        self.progress_bar_width = self.button_width + self.vertical_label_width

        # timer datepicker
        self.current_work_day = datetime.today().date()
        self.work_time_interval = 25*60 # 25 minutes work interval
        self.break_time_interval = 5*60
        self.coffee_time_interval = 0

        # timer labels and descriptions
        self.work_session_total_name = "TW"
        self.break_session_total_name = "TB"
        self.coffee_session_total_name = "TC"
        self.work_session_subject_name = "W "
        self.break_sesson_subject_name = "B "
        self.coffee_session_subject_name = "C "
        self.summary_label_init = "00:00:00"
        self.work_description = "Work"
        self.break_description = "Break"
        self.coffee_description = "Coffee"

        self.scrollbar_policy = Qt.ScrollBarPolicy.ScrollBarAlwaysOn
        min_height = "1em"
        min_scrollbar_width = "1.2em"
        if os_type == "win32" or os_type == "linux":
            self.font = QFont("Arial")
            self.font.setPointSize(9)
            min_height = "1em"
            min_scrollbar_width = "1.2em"
            print("win or linux")
        elif os_type == "darwin":
            self.font = QFont("San Francisco")
            self.font.setPointSize(9)
            print("### mac os ###")
        
        self.style = """
            QPushButton [ 
                min-height: {min_height};
            ]
            QDateEdit [ 
                min-height: {min_height};
            ]
            QTimeEdit [
                min-height: {min_height};
            ]
            QComboBox [
                min-height: {min_height};
            ]
            QScrollBar [
                min-width: {min_s_width};
                border-radius: 3px;
            ]
            QProgressBar::Chunk [
                min-height: {min_height};
                background-color: green;
                border-radius: 3px;
            ]

        """.format(\
            min_height=min_height,\
            min_s_width=min_scrollbar_width)\
            .replace("[","{").replace("]","}")
