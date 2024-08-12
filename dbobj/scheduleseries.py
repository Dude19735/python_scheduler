"""
Module offers object that can store series of something with a start_date
and an end_date
"""

import sqlite3
from dbobj.helperfunctions import HelperFunctions as HF

class ScheduleSeries():

    """
    Class represents one series object
    """

    def __init__(self, type_id, subject_id, start_date, end_date, description):
        self.schedule_series_id = None
        self.type_id = type_id
        self.subject_id = subject_id
        self.start_date = start_date
        self.end_date = end_date
        self.description = description

    def __del__(self):
        pass

    def key(self):

        """return uniform series key"""

        return self.schedule_series_id

    def copy(self):

        """return a copy of this object"""

        obj = ScheduleSeries(self.type_id, self.subject_id,\
            self.start_date, self.end_date, self.description)
        obj.schedule_series_id = self.schedule_series_id
        return obj

    @staticmethod
    def seed(db_connection):

        """create object table in database"""

        cursor = db_connection.cursor()
        try:
            cursor.execute("""CREATE TABLE ScheduleSeries
                               (ScheduleSeriesId integer PRIMARY KEY autoincrement,
                               TypeId integer,
                               SubjectId integer,
                               StartDate integer,
                               EndDate integer,
                               Description text,
                               CreatedTS DEFAULT CURRENT_TIMESTAMP,
                               ModifiedTS DEFAULT CURRENT_TIMESTAMP,
                               FOREIGN KEY (SubjectId) REFERENCES Subject(SubjectId),
                               FOREIGN KEY (TypeId) REFERENCES SubjectType(TypeId))""")

            cursor.execute(\
                "CREATE INDEX ScheduleSeries_DateIndex_I ON ScheduleSeries (StartDate)")
            cursor.execute(\
                "CREATE INDEX ScheduleSeries_EndDate_I ON ScheduleSeries (EndDate)")

        except sqlite3.Error as error:
            print("ScheduleSeries.Seeding " + str(ScheduleSeries.__class__) +\
                " error:", error.args[0])
            raise

    @staticmethod
    def new(type_id, subject_id, start_date, end_date, description):

        """Create a new instance"""

        return ScheduleSeries(type_id, subject_id, start_date, end_date, description)

    @staticmethod
    def to_db(obj, db_connection):

        """
        store object to db
        has no obj_dict because it's stored in a ScheduleEntry
        it also has a db_connection in order to be faster and force correct usage
        a little bit better
        """

        cursor = db_connection.cursor()
        try:
            cursor.execute("""INSERT INTO ScheduleSeries
                              (TypeId, SubjectId, StartDate, EndDate, Description)
                       VALUES ({0}, {1}, {2}, {3}, '{4}')""".format(\
                           obj.type_id,\
                               obj.subject_id,\
                                   HF.date_2_db(obj.start_date),\
                                       HF.date_2_db(obj.end_date),\
                                           HF.escape_quote(obj.description)))
        except sqlite3.Error as error:
            print("ScheduleSeries.to_db " +\
                str(ScheduleSeries.__class__) + " error:", error.args[0])
            raise

        # add object to dict containing all subjects
        obj.series_id = cursor.lastrowid

    @staticmethod
    def update_by_db_id(obj, db_name):

        """update db object using db id"""

        connection = sqlite3.connect(db_name)
        cursor = connection.cursor()
        try:
            cursor.execute("""UPDATE ScheduleSeries SET
                                     TypeId = {0},
                                     SubjectId = {1},
                                     StartDate = {2},
                                     EndDate = {3},
                                     Description = '{4}'
                              WHERE ScheduleSeriesId = {5}""".format(\
                                  obj.type_id,\
                                      obj.subject_id,\
                                          HF.date_2_db(obj.start_date),\
                                              HF.date_2_db(obj.end_date),\
                                                  HF.escape_quote(obj.description),\
                                                      obj.schedule_series_id))
        except sqlite3.Error as error:
            connection.rollback()
            connection.close()
            print("ScheduleSeries.update_by_db_id " + str(ScheduleSeries.__class__) +\
                " error:", error.args[0])
            raise

        connection.commit()
        connection.close()

    @staticmethod
    def delete_by_db_id(obj, obj_dict, db_name):

        """delete obj from db and from corresponding obj_dict"""

        connection = sqlite3.connect(db_name)
        cursor = connection.cursor()
        try:
            cursor.execute("""DELETE FROM ScheduleSeries WHERE ScheduleSeriesId = {0}""".format(\
                obj.subject_series_id))

            del obj_dict[obj.key()]
        except sqlite3.Error as error:
            connection.rollback()
            connection.close()
            print("ScheduleSeries.delete_by_db_id " + str(ScheduleSeries.__class__) +\
                " error:", error.args[0])
            raise

        connection.commit()
        connection.close()

    @staticmethod
    def compare(obj1, obj2):

        """compare two Series objects"""

        return obj1.schedule_series_id == obj2.schedule_series_id and\
            obj1.type_id == obj2.type_id and\
                obj1.subject_id == obj2.subject_id and\
                    obj1.start_date == obj2.start_date and\
                        obj1.end_date == obj2.end_date and\
                            obj1.description == obj2.description
