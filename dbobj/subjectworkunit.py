"""
Module contains definition of SubjectWorkUnit
"""

import sqlite3
from dbobj.helperfunctions import HelperFunctions as HF

class SubjectWorkUnit():

    """
    Class represents one (Subject, Date) planed work unit in hours
    """

    def __init__(self, subject_id, work_time, start_date, at_date, description):

        self.subject_work_unit_id = None
        self.subject_id = subject_id
        self.work_time = work_time
        self.at_date = at_date
        self.description = description

        # these two are set by the reload_from_db function
        self.start_date = start_date

        # index of at_date with respect to start_date
        self.date_index = (self.at_date - start_date).days

    def __del__(self):
        pass

    def key(self):

        """return uniform key for work unit entry"""

        return (self.subject_id, self.date_index)

    def set_at_date(self, new_date):

        """set new date including the new index"""

        self.at_date = new_date
        self.date_index = (self.at_date - self.start_date).days

    @staticmethod
    def seed(db_connection): # pylint: disable=invalid-name

        """create object table in database"""

        cursor = db_connection.cursor()
        try:
            cursor.execute("""CREATE TABLE SubjectWorkUnit
                        (SubjectWorkUnitId integer PRIMARY KEY autoincrement,
                        SubjectId integer,
                        WorkTime real,
                        AtDate integer,
                        Description text,
                        CreatedTS DEFAULT CURRENT_TIMESTAMP,
                        ModifiedTS DEFAULT CURRENT_TIMESTAMP)""")

            cursor.execute(\
                "CREATE INDEX SubjectWorkUnit_AtDate_I ON SubjectWorkUnit (AtDate)")
            cursor.execute(\
                "CREATE INDEX SubjectWorkUnit_SubjectId_I ON SubjectWorkUnit (SubjectId)")
        except sqlite3.Error as error:
            print("Seeding " + str(SubjectWorkUnit.__class__) + " error:", error.args[0])
            raise

    @staticmethod
    def new(subject_id, work_time, start_date, at_date, description): # pylint: disable=invalid-name

        """Create a new instance"""

        return SubjectWorkUnit(subject_id, work_time, start_date, at_date, description)

    @staticmethod
    def to_db(obj, obj_dict, db_name):

        """store object to db"""

        connection = sqlite3.connect(db_name)
        cursor = connection.cursor()
        try:
            cursor.execute("""INSERT INTO SubjectWorkUnit
                              (SubjectId, WorkTime, AtDate, Description)
                       VALUES ({0}, {1}, {2}, '{3}')""".format(\
                           obj.subject_id,\
                               obj.work_time,\
                                   HF.date_2_db(obj.at_date),\
                                       HF.escape_quote(obj.description)))
        except sqlite3.Error as error:
            connection.rollback()
            connection.close()
            print("SubjectWorkUnit.to_db " + str(SubjectWorkUnit.__class__) +\
                " error:", error.args[0])
            raise

        connection.commit()
        connection.close()

        # add object to dict containing all subjects
        obj.subject_work_unit_id = cursor.lastrowid

        obj_dict[obj.key()] = obj

    @staticmethod
    def update_by_db_id(obj, db_name):

        """update object by db id"""

        connection = sqlite3.connect(db_name)
        cursor = connection.cursor()
        try:
            cursor.execute("""UPDATE SubjectWorkUnit SET
                              SubjectId = {0},
                              WorkTime = {1},
                              AtDate = {2},
                              Description = '{3}'
                       WHERE SubjectWorkUnitId = {4}""".format(\
                               obj.subject_id,\
                                   obj.work_time,\
                                       HF.date_2_db(obj.at_date),\
                                           HF.escape_quote(obj.description),\
                                               obj.subject_work_unit_id))
        except sqlite3.Error as error:
            connection.rollback()
            connection.close()
            print("SubjectWorkUnit.update_by_db_id " + str(SubjectWorkUnit.__class__) +\
                " error:", error.args[0])
            raise

        connection.commit()
        connection.close()

    @staticmethod
    def reload_from_db(obj_dict, start_date, end_date, db_name):

        """load all objects of this type from db"""

        start_date_val = HF.date_2_db(start_date)
        end_date_val = HF.date_2_db(end_date)

        connection = sqlite3.connect(db_name)
        cursor = connection.cursor()
        try:
            cursor.execute("""SELECT SubjectWorkUnitId, SubjectId,
                                    WorkTime, AtDate, Description
                              FROM SubjectWorkUnit WHERE AtDate >= {0}
                                             AND AtDate <= {1}
                              ORDER BY SubjectWorkUnitId""".format(\
                                                 start_date_val,\
                                                     end_date_val))
            rows = cursor.fetchall()
            obj_dict.clear()
            for row in rows:
                obj = SubjectWorkUnit.new(\
                    row[1],\
                        row[2],\
                            start_date,\
                                HF.date_2_python_date(row[3]),\
                                    row[4])

                obj.subject_work_unit_id = row[0]

                obj_dict[obj.key()] = obj
        except sqlite3.Error as error:
            connection.rollback()
            connection.close()
            print("SubjectWorkUnit.reload_from_db " + str(SubjectWorkUnit.__class__) +\
                " error:", error.args[0])
            raise

        connection.close()

    @staticmethod
    def delete_by_db_id(obj, obj_dict, db_name):

        """delete obj from db and from corresponding obj_dict"""

        connection = sqlite3.connect(db_name)
        cursor = connection.cursor()
        try:
            cursor.execute("""DELETE FROM SubjectWorkUnit WHERE SubjectWorkUnitId = {0}""".format(\
                obj.subject_work_unit_id))

            del obj_dict[obj.key()]
        except sqlite3.Error as error:
            connection.rollback()
            connection.close()
            print("SubjectWorkUnit.delete_by_db_id " + str(SubjectWorkUnit.__class__) +\
                " error:", error.args[0])
            raise

        connection.commit()
        connection.close()

    @staticmethod
    def compare(obj1, obj2):

        """compare two WorkUnitEntry objects"""

        return obj1.subject_work_unit_id == obj2.subject_work_unit_id and\
            obj1.subject_id == obj2.subject_id and\
                obj1.work_time == obj2.work_time and\
                    obj1.at_date == obj2.at_date and\
                        obj1.description == obj2.description
