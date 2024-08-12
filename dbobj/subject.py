"""
Module contains definition of Subject
"""

import sqlite3
from datetime import date
from dbobj.helperfunctions import HelperFunctions as HF
from dbobj.subjecttypes import SubjectTypes

class Subject():

    """
    Class represents one subject and all it's properties
    """

    def __init__(self, name, description, color, start_date, end_date, active, subject_type):
        self.subject_id = None
        self.name = name
        self.description = description
        self.color = color
        self.start_date = start_date
        self.end_date = end_date
        self.active = active
        self.subject_type = subject_type

    def __del__(self):
        pass

    def key(self):

        """return uniform key for subject dictionary"""

        return self.subject_id

    @staticmethod
    def seed(db_connection): # pylint: disable=invalid-name

        """create object table in database"""

        cursor = db_connection.cursor()
        try:
            cursor.execute("""CREATE TABLE Subject
                        (SubjectId integer PRIMARY KEY autoincrement,
                        Name text,
                        Description text,
                        Color text,
                        StartDate integer,
                        EndDate integer,
                        Active integer,
                        SubjectType integer,
                        CreatedTS DEFAULT CURRENT_TIMESTAMP,
                        ModifiedTS DEFAULT CURRENT_TIMESTAMP,
                        UNIQUE(Name))""")

            cursor.execute(\
                "CREATE INDEX Subject_StartDate_I ON Subject (StartDate)")
            cursor.execute(\
                "CREATE INDEX Subject_EndDate_I ON Subject (EndDate)")
            cursor.execute(\
                "CREATE INDEX Subject_Active_I ON Subject (Active)")
            cursor.execute(\
                "CREATE INDEX Subject_SubjectType_I ON Subject (SubjectType)")
        except sqlite3.Error as error:
            print("Subject.Seeding " + str(Subject.__class__) + " error:", error.args[0])
            raise

    @staticmethod
    def init(db_connection):

        """Insert initial data in the Subject table"""

        cursor = db_connection.cursor()
        try:
            cursor.execute("""INSERT INTO Subject
                              (Name, Description, Color, StartDate, EndDate, Active, SubjectType)
                              VALUES ('{0}', '{1}', '{2}', {3}, {4}, {5}, {6})""".format(\
                                  "Study",\
                                      "Study",\
                                          "64,224,208,150",\
                                              HF.date_2_db(date(2000, 1, 1)),\
                                                  HF.date_2_db(date(3000, 12, 31)),\
                                                      1,\
                                                          SubjectTypes.STUDY_TYPE))
        except sqlite3.Error as error:
            print("Subject.init " + str(Subject.__class__) + " error: ", error.args[0])
            raise

    @staticmethod
    def new(name, description, color, start_date, end_date, active, subject_type): # pylint: disable=invalid-name

        """Create a new instance"""

        return Subject(name, description, color, start_date, end_date, active, subject_type)

    @staticmethod
    def to_db(obj, obj_dict, db_name):

        """store object to db"""

        connection = sqlite3.connect(db_name)
        cursor = connection.cursor()
        try:
            cursor.execute("""INSERT INTO Subject
                              (Name, Description, Color, StartDate, EndDate, Active, SubjectType)
                       VALUES ('{0}', '{1}', '{2}', {3}, {4}, {5}, {6})""".format(\
                           HF.escape_quote(obj.name),\
                               HF.escape_quote(obj.description),\
                                   HF.color_2_db_string(obj.color),\
                                       HF.date_2_db(obj.start_date),\
                                           HF.date_2_db(obj.end_date),\
                                               1,\
                                                   SubjectTypes.SUBJECT_TYPE))
        except sqlite3.Error as error:
            connection.rollback()
            connection.close()
            print("Subject.to_db " + str(Subject.__class__) + " error:", error.args[0])
            raise

        connection.commit()
        connection.close()

        # add object to dict containing all subjects
        obj.subject_id = cursor.lastrowid
        obj_dict[obj.key()] = obj

    @staticmethod
    def update_by_db_id(obj, db_name):

        """update existing object using db id"""

        connection = sqlite3.connect(db_name)
        cursor = connection.cursor()
        try:
            cursor.execute("""UPDATE Subject set
                              Name = '{0}',
                              Description = '{1}',
                              Color = '{2}',
                              StartDate = {3},
                              EndDate = {4},
                              Active = {5},
                              SubjectType = {6}
                       WHERE SubjectId = {7}""".format(\
                           HF.escape_quote(obj.name),\
                               HF.escape_quote(obj.description),\
                                   HF.color_2_db_string(obj.color),\
                                       HF.date_2_db(obj.start_date),\
                                           HF.date_2_db(obj.end_date),\
                                               obj.active,\
                                                   obj.subject_type,\
                                                       obj.subject_id))
        except sqlite3.Error as error:
            connection.rollback()
            connection.close()
            print("Subject.update_by_db_id " + str(Subject.__class__) + " error:", error.args[0])
            raise

        connection.commit()
        connection.close()

    @staticmethod
    def reload_from_db(obj_dict, subject_type, active, db_name):

        """load all objects of this type from db"""

        # TODO: do something with start and end dates of subjects

        # start_date_val = HF.date_2_db(start_date)
        # end_date_val = HF.date_2_db(end_date)

        connection = sqlite3.connect(db_name)
        cursor = connection.cursor()
        try:
            cursor.execute("""SELECT SubjectId, Name, Description, Color,
                                     StartDate, EndDate, Active, SubjectType
                              FROM Subject
                              WHERE SubjectType = {0} AND Active = {1}
                              ORDER BY SubjectId""".format(\
                                  subject_type,\
                                      active\
                                          ))

            rows = cursor.fetchall()
            obj_dict.clear()
            for row in rows:
                obj = Subject.new(\
                    row[1],\
                        row[2],\
                            HF.color_db_string_2_q_color(row[3]),\
                                HF.date_2_python_date(row[4]),\
                                    HF.date_2_python_date(row[5]),\
                                        row[6],\
                                            row[7])

                obj.subject_id = row[0]
                obj_dict[obj.key()] = obj
        except sqlite3.Error as error:
            connection.rollback()
            connection.close()
            print("Subject.reload_from_db " + str(Subject.__class__) + " error:", error.args[0])
            raise

        connection.close()

    @staticmethod
    def delete_by_db_id(obj, obj_dict, db_name):

        """delete obj from db and from corresponding obj_dict"""

        connection = sqlite3.connect(db_name)
        cursor = connection.cursor()
        try:
            cursor.execute("""DELETE FROM Subject WHERE SubjectId = {0}""".format(\
                obj.subject_id))

            del obj_dict[obj.key()]
        except sqlite3.Error as error:
            connection.rollback()
            connection.close()
            print("Subject.delete_by_db_id " + str(Subject.__class__) + " error:", error.args[0])
            raise

        connection.commit()
        connection.close()

    @staticmethod
    def compare(obj1, obj2):

        """compare two subjects"""

        return obj1.subject_id == obj2.subject_id and\
            obj1.name == obj2.name and\
                obj1.description == obj2.description and\
                    obj1.color == obj2.color and\
                        obj1.start_date == obj2.start_date and\
                            obj1.end_date == obj2.end_date and\
                                obj1.active == obj2.active and\
                                    obj1.subject_type == obj2.subject_type
