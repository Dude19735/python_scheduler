"""
Module contains definition of Config
"""

import sqlite3

class Config():

    """
    Class represents one configuration set
    """

    def __init__(self, name, description, type_id, value):
        self.config_id = None
        self.name = name
        self.description = description
        self.type_id = type_id
        self.value = value

    def __del__(self):
        pass

    def key(self):

        """return uniform key for config entry"""

        return self.config_id

    @staticmethod
    def seed(db_connection): # pylint: disable=invalid-name

        """create object table in database"""

        cursor = db_connection.cursor()
        try:
            cursor.execute("""CREATE TABLE Config
                        (ConfigId integer PRIMARY KEY autoincrement,
                        Name text,         
                        Description text,
                        TypeId integer,
                        Value text,
                        CreatedTS DEFAULT CURRENT_TIMESTAMP,
                        ModifiedTS DEFAULT CURRENT_TIMESTAMP,
                        UNIQUE(Name, TypeId))""")
        except sqlite3.Error as error:
            print("Seeding " + str(Config.__class__) + " error:", error.args[0])
            raise

    @staticmethod
    def new(name, description, type_id, value): # pylint: disable=invalid-name

        """Create a new instance"""

        return Config(name, description, type_id, value)

    @staticmethod
    def to_db(obj, obj_dict, db_name):

        """store object to db"""

        connection = sqlite3.connect(db_name)
        cursor = connection.cursor()
        try:
            cursor.execute("""INSERT INTO Config
                              (Name, Description, TypeId, Value)
                       VALUES ('{0}', '{1}', {2}, '{3}')""".format(\
                           obj.name,\
                               obj.description,\
                                   obj.type_id,\
                                       obj.value))
        except sqlite3.Error as error:
            connection.rollback()
            connection.close()
            print("Config.to_db " + str(Config.__class__) + " error:", error.args[0])
            raise

        connection.commit()
        connection.close()

        # add object to dict containing all subjects
        obj.config_id = cursor.lastrowid
        obj_dict[obj.key()] = obj

    @staticmethod
    def update_by_db_id(obj, db_name):

        """update object using db id"""

        connection = sqlite3.connect(db_name)
        cursor = connection.cursor()
        try:
            cursor.execute("""UPDATE Config SET
                              Name = '{0}',
                              Description = '{1}',
                              TypeId = {2},
                              Value = '{3}'
                       WHERE ConfigId = {4}""".format(\
                           obj.name,\
                               obj.description,\
                                   obj.type_id,\
                                       obj.value,\
                                           obj.config_id))
        except sqlite3.Error as error:
            connection.rollback()
            connection.close()
            print("Config.update_by_db_id " + str(Config.__class__) +\
                " error:", error.args[0])
            raise

        connection.commit()
        connection.close()

    @staticmethod
    def reload_from_db(obj_dict, db_name):

        """load all objects of this type from db"""

        connection = sqlite3.connect(db_name)
        cursor = connection.cursor()
        try:
            cursor.execute("""SELECT ConfigId, Name, Description, TypeId, Value
                              FROM Config 
                              ORDER BY ConfigId""")
            rows = cursor.fetchall()
            obj_dict.clear()
            for row in rows:
                obj = Config.new(\
                    row[1],\
                        row[2],\
                            row[3],\
                                row[4])

                obj.config_id = row[0]
                obj_dict[obj.key()] = obj
        except sqlite3.Error as error:
            connection.close()
            print("Config.reload_from_db " + str(Config.__class__) + " error:", error.args[0])
            raise

        connection.close()

    @staticmethod
    def delete_by_db_id(obj, obj_dict, db_name):

        """delete obj from db and from corresponding obj_dict"""

        connection = sqlite3.connect(db_name)
        cursor = connection.cursor()
        try:
            cursor.execute("""DELETE FROM Config WHERE ConfigId = {0}""".format(\
                obj.work_unit_entry_id))

            del obj_dict[obj.key()]
        except sqlite3.Error as error:
            connection.rollback()
            connection.close()
            print("Config.delete_by_db_id " + str(Config.__class__) + " error:", error.args[0])
            raise

        connection.commit()
        connection.close()

    @staticmethod
    def compare(obj1, obj2):

        """compare two Config objects"""

        return obj1.config_id == obj2.config_id and\
            obj1.name == obj2.name and\
                obj1.description == obj2.description and\
                    obj1.type_id == obj2.type_id and\
                        obj1.value == obj2.value
