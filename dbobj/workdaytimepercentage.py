"""
Module contains definition of
WorkDayTimePercentage
"""

import sqlite3

from dbobj.helperfunctions import HelperFunctions as HF
from dbobj.unittypes import UnitTypes

class WorkDayTimePercentage():

    """
    Class offers methodes to get percentage of planed vs worked time
    """

    def __init__(self, start_date, at_date, time_diff, work_time,\
        work_percent, total_time_diff):

        self.at_date = at_date
        self.time_diff = time_diff # only recorded time using timer
        self.work_time = work_time # planed time using entry canvas
        self.work_percent = work_percent
        self.total_time_diff = total_time_diff # booked and recorded time

        # index of at_date with respect to start_date
        self.date_index = (self.at_date - start_date).days

    def key(self):

        """return uniform key for work unit entry"""

        return self.date_index

    @staticmethod
    def new(start_date, at_date, time_diff, work_time, work_percent, total_time_diff):

        """return new object of this type"""

        return WorkDayTimePercentage(\
            start_date, at_date, time_diff, work_time, work_percent, total_time_diff)

    @staticmethod
    def get_work_day_time_percentage(obj_dict, from_work_day, to_work_day, db_name):

        """get list with ordered time units for given work day"""

        from_work_day_value = HF.date_2_db(from_work_day)
        to_work_day_value = HF.date_2_db(to_work_day)

        connection = sqlite3.connect(db_name)
        cursor = connection.cursor()
        try:
            obj_dict.clear()
            cursor.execute("""
                           SELECT StartDate, SUM(TimeDiff) / 3600.0 TimeDiff
                           FROM WorkUnitEntry
                           WHERE StartDate >= {0} AND StartDate <= {1} AND UnitType IN ({2}, {3})
                           GROUP BY StartDate
                           ORDER BY StartDate
                           """.format(\
                               from_work_day_value,\
                                   to_work_day_value,\
                                       UnitTypes.WORK_TIME,\
                                              UnitTypes.SCHOOL_TIME))

            rows = cursor.fetchall()
            for row in rows:
                start_date = HF.date_2_python_date(row[0])
                entry = WorkDayTimePercentage.new(\
                    from_work_day, start_date, row[1], 0, 0, 0)
                obj_dict[entry.key()] = entry

            cursor.execute("""
                           SELECT AtDate, SUM(WorkTime) WorkTime
                           FROM SubjectWorkUnit
                           WHERE AtDate >= {0} AND AtDate <= {1}
                           GROUP BY AtDate
                           ORDER BY AtDate
                           """.format(\
                               from_work_day_value,\
                                   to_work_day_value))

            rows = cursor.fetchall()
            for row in rows:
                at_date = HF.date_2_python_date(row[0])
                date_index = (at_date - from_work_day).days
                if date_index in obj_dict.keys():
                    entry = obj_dict[date_index]
                    entry.work_time = row[1]
                else:
                    obj_dict[date_index] = WorkDayTimePercentage.new(\
                        from_work_day, at_date, 0, row[1], 0, 0)

            # collect the totals, every entry should already have something
            # in obj_dict
            cursor.execute("""
                           SELECT StartDate, SUM(TimeDiff) / 3600.0 TimeDiff
                           FROM WorkUnitEntry
                           WHERE StartDate >= {0} AND StartDate <= {1}
                             AND UnitType IN ({2}, {3})
                           GROUP BY StartDate
                           ORDER BY StartDate
                           """.format(\
                               from_work_day_value,\
                                   to_work_day_value,\
                                       UnitTypes.WORK_TIME,\
                                           UnitTypes.SCHOOL_TIME))

            rows = cursor.fetchall()
            for row in rows:
                at_date = HF.date_2_python_date(row[0])
                date_index = (at_date - from_work_day).days
                if date_index in obj_dict.keys():
                    entry = obj_dict[date_index]
                    entry.total_time_diff = row[1]
                else:
                    obj_dict[date_index] = WorkDayTimePercentage.new(\
                        from_work_day, at_date, 0, 0, 0, row[1])

            for i in obj_dict.values():
                entry = obj_dict[i.date_index]
                if entry.work_time == 0:
                    entry.work_percent = 100
                else:
                    entry.work_percent = min(100.0, 100.0 / entry.work_time * entry.time_diff)

        except sqlite3.Error as error:
            connection.rollback()
            connection.close()
            print("WorkDaySubjectTimePercentage.get_work_day_time_percentage " +\
                str(WorkDayTimePercentage.__class__) + " error:", error.args[0])
            connection.close()
            raise

        connection.close()
