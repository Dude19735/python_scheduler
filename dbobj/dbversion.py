"""
Module contains definitions for DBVersion
"""

import sqlite3

class DBVersion():

    """
    Class represents the Attributes of the DB, like version
    """

    def __init__(self, description, value):
        self.db_version_id = None
        self.description = description
        self.value = value

    def __del__(self):
        pass

    @staticmethod
    def seed(db_connection): # pylint: disable=invalid-name

        """create object table in database"""

        cursor = db_connection.cursor()
        try:
            cursor.execute("""CREATE TABLE DBVersion
                        (DbVersionId integer PRIMARY KEY autoincrement,
                        Description text,
                        Value real,
                        CreatedTS DEFAULT CURRENT_TIMESTAMP,
                        ModifiedTS DEFAULT CURRENT_TIMESTAMP,
                        UNIQUE(Value))""")
        except sqlite3.Error as error:
            print("DBVersion.Seeding " + str(DBVersion.__class__) + " error:", error.args[0])
            raise

    @staticmethod
    def new(description, value): # pylint: disable=invalid-name

        """Create a new instance"""

        return DBVersion(description, value)

    @staticmethod
    def create_new_version(description, value, db_name):

        """
        Create new version of db
        value and description are taken from version.py
        """

        connection = sqlite3.connect(db_name)
        cursor = connection.cursor()
        try:
            cursor.execute("""INSERT INTO DBVersion
                              (Description, Value)
                       VALUES ('{0}', {1})""".format(\
                           description,\
                               value))
        except sqlite3.Error as error:
            connection.rollback()
            connection.close()
            print("DBVersion.create_new_version " +\
                str(DBVersion.__class__) + " error:", error.args[0])
            raise

        connection.commit()
        connection.close()

    @staticmethod
    def create_new_version_extern_conn(description, value, connection):

        """
        Create new version of db
        value and description are taken from version.py
        """

        cursor = connection.cursor()
        try:
            cursor.execute("""INSERT INTO DBVersion
                              (Description, Value)
                       VALUES ('{0}', {1})""".format(\
                           description,\
                               value))
        except sqlite3.Error as error:
            print("DBVersion.create_new_version_extern_conn " +\
                str(DBVersion.__class__) + " error:", error.args[0])
            raise

    @staticmethod
    def get_current_version(db_name):

        """Get current version of the data base"""

        connection = sqlite3.connect(db_name)
        cursor = connection.cursor()
        obj = DBVersion.new("init", 0.0)
        try:
            cursor.execute("""SELECT DbVersionId,Description, Value
                              FROM DBVersion 
                              ORDER BY DbVersionId desc
                              LIMIT 1""")

            rows = cursor.fetchall()
            if rows:
                row = rows[0]
                obj = DBVersion.new(\
                    row[1],\
                        row[2])

                obj.db_version_id = row[0]
        except sqlite3.Error as error:
            connection.rollback()
            connection.close()
            print("DBVersion.reload_from_db " + str(DBVersion.__class__) + " error:", error.args[0])
            raise

        connection.close()
        return obj
