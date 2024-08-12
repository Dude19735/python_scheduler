"""
Module contains definition of SubjectType
"""

import sqlite3
from dbobj.helperfunctions import HelperFunctions as HF

class SubjectType():

    """
    Class represents one subject type (lecture, exercise class, ...)
    and all it's properties
    """

    def __init__(self, name, description):
        self.subject_type_id = None
        self.name = name
        self.description = description

    def __del__(self):
        pass

    def key(self):

        """return uniform key for subject type"""

        return self.subject_type_id

    @staticmethod
    def seed(db_connection): # pylint: disable=invalid-name
        """create object table in database"""

        cursor = db_connection.cursor()
        try:
            cursor.execute("""CREATE TABLE SubjectType
                        (SubjectTypeId integer PRIMARY KEY autoincrement,
                        Name text,
                        Description text,
                        CreatedTS DEFAULT CURRENT_TIMESTAMP,
                        ModifiedTS DEFAULT CURRENT_TIMESTAMP,
                        UNIQUE(Name))""")
        except sqlite3.Error as error:
            print("SubjectType.Seeding " + str(SubjectType.__class__) + " error:", error.args[0])
            raise

    @staticmethod
    def init(db_connection):

        """insert initial data into table"""

        cursor = db_connection.cursor()
        try:
            cursor.execute("""INSERT INTO SubjectType
                              (Name, Description)
                       VALUES ('{0}', '{1}')""".format("V", "Lecture"))

            cursor.execute("""INSERT INTO SubjectType
                              (Name, Description)
                       VALUES ('{0}', '{1}')""".format("U", "Exercise"))

            cursor.execute("""INSERT INTO SubjectType
                              (Name, Description)
                       VALUES ('{0}', '{1}')""".format("C", "Coffee"))

            cursor.execute("""INSERT INTO SubjectType
                              (Name, Description)
                       VALUES ('{0}', '{1}')""".format("F", "Free Work"))

        except sqlite3.Error as error:
            print("SubjectType.init " + str(SubjectType.__class__) + " error: ", error.args[0])
            raise

    @staticmethod
    def new(name, description): # pylint: disable=invalid-name

        """Create a new instance"""

        return SubjectType(name, description)

    @staticmethod
    def to_db(obj, obj_dict, db_name):

        """store object to db"""

        connection = sqlite3.connect(db_name)
        cursor = connection.cursor()
        try:
            cursor.execute("""INSERT INTO SubjectType
                              (Name, Description)
                       VALUES ('{0}', '{1}')""".format(\
                           HF.escape_quote(obj.name),\
                               HF.escape_quote(obj.description)))
        except sqlite3.Error as error:
            connection.rollback()
            connection.close()
            print("SubjectType.to_db " + str(SubjectType.__class__) + " error:", error.args[0])
            raise

        connection.commit()
        connection.close()

        # add object to dict containing all subjects
        obj.subject_type_id = cursor.lastrowid
        obj_dict[obj.key()] = obj

    @staticmethod
    def update_by_db_id(obj, db_name):

        """update object using db id"""

        connection = sqlite3.connect(db_name)
        cursor = connection.cursor()
        try:
            cursor.execute("""UPDATE SubjectType SET
                              Name = '{0}',
                              Description = '{1}'
                              WHERE SubjectTypeId = {2}""".format(\
                           HF.escape_quote(obj.name),\
                               HF.escape_quote(obj.description),\
                                   obj.subject_type_id))
        except sqlite3.Error as error:
            connection.rollback()
            connection.close()
            print("SubjectType.update_by_db_id " + str(SubjectType.__class__) +\
                " error:", error.args[0])
            raise

        connection.commit()
        connection.close()

    @staticmethod
    def reload_from_db(obj_dict, db_name):

        """reload all subject types from db"""

        connection = sqlite3.connect(db_name)
        cursor = connection.cursor()
        try:
            cursor.execute("""SELECT SubjectTypeId, Name, Description
                              FROM SubjectType ORDER BY SubjectTypeId""")

            rows = cursor.fetchall()
            obj_dict.clear()
            for row in rows:
                obj = SubjectType.new(\
                    row[1],\
                        row[2])
                obj.subject_type_id = row[0]
                obj_dict[obj.key()] = obj

        except sqlite3.Error as error:
            connection.rollback()
            connection.close()
            print("SubjectType.reload_from_db " + str(SubjectType.__class__) +\
                " error:", error.args[0])
            raise

        connection.close()

    @staticmethod
    def delete_by_db_id(obj, obj_dict, db_name):

        """delete obj from db and from corresponding obj_dict"""

        connection = sqlite3.connect(db_name)
        cursor = connection.cursor()
        try:
            cursor.execute("""DELETE FROM SubjectType WHERE SubjectTypeId = {0}""".format(\
                obj.subject_type_id))

            del obj_dict[obj.key()]
        except sqlite3.Error as error:
            connection.rollback()
            connection.close()
            print("SubjectType.delete_by_db_id " + str(SubjectType.__class__) +\
                " error:", error.args[0])
            raise

        connection.commit()
        connection.close()

    @staticmethod
    def compare(obj1, obj2):

        """compare two SubjectType objects"""

        return obj1.subject_type_id == obj2.subject_type_id and\
            obj1.name == obj2.name and\
                obj1.description == obj2.description
