"""
Module defines TodoListItem
"""

import sqlite3
from dbobj.helperfunctions import HelperFunctions as HF

class TodoListItem():

    """
    Class represents one TodoListItem
    """

    def __init__(self, position, task_complete, task_description, deadline_date):
        self.todo_list_item_id = None
        self.position = position
        self.task_complete = task_complete
        self.task_description = task_description
        self.deadline_date = deadline_date

    def __del__(self):
        pass

    def key(self):

        """return uniform todo list item key"""

        return self.todo_list_item_id

    @staticmethod
    def seed(db_connection): # pylint: disable=invalid-name

        """create object table in database"""

        cursor = db_connection.cursor()
        try:
            cursor.execute("""CREATE TABLE TodoListItem
                        (TodoListItemId integer PRIMARY KEY autoincrement,
                        Position integer,
                        TaskComplete integer,
                        TaskDescription text,
                        DeadlineDate integer,
                        CreatedTS DEFAULT CURRENT_TIMESTAMP,
                        ModifiedTS DEFAULT CURRENT_TIMESTAMP)""")

            cursor.execute(\
                "CREATE INDEX TodoListItem_DeadlineDate_I ON TodoListItem (DeadlineDate)")
        except sqlite3.Error as error:
            print("TodoListItem.Seeding " + str(TodoListItem.__class__) +\
                " error:", error.args[0])
            raise

    @staticmethod
    def new(position, task_complete, task_description, deadline_date):

        """Create new TodoListItem obj"""

        return TodoListItem(position, task_complete, task_description, deadline_date)

    @staticmethod
    def to_db(obj, obj_dict, db_name):

        """store object to db"""

        connection = sqlite3.connect(db_name)
        cursor = connection.cursor()
        try:
            cursor.execute("""INSERT INTO TodoListItem
                              (Position, TaskComplete, TaskDescription, DeadlineDate)
                       VALUES ({0}, {1}, '{2}', {3})""".format(\
                           obj.position,\
                               obj.task_complete,\
                                   HF.escape_quote(obj.task_description),\
                                       HF.date_2_db(obj.deadline_date)))
        except sqlite3.Error as error:
            connection.rollback()
            connection.close()
            print("TodoListItem.to_db " + str(TodoListItem.__class__) + " error:", error.args[0])
            raise

        connection.commit()
        connection.close()

        # add object to dict containing all subjects
        obj.todo_list_item_id = cursor.lastrowid
        obj_dict[obj.key()] = obj

    @staticmethod
    def update_by_db_id(obj, db_name):

        """update existing object using db id"""

        connection = sqlite3.connect(db_name)
        cursor = connection.cursor()
        try:
            cursor.execute("""UPDATE TodoListItem set
                              Position = {0},
                              TaskComplete = {1},
                              TaskDescription = '{2}',
                              DeadlineDate = {3}
                       WHERE TodoListItemId = {4}""".format(\
                           obj.position,\
                               obj.task_complete,\
                                   HF.escape_quote(obj.task_description),\
                                       HF.date_2_db(obj.deadline_date),\
                                           obj.todo_list_item_id))
        except sqlite3.Error as error:
            connection.rollback()
            connection.close()
            print("TodoListItem.update_by_db_id " +\
                str(TodoListItem.__class__) + " error:", error.args[0])
            raise

        connection.commit()
        connection.close()

    @staticmethod
    def update_all_positions(obj_dict, db_name):

        """update position field of all current db entries"""

        prototype =\
            """
            UPDATE TodoListItem SET Position = {0}
            WHERE TodoListItemId = {1}
            """

        stmt_list = []
        for i in obj_dict.values():
            stmt_list.append(prototype.format(i.position, i.todo_list_item_id))

        connection = sqlite3.connect(db_name)
        cursor = connection.cursor()
        try:
            for i in stmt_list:
                cursor.execute(i)
        except sqlite3.Error as error:
            connection.rollback()
            connection.close()
            print("TodoListItem.update_all_positions " + str(TodoListItem.__class__) +\
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
            cursor.execute("""SELECT TodoListItemId, Position, TaskComplete,
                                        TaskDescription, DeadlineDate
                            FROM TodoListItem
                            ORDER BY Position asc""")

            rows = cursor.fetchall()
            obj_dict.clear()
            for row in rows:
                obj = TodoListItem.new(\
                    row[1],\
                        row[2],\
                            row[3],\
                                HF.date_2_python_date(row[4]))

                obj.todo_list_item_id = row[0]
                obj_dict[obj.key()] = obj
        except sqlite3.Error as error:
            connection.rollback()
            connection.close()
            print("TodoListItem.reload_from_db " + str(TodoListItem.__class__) +\
                " error:", error.args[0])
            raise

        connection.close()

    @staticmethod
    def delete_all_completed(obj_dict, db_name):

        """delete obj from db and from corresponding obj_dict"""

        connection = sqlite3.connect(db_name)
        cursor = connection.cursor()
        try:
            cursor.execute("""DELETE FROM TodoListItem WHERE TaskComplete = 1""")

            val_list = list(obj_dict.values())
            for i in val_list:
                if i.task_complete:
                    del obj_dict[i.key()]
        except sqlite3.Error as error:
            connection.rollback()
            connection.close()
            print("TodoListItem.delete_all_completed " + str(TodoListItem.__class__) +\
                " error:", error.args[0])
            raise

        connection.commit()
        connection.close()

    @staticmethod
    def compare(obj1, obj2):

        """compare two ScheduleEntry objects"""

        return obj1.todo_list_item_id == obj2.todo_list_item_id and\
            obj1.position == obj2.position and\
                obj1.task_complete == obj2.task_complete and\
                    obj1.task_description == obj2.task_description and\
                        obj1.deadline_date == obj2.deadline_date
