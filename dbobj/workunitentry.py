"""
Module contains definition of WorkUnitEntry
"""

from datetime import datetime, timedelta, time
import sqlite3
from dbobj.helperfunctions import HelperFunctions as HF

class WorkUnitEntry():

    """
    Class represents one work unit entry which is one worked
    worked time unit with from-to times and subject
    """

    def __init__(self, type_id, subject_id, schedule_entry_id, unit_type, start_offset,\
        start_time, start_date, end_time, end_date, state, description):

        self.work_unit_entry_id = None
        self.type_id = type_id
        self.subject_id = subject_id
        self.schedule_entry_id = schedule_entry_id
        self.unit_type = unit_type
        self.start_offset = start_offset
        self.start_time = start_time
        self.start_date = start_date
        self.end_time = end_time
        self.end_date = end_date
        self.time_diff = (datetime.combine(end_date, end_time) -\
            datetime.combine(start_date, start_time)).seconds
        self.state = state
        self.description = description

    def __del__(self):
        pass

    def key(self):

        """return uniform key for work unit entry"""

        return self.work_unit_entry_id

    @staticmethod
    def seed(db_connection): # pylint: disable=invalid-name

        """create object table in database"""

        cursor = db_connection.cursor()
        try:
            cursor.execute("""CREATE TABLE WorkUnitEntry
                        (WorkUnitEntryId integer PRIMARY KEY autoincrement,
                        TypeId integer,
                        SubjectId integer,
                        ScheduleEntryId integer DEFAULT 0,
                        UnitType integer,
                        StartOffset integer,
                        StartTime integer,
                        StartDate integer,
                        EndTime integer,
                        EndDate integer,
                        TimeDiff integer,
                        State integer,
                        Description text,
                        CreatedTS DEFAULT CURRENT_TIMESTAMP,
                        ModifiedTS DEFAULT CURRENT_TIMESTAMP)""")

            cursor.execute("CREATE INDEX WorkUnitEntry_StartDate_I ON WorkUnitEntry (StartDate)")
            cursor.execute("CREATE INDEX WorkUnitEntry_EndDate_I ON WorkUnitEntry (EndDate)")
            cursor.execute(\
                "CREATE INDEX WorkUnitEntry_ScheduleId_I ON WorkUnitEntry (ScheduleEntryId)")
        except sqlite3.Error as error:
            print("Seeding " + str(WorkUnitEntry.__class__) + " error:", error.args[0])
            raise

    @staticmethod
    def new(type_id, subject_id, schedule_entry_id, unit_type, start_offset,\
        start_time, start_date, end_time, end_date, state, description): # pylint: disable=invalid-name

        """Create a new instance"""

        return WorkUnitEntry(type_id, subject_id, schedule_entry_id,\
            unit_type, start_offset, start_time, start_date, end_time,\
                end_date, state, description)

    @staticmethod
    def to_db(obj, obj_dict, db_name):

        """store object to db"""

        connection = sqlite3.connect(db_name)
        cursor = connection.cursor()
        try:
            start_datetime = (datetime.combine(obj.start_date, obj.start_time) -\
                timedelta(hours=obj.start_offset))
            end_datetime = (datetime.combine(obj.end_date, obj.end_time) -\
                timedelta(hours=obj.start_offset))
            time_diff = (end_datetime - start_datetime).seconds

            # if we are crazy and work over the 5am threshhold, we need to separate
            # work entries in order to have them separated nicely on the schedule display
            if start_datetime.date() != end_datetime.date():
                cursor.execute("""INSERT INTO WorkUnitEntry
                                 (TypeId, SubjectId, ScheduleEntryId, UnitType, StartOffset,
                                  StartTime, StartDate, EndTime, EndDate, TimeDiff,
                                  State, Description)
                    VALUES ({0}, {1}, {2}, {3}, {4}, {5}, {6},
                            {7}, {8}, {9}, {10}, '{11}')""".format(\
                        obj.type_id,\
                            obj.subject_id,\
                                obj.schedule_entry_id,\
                                    obj.unit_type,\
                                        obj.start_offset,\
                                            HF.time_2_db(start_datetime.time()),\
                                                HF.date_2_db(start_datetime.date()),\
                                                    HF.time_2_db(time(23, 39)),\
                                                        HF.date_2_db(start_datetime.date()),\
                                                            time_diff,\
                                                                obj.state,\
                                                                    HF.escape_quote(obj.description)))
                cursor.execute("""INSERT INTO WorkUnitEntry
                                (TypeId, SubjectId, ScheduleEntryId, UnitType, StartOffset,
                                StartTime, StartDate, EndTime, EndDate, TimeDiff,
                                State, Description)
                    VALUES ({0}, {1}, {2}, {3}, {4}, {5}, {6},
                            {7}, {8}, {9}, {10}, '{11}')""".format(\
                        obj.type_id,\
                            obj.subject_id,\
                                obj.schedule_entry_id,\
                                    obj.unit_type,\
                                        obj.start_offset,\
                                            HF.time_2_db(time(0, 0)),\
                                                HF.date_2_db(end_datetime.date()),\
                                                    HF.time_2_db(end_datetime.time()),\
                                                        HF.date_2_db(end_datetime.date()),\
                                                            time_diff,\
                                                                obj.state,\
                                                                    HF.escape_quote(obj.description)))
            else:
                cursor.execute("""INSERT INTO WorkUnitEntry
                                (TypeId, SubjectId, ScheduleEntryId, UnitType, StartOffset,
                                StartTime, StartDate, EndTime, EndDate, TimeDiff,
                                State, Description)
                    VALUES ({0}, {1}, {2}, {3}, {4}, {5}, {6},
                            {7}, {8}, {9}, {10}, '{11}')""".format(\
                        obj.type_id,\
                            obj.subject_id,\
                                obj.schedule_entry_id,\
                                    obj.unit_type,\
                                        obj.start_offset,\
                                            HF.time_2_db(start_datetime.time()),\
                                                HF.date_2_db(start_datetime.date()),\
                                                    HF.time_2_db(end_datetime.time()),\
                                                        HF.date_2_db(end_datetime.date()),\
                                                            time_diff,\
                                                                obj.state,\
                                                                    HF.escape_quote(obj.description)))
        except sqlite3.Error as error:
            connection.rollback()
            connection.close()
            print("WorkUnitEntry.to_db " + str(WorkUnitEntry.__class__) + " error:", error.args[0])
            raise

        connection.commit()
        connection.close()

        # add object to dict containing all subjects
        obj.work_unit_entry_id = cursor.lastrowid
        obj_dict[obj.key()] = obj

    @staticmethod
    def update_by_db_id(obj, db_name):

        """update object by db id"""

        connection = sqlite3.connect(db_name)
        cursor = connection.cursor()
        try:
            start_datetime = (datetime.combine(obj.start_date, obj.start_time) -\
                timedelta(hours=obj.start_offset))
            end_datetime = (datetime.combine(obj.end_date, obj.end_time) -\
                timedelta(hours=obj.start_offset))
            time_diff = (end_datetime - start_datetime).seconds

            cursor.execute("""UPDATE WorkUnitEntry SET
                              TypeId = {0},
                              SubjectId = {1},
                              ScheduleEntryId = {2},
                              UnitType = {3},
                              StartOffset = {4},
                              StartTime = {5},
                              StartDate = {6},
                              EndTime = {7},
                              EndDate = {8},
                              TimeDiff = {9},
                              State = {10},
                              Description = '{11}'
                       WHERE WorkUnitEntryId = {12}""".format(\
                           obj.type_id,\
                               obj.subject_id,\
                                   obj.schedule_entry_id,\
                                    obj.unit_type,\
                                        obj.start_offset,\
                                               HF.time_2_db(start_datetime.time()),\
                                                   HF.date_2_db(start_datetime.date()),\
                                                       HF.time_2_db(end_datetime.time()),\
                                                           HF.date_2_db(end_datetime.date()),\
                                                               time_diff,\
                                                                   obj.state,\
                                                                       HF.escape_quote(obj.description),\
                                                                           obj.work_unit_entry_id))
        except sqlite3.Error as error:
            connection.rollback()
            connection.close()
            print("WorkUnitEntry.update_by_db_id " + str(WorkUnitEntry.__class__) +\
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
            cursor.execute("""SELECT WorkUnitEntryId, TypeId, SubjectId, ScheduleEntryId, UnitType,
                              StartOffset, StartTime, StartDate, EndTime, EndDate, TimeDiff,
                              State, Description
                              FROM WorkUnitEntry WHERE StartDate <= {0}
                                             AND EndDate >= {1}
                              ORDER BY WorkUnitEntryId""".format(\
                                                 start_date_val,\
                                                     end_date_val))
            rows = cursor.fetchall()
            obj_dict.clear()
            for row in rows:
                start_time = HF.time_2_python_time(row[5])
                start_date = HF.date_2_python_date(row[6])
                end_time = HF.time_2_python_time(row[7])
                end_date = HF.date_2_python_date(row[8])

                start_time = (datetime.combine(start_date, start_time) +\
                    timedelta(hours=row[4])).time()
                end_time = (datetime.combine(end_date, end_time) +\
                    timedelta(hours=row[4])).time()

                obj = WorkUnitEntry.new(\
                    row[1],\
                        row[2],\
                            row[3],\
                                row[4],\
                                    row[5],\
                                        start_time,\
                                            start_date,\
                                                end_time,\
                                                    end_date,\
                                                        row[11],\
                                                            row[12])

                obj.work_unit_entry_id = row[0]
                # takes the old value and overrides the new one on purpose!
                obj.time_diff = row[10]
                obj_dict[obj.key()] = obj
        except sqlite3.Error as error:
            connection.rollback()
            connection.close()
            print("WorkUnitEntry.reload_from_db " + str(WorkUnitEntry.__class__) +\
                " error:", error.args[0])
            raise

        connection.close()

    @staticmethod
    def load_entry_from_db(obj_properties, db_name):

        """load single object of this type from db"""

        connection = sqlite3.connect(db_name)
        cursor = connection.cursor()
        obj = None
        try:
            cursor.execute("""SELECT WorkUnitEntryId, TypeId, SubjectId, ScheduleEntryId,
                              UnitType, StartOffset, StartTime, StartDate, EndTime, EndDate,
                              TimeDiff, State, Description
                              FROM WorkUnitEntry
                              WHERE ScheduleEntryId = {0}
                              LIMIT 1""".format(obj_properties.schedule_entry_id))

            rows = cursor.fetchall()
            for row in rows:
                start_time = HF.time_2_python_time(row[6])
                start_date = HF.date_2_python_date(row[7])
                end_time = HF.time_2_python_time(row[8])
                end_date = HF.date_2_python_date(row[9])

                start_time = (datetime.combine(start_date, start_time) +\
                    timedelta(hours=row[5])).time()
                end_time = (datetime.combine(end_date, end_time) +\
                    timedelta(hours=row[5])).time()

                obj = WorkUnitEntry.new(\
                    row[1],\
                        row[2],\
                            row[3],\
                                row[4],\
                                    row[5],\
                                        start_time,\
                                            start_date,\
                                                end_time,\
                                                    end_date,\
                                                        row[11],\
                                                            row[12])

                obj.work_unit_entry_id = row[0]
                # takes the old value and overrides the new one on purpose!
                obj.time_diff = row[10]
        except sqlite3.Error as error:
            connection.rollback()
            connection.close()
            print("WorkUnitEntry.load_entry_from_db " + str(WorkUnitEntry.__class__) +\
                " error:", error.args[0])
            raise

        connection.close()
        return obj

    @staticmethod
    def delete_by_db_id(obj, obj_dict, date_format, db_name):

        """delete obj from db and from corresponding obj_dict"""

        connection = sqlite3.connect(db_name)
        cursor = connection.cursor()
        try:
            cursor.execute("""DELETE FROM WorkUnitEntry WHERE WorkUnitEntryId = {0}""".format(\
                obj.work_unit_entry_id))

            date_key = obj.start_date.strftime(date_format)
            if date_key in obj_dict.keys():
                obj_list = obj_dict[date_key]
                index = 0
                for i in obj_list:
                    if i.work_unit_entry_id == obj.work_unit_entry_id:
                        del obj_list[index]
                        break
                    index = index + 1

                if not obj_list:
                    del obj_dict[date_key]
        except sqlite3.Error as error:
            connection.rollback()
            connection.close()
            print("WorkUnitEntry.delete_by_db_id " + str(WorkUnitEntry.__class__) +\
                " error:", error.args[0])
            raise

        connection.commit()
        connection.close()

    @staticmethod
    def compare(obj1, obj2):

        """compare two WorkUnitEntry objects"""

        # obj1.time_diff == obj2.time_diff and\ can't be compared because it always changes
        return obj1.work_unit_entry_id == obj2.work_unit_entry_id and\
            obj1.type_id == obj2.type_id and\
                obj1.subject_id == obj2.subject_id and\
                    obj1.schedule_entry_id == obj2.schedule_entry_id and\
                        obj1.unit_type == obj2.unit_type and\
                            obj1.start_offset == obj2.start_offset and\
                                obj1.start_time == obj2.start_time and\
                                    obj1.start_date == obj2.start_date and\
                                        obj1.end_time == obj2.end_time and\
                                            obj1.end_date == obj2.end_date and\
                                                obj1.state == obj2.state and\
                                                    obj1.description == obj2.description
