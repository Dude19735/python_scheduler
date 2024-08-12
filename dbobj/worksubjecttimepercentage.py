"""
Module contains definition of
WorkSubjectTimePercentage
"""

import sqlite3

from dbobj.helperfunctions import HelperFunctions as HF
from dbobj.unittypes import UnitTypes
from dbobj.subjecttypes import SubjectTypes

class WorkSubjectTimePercentage():

    """
    Class offers methodes to get percentage of planed vs worked time
    """

    def __init__(self, subject_id, time_diff, work_time, work_percent, total_time_diff):

        self.subject_id = subject_id
        self.time_diff = time_diff
        self.work_time = work_time
        self.work_percent = work_percent
        self.total_time_diff = total_time_diff

    def key(self):

        """return uniform key for work unit entry"""

        return self.subject_id

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
    def new(subject_id, time_diff, work_time, work_percent, total_time_diff):

        """return new object of this type"""

        return WorkSubjectTimePercentage(\
            subject_id, time_diff, work_time, work_percent, total_time_diff)

    @staticmethod
    def get_work_subject_time_percentage(from_work_day, to_work_day, db_name):

        """get list with ordered time units for given work day"""

        from_work_day_value = HF.date_2_db(from_work_day)
        to_work_day_value = HF.date_2_db(to_work_day)

        connection = sqlite3.connect(db_name)
        cursor = connection.cursor()
        obj_dict = dict()
        try:
            cursor.execute("""SELECT
                                SubjectId
                              FROM Subject
                              WHERE SubjectType = {0}
                              ORDER BY SubjectId""".format(\
                                  SubjectTypes.SUBJECT_TYPE))
            subjects = cursor.fetchall()

            cursor.execute("""SELECT
                                SubjectId,
                                COALESCE(SUM(TimeDiff), 0) / 3600.0 TimeDiff
                              FROM WorkUnitEntry
                              WHERE StartDate >= {0} AND StartDate <= {1}
                              AND UnitType IN ({2}, {3})
                              GROUP BY SubjectId
                              ORDER BY SubjectId""".format(\
                                  from_work_day_value,\
                                      to_work_day_value,\
                                          UnitTypes.WORK_TIME,\
                                              UnitTypes.SCHOOL_TIME))
            work_units = cursor.fetchall()
            work_units_dict = dict()
            for work in work_units:
                work_units_dict[work[0]] = work[1]

            cursor.execute("""SELECT
                                SubjectId,
                                COALESCE(SUM(TimeDiff), 0) / 3600.0 TimeDiff
                              FROM WorkUnitEntry
                              WHERE StartDate >= {0} AND StartDate <= {1}
                              AND UnitType IN ({2}, {3})
                              GROUP BY SubjectId
                              ORDER BY SubjectId""".format(\
                                  from_work_day_value,\
                                      to_work_day_value,\
                                          UnitTypes.WORK_TIME,\
                                              UnitTypes.SCHOOL_TIME))
            all_work_units = cursor.fetchall()
            all_work_units_dict = dict()
            for all_work in all_work_units:
                all_work_units_dict[all_work[0]] = all_work[1]

            cursor.execute("""SELECT
                                SubjectId,
                                COALESCE(SUM(WorkTime), 0) WorkTime
                              FROM SubjectWorkUnit
                              WHERE AtDate >= {0} AND AtDate <= {1}
                              GROUP BY SubjectId
                              ORDER BY SubjectId""".format(\
                                  from_work_day_value,\
                                      to_work_day_value))
            subject_units = cursor.fetchall()
            subject_units_dict = dict()
            for subu in subject_units:
                subject_units_dict[subu[0]] = subu[1]

            for row in subjects:
                subject_id = row[0]

                time_diff = 0
                if subject_id in work_units_dict.keys():
                    time_diff = work_units_dict[subject_id]

                total_time_diff = 0
                if subject_id in all_work_units_dict.keys():
                    total_time_diff = all_work_units_dict[subject_id]

                work_time = 0
                if subject_id in subject_units_dict.keys():                
                    work_time = subject_units_dict[subject_id]

                percent = 100.0
                if work_time > 0:
                    percent = 100.0 / work_time * time_diff

                obj = WorkSubjectTimePercentage.new(\
                    subject_id,\
                        time_diff,\
                            work_time,\
                                percent,\
                                    total_time_diff)

                obj_dict[obj.key()] = obj

        except sqlite3.Error as error:
            connection.rollback()
            connection.close()
            print("WorkSubjectTimePercentage.get_work_subject_time_percentage " +\
                str(WorkSubjectTimePercentage.__class__) + " error:", error.args[0])
            connection.close()
            raise

        connection.close()

        return obj_dict
