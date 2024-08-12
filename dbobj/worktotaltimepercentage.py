"""
Module contains definition of
WorkTotalTimePercentage
"""

import sqlite3

from dbobj.helperfunctions import HelperFunctions as HF
from dbobj.unittypes import UnitTypes

class WorkTotalTimePercentage():

    """
    Class offers methodes to get percentage of planed vs worked time
    """

    def __init__(self, time_diff, work_time, total_time_diff):

        self.time_diff = time_diff
        self.work_time = 0
        self.work_percent = 0
        self.total_time_diff = total_time_diff

        self.update_percent(work_time)

    def key(self):

        """return uniform key for work unit entry"""

        return (self.time_diff, self.work_time, self.work_percent)

    def update_percent(self, work_time):

        """update work_percent using new work_time"""

        self.work_time = work_time
        if self.work_time == 0:
            if self.time_diff > 0:
                self.work_percent = 100
            elif self.total_time_diff > 0:
                self.work_percent = 100
            else:
                self.work_percent = 0
        else:
            self.work_percent = 100.0 / self.work_time * self.time_diff / 3600.0

    @staticmethod
    def new(time_diff, work_time, total_time_diff):

        """return new object of this type"""

        return WorkTotalTimePercentage(time_diff, work_time, total_time_diff)

    @staticmethod
    def get_work_total_time_percentage(from_work_day, to_work_day, db_name):

        """get list with ordered time units for given work day"""

        from_work_day_value = HF.date_2_db(from_work_day)
        to_work_day_value = HF.date_2_db(to_work_day)

        connection = sqlite3.connect(db_name)
        cursor = connection.cursor()
        try:
            cursor.execute("""
                           SELECT COALESCE(SUM(TimeDiff), 0) / 3600.0 TimeDiff
                           FROM WorkUnitEntry
                           WHERE StartDate >= {0} AND StartDate <= {1} AND UnitType IN ({2}, {3})
                           """.format(\
                               from_work_day_value,\
                                   to_work_day_value,\
                                       UnitTypes.WORK_TIME,\
                                           UnitTypes.SCHOOL_TIME))

            rows = cursor.fetchall()
            time_diff = rows[0][0]

            cursor.execute("""
                           SELECT COALESCE(SUM(TimeDiff), 0) / 3600.0 TimeDiff
                           FROM WorkUnitEntry
                           WHERE StartDate >= {0} AND StartDate <= {1}
                             AND UnitType IN ({2}, {3})
                           """.format(\
                               from_work_day_value,\
                                   to_work_day_value,\
                                       UnitTypes.WORK_TIME,\
                                           UnitTypes.SCHOOL_TIME))

            rows = cursor.fetchall()
            total_time_diff = rows[0][0]

            cursor.execute("""
                           SELECT COALESCE(SUM(WorkTime), 0) WorkTime
                           FROM SubjectWorkUnit
                           WHERE AtDate >= {0} AND AtDate <= {1}
                           """.format(\
                               from_work_day_value,\
                                   to_work_day_value))

            rows = cursor.fetchall()
            work_time = rows[0][0]

            obj = WorkTotalTimePercentage.new(time_diff, work_time, total_time_diff)

        except sqlite3.Error as error:
            connection.rollback()
            connection.close()
            print("WorkTotalTimePercentage.get_work_total_time_percentage " +\
                str(WorkTotalTimePercentage.__class__) + " error:", error.args[0])
            connection.close()
            raise

        connection.close()

        return obj
