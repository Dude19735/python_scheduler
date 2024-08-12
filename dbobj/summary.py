"""
Module contains definition of Summary
"""

import sqlite3
from dbobj.helperfunctions import HelperFunctions as HF
from dbobj.unittypes import UnitTypes

class Summary():

    """
    Class offers method to get summary times in seconds
    """

    def __init__(self):
        pass

    @staticmethod
    def total_work_for_subject_and_workday(work_day, subject_id, db_name):

        """get total worktime for subject and workday"""

        return Summary.total_time_for_subject_and_workday(\
            HF.date_2_db(work_day), subject_id, UnitTypes.WORK_TIME, db_name)

    @staticmethod
    def total_break_for_subject_and_workday(work_day, subject_id, db_name):

        """get total breaktime for subject and workday"""

        return Summary.total_time_for_subject_and_workday(\
            HF.date_2_db(work_day), subject_id, UnitTypes.BREAK_TIME, db_name)

    @staticmethod
    def total_work_for_workday(work_day, db_name):

        """get total worktime for subject and workday"""

        return Summary.total_time_for_workday(\
            HF.date_2_db(work_day), UnitTypes.WORK_TIME, db_name)

    @staticmethod
    def total_break_for_workday(work_day, db_name):

        """get total breaktime for subject and workday"""

        return Summary.total_time_for_workday(\
            HF.date_2_db(work_day), UnitTypes.BREAK_TIME, db_name)

    @staticmethod
    def total_coffee_for_workday(work_day, db_name):

        """get total coffee time for subject and workday"""

        return Summary.total_time_for_workday(\
            HF.date_2_db(work_day), UnitTypes.COFFEE_TIME, db_name)

    @staticmethod
    def total_time_for_subject_and_workday(work_day, subject_id, unit_type, db_name):

        """get total worktime for subject and unit time and workday"""

        connection = sqlite3.connect(db_name)
        cursor = connection.cursor()
        try:
            cursor.execute("""SELECT SUM(TimeDiff) AS TimeDiff
                              FROM WorkUnitEntry
                              WHERE StartDate = {0}
                                AND SubjectId = {1}
                                AND UnitType = {2}""".format(\
                                    str(work_day), str(subject_id), str(unit_type)))
            rows = cursor.fetchall()
            result = rows[0][0]

        except sqlite3.Error as error:
            connection.rollback()
            connection.close()
            print("Summary.total_time_for_subject " +\
                str(Summary.__class__) + " error:", error.args[0])
            connection.close()
            raise

        connection.close()

        if result is None:
            return 0
        return int(result)

    @staticmethod
    def total_time_for_workday(work_day, unit_type, db_name):

        """get total worktime and unit time and workday"""

        connection = sqlite3.connect(db_name)
        cursor = connection.cursor()
        try:
            cursor.execute("""SELECT SUM(TimeDiff) AS TimeDiff
                              FROM WorkUnitEntry
                              WHERE StartDate = {0}
                                AND UnitType = {1}""".format(\
                                    str(work_day), str(unit_type)))
            rows = cursor.fetchall()
            result = rows[0][0]

        except sqlite3.Error as error:
            connection.rollback()
            connection.close()
            print("Summary.total_time_for_workday " +\
                str(Summary.__class__) + " error:", error.args[0])
            connection.close()
            raise

        connection.close()

        if result is None:
            return 0
        return int(result)
