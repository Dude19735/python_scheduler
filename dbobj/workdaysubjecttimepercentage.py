"""
Module contains definition of 
WorkDaySubjectTimePercentage
"""

import sqlite3

from dbobj.helperfunctions import HelperFunctions as HF
from dbobj.unittypes import UnitTypes

class WorkDaySubjectTimePercentage():

    """
    Class offers methodes to get percentage of planed vs worked time
    """

    def __init__(self, subject_id, start_date, at_date, time_diff,\
        work_time, total_time_diff):

        self.subject_id = subject_id
        self.at_date = at_date
        self.time_diff = time_diff
        self.work_time = work_time
        self.work_percent = 0
        self.total_time_diff = total_time_diff

        self.update_percent(self.work_time)

        # index of at_date with respect to start_date
        self.date_index = (self.at_date - start_date).days

    def key(self):

        """return uniform key for work unit entry"""

        return (self.subject_id, self.date_index)

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
            self.work_percent = 100.0 / self.work_time * self.time_diff

    @staticmethod
    def new(subject_id, start_date, at_date, time_diff,\
        work_time, total_time_diff):

        """return new object of this type"""

        return WorkDaySubjectTimePercentage(\
            subject_id, start_date, at_date, time_diff,\
                work_time, total_time_diff)

    @staticmethod
    def get_work_day_subject_time_percentage(obj_dict, from_work_day, to_work_day, db_name):

        """get list with ordered time units for given work day"""

        from_work_day_value = HF.date_2_db(from_work_day)
        to_work_day_value = HF.date_2_db(to_work_day)

        connection = sqlite3.connect(db_name)
        cursor = connection.cursor()
        try:
            cursor.execute("""SELECT
                                wue.SubjectId,
                                wue.StartDate AS AtDate,
                                SUM(wue.TimeDiff) / 3600.0 AS TimeDiff,
                                COALESCE(swu.WorkTime, 0) AS WorkTime
                              FROM WorkUnitEntry wue
                              LEFT OUTER JOIN SubjectWorkUnit swu ON wue.SubjectId = swu.SubjectId 
                                                                 AND swu.AtDate = wue.StartDate
                              WHERE wue.StartDate >= {0} AND wue.StartDate <= {1}
                                AND wue.UnitType IN ({2}, {3})
                              GROUP BY wue.SubjectId, wue.StartDate
                              ORDER BY wue.SubjectId, wue.StartDate""".format(\
                                  from_work_day_value,\
                                      to_work_day_value,\
                                          UnitTypes.WORK_TIME,\
                                              UnitTypes.SCHOOL_TIME))

            rows = cursor.fetchall()
            obj_dict.clear()

            for row in rows:
                at_date = HF.date_2_python_date(row[1])

                obj = WorkDaySubjectTimePercentage.new(\
                    row[0],\
                        from_work_day,\
                            at_date,\
                                row[2],\
                                    row[3],\
                                        0)
                obj_dict[obj.key()] = obj

            cursor.execute("""SELECT
                                wue.SubjectId,
                                wue.StartDate AS AtDate,
                                SUM(wue.TimeDiff) / 3600.0 AS TimeDiff
                              FROM WorkUnitEntry wue
                              LEFT OUTER JOIN SubjectWorkUnit swu ON wue.SubjectId = swu.SubjectId 
                                                                 AND swu.AtDate = wue.StartDate
                              WHERE wue.StartDate >= {0} AND wue.StartDate <= {1}
                                AND wue.UnitType IN ({2}, {3})
                              GROUP BY wue.SubjectId, wue.StartDate
                              ORDER BY wue.SubjectId, wue.StartDate""".format(\
                                  from_work_day_value,\
                                      to_work_day_value,\
                                          UnitTypes.WORK_TIME,\
                                              UnitTypes.SCHOOL_TIME))

            rows = cursor.fetchall()
            for row in rows:
                at_date = HF.date_2_python_date(row[1])
                obj = WorkDaySubjectTimePercentage.new(\
                    row[0],\
                        from_work_day,\
                            at_date,\
                                0,\
                                    0,\
                                        row[2])

                if obj.key() in obj_dict.keys():
                    obj_dict[obj.key()].total_time_diff = obj.total_time_diff
                else:
                    obj_dict[obj.key()] = obj

        except sqlite3.Error as error:
            connection.rollback()
            connection.close()
            print("WorkDaySubjectTimePercentage.get_work_day_subject_time_percentage " +\
                str(WorkDaySubjectTimePercentage.__class__) + " error:", error.args[0])
            connection.close()
            raise

        connection.close()
