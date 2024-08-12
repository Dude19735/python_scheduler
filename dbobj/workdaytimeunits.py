"""
Module contains definition of WorkDayTimeUnits
"""

from datetime import datetime, timedelta
import sqlite3
from dbobj.helperfunctions import HelperFunctions as HF

class WorkDayTimeUnits():

    """
    Class offers methodes to get time units for work day in order to
    display them
    """

    def __init__(self, work_unit_entry_id, subject_id, unit_type, start_time, end_time,\
        time_diff_min, time_diff_sec, start_offset, start_date, load_date, description):

        self.work_unit_entry_id = work_unit_entry_id
        self.subject_id = subject_id
        self.unit_type = unit_type
        self.start_time = start_time
        self.end_time = end_time
        self.time_diff_min = time_diff_min
        self.time_diff_sec = time_diff_sec
        self.start_offset = start_offset
        self.start_date = start_date
        self.load_date = load_date
        self.description = description

    @staticmethod
    def new(work_unit_entry_id, subject_id, unit_type, start_time, end_time,\
        time_diff_min, time_diff_sec, start_offset, start_date, load_date, description):

        """return new object of this type"""

        return WorkDayTimeUnits(work_unit_entry_id, subject_id, unit_type, start_time, end_time,\
            time_diff_min, time_diff_sec, start_offset, start_date, load_date, description)

    @staticmethod
    def get_time_unit_list(obj_dict, from_work_day, to_work_day, date_format, db_name):

        """get list with ordered time units for given work day"""

        from_work_day_value = HF.date_2_db(from_work_day)
        to_work_day_value = HF.date_2_db(to_work_day)

        connection = sqlite3.connect(db_name)
        cursor = connection.cursor()
        try:
            cursor.execute("""SELECT WorkUnitEntryId, SubjectId, UnitType, StartTime, EndTime,
                                     TimeDiff/60 AS TimeDiffMin, TimeDiff AS TimeDiffSec,
                                     StartOffset, StartDate, Description
                              FROM WorkUnitEntry
                              WHERE StartDate >= {0} AND StartDate <= {1}
                              ORDER BY StartDate ASC, StartTime ASC;""".format(\
                                  from_work_day_value, to_work_day_value))

            rows = cursor.fetchall()

            last_date = 0
            current_date_value = 0
            current_date_str = "00.00.00"

            obj_dict.clear()
            c_list = None

            for row in rows:

                current_date = row[8]
                if current_date != last_date:
                    last_date = current_date
                    current_date_value = HF.date_2_python_date(current_date)
                    current_date_str = current_date_value.strftime(date_format)
                    obj_dict[current_date_str] = list()
                    c_list = obj_dict[current_date_str]

                start_time = HF.time_2_python_time(row[3])
                end_time = HF.time_2_python_time(row[4])
                start_datetime = (datetime.combine(current_date_value, start_time) +\
                    timedelta(hours=row[7]))
                end_datetime = (datetime.combine(current_date_value, end_time) +\
                    timedelta(hours=row[7]))

                c_list.append(WorkDayTimeUnits.new(\
                    row[0],\
                        row[1],\
                            row[2],\
                                start_datetime.time(),\
                                    end_datetime.time(),\
                                        row[5],\
                                            row[6],\
                                                row[7],\
                                                    start_datetime.date(),\
                                                        current_date_value,\
                                                            row[9]))

        except sqlite3.Error as error:
            connection.rollback()
            connection.close()
            print("WorkDayTimeUnits.get_time_unit_list " +\
                str(WorkDayTimeUnits.__class__) + " error:", error.args[0])
            connection.close()
            raise

        connection.close()
