"""
Module contains definition of ScheduleEntry
"""

from datetime import datetime, timedelta
import sqlite3
from dbobj.helperfunctions import HelperFunctions as HF
from dbobj.scheduleseries import ScheduleSeries

class ScheduleEntry():

    """
    Class represents one schedule entry, which can either be
    constant over time or only planed for one day

    If is_planed = 1: entry is planed work, meaning nothing
    fixed like lectures or exercise classes. In this case
    the entry runs from [start_date, start_time] to [end_date, end_time].
    day_of_week is determined using the [start_date].

    If is_planed = 0: entry is scheduled work, like fixed lectures
    or exercise classes. In this case the entry runs weekly from
    [start_time] to [end_time] on the specified day_of_week
    between bounding dates [start_date] and [end_date].

    description may contain anything the user likes.
    """

    def __init__(self, series_obj, start_offset,\
        start_time, end_time, at_date, description):

        self.schedule_entry_id = None
        self.series_obj = series_obj
        self.start_offset = start_offset
        self.start_time = start_time
        self.end_time = end_time
        self.at_date = at_date
        self.description = description

    def __del__(self):
        pass

    def key(self):

        """return uniform schedule entry key"""

        # don't change this without changing the remove_series_by_db_id
        return self.schedule_entry_id

    def extended_copy(self, schedule_entry_id, series_obj, at_date, description):

        """
        return a completed copy that contains the schedule_entry_id, the
        description and the at_date as well
        """

        obj = ScheduleEntry(series_obj, self.start_offset, self.start_time, self.end_time,\
            at_date, description)
        obj.schedule_entry_id = schedule_entry_id
        return obj

    @staticmethod
    def seed(db_connection):

        """create object table in database"""

        # this one must come first according to foreign keys
        ScheduleSeries.seed(db_connection)

        cursor = db_connection.cursor()
        try:
            cursor.execute("""CREATE TABLE ScheduleEntry
                        (ScheduleEntryId integer PRIMARY KEY autoincrement,
                        ScheduleSeriesId integer,
                        StartOffset integer,
                        StartTime integer,
                        EndTime integer,
                        AtDate integer,
                        Description text,
                        CreatedTS DEFAULT CURRENT_TIMESTAMP,
                        ModifiedTS DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (ScheduleSeriesId) REFERENCES Series(ScheduleSeriesId))""")

            cursor.execute(\
                "CREATE INDEX ScheduleEntry_SeriesId_I ON ScheduleEntry (ScheduleSeriesId)")
            cursor.execute(\
                "CREATE INDEX ScheduleEntry_AtDate_I ON ScheduleEntry (AtDate)")

        except sqlite3.Error as error:
            print("ScheduleEntry.Seeding " + str(ScheduleEntry.__class__) +\
                " error:", error.args[0])
            raise

    @staticmethod
    def new(series_obj, start_offset,\
        start_time, end_time, at_date, description):

        """Create a new instance"""

        return ScheduleEntry(series_obj, start_offset,\
            start_time, end_time, at_date, description)

    @staticmethod
    def __create_entry_series(schedule_obj, series_id, start_date, end_date, cursor):

        """
        Create schedule entry series
        (don't use outside of ScheduleEntry)
        """

        c_date = start_date
        c_dow = c_date.weekday()

        at_date = schedule_obj.at_date
        at_dow = at_date.weekday()
        dow_diff = at_dow - c_dow
        c_at_date = c_date + timedelta(hours=dow_diff*24)
        if c_at_date < c_date:
            c_at_date = c_at_date + timedelta(hours=168)

        start_offset = schedule_obj.start_offset
        start_time = schedule_obj.start_time
        end_time = schedule_obj.end_time
        description = schedule_obj.description

        start_time = HF.time_2_db((datetime.combine(c_date, start_time) -\
            timedelta(hours=start_offset)).time())
        end_time = HF.time_2_db((datetime.combine(c_date, end_time) -\
            timedelta(hours=start_offset)).time())

        obj_list = []
        while c_at_date <= end_date:

            cursor.execute("""INSERT INTO ScheduleEntry
                            (ScheduleSeriesId, StartOffset,
                            StartTime, EndTime, AtDate, Description)
                            VALUES ({0}, {1}, {2}, {3}, {4}, '{5}')""".format(\
                                series_id,\
                                    start_offset,\
                                        start_time,\
                                            end_time,\
                                                HF.date_2_db(c_at_date),\
                                                    HF.escape_quote(description)))

            # use an intermediate list in case of an exception
            obj_list.append(\
                schedule_obj.extended_copy(\
                    cursor.lastrowid, schedule_obj.series_obj.copy(),\
                        c_date, description))

            c_date = c_date + timedelta(hours=168)
            c_at_date = c_at_date + timedelta(hours=168)

        return obj_list

    @staticmethod
    def series_to_db(schedule_obj, obj_dict, db_name):

        """
        Store object to db

        There is no simple to_db here because only series can be created

        Descriptions for single entries may be updated using the
        update_by_db_id method

        The connected series_obj is not shared between all schedule_obj of
        the same series
        """

        connection = sqlite3.connect(db_name)
        cursor = connection.cursor()
        obj_list = []
        try:
            # store one single ScheduleSeries, take id and add it to every
            # subsequent ScheduleEntry
            ScheduleSeries.to_db(schedule_obj.series_obj, connection)

            c_date = schedule_obj.series_obj.start_date
            end_date = schedule_obj.series_obj.end_date

            obj_list = ScheduleEntry.__create_entry_series(\
                schedule_obj, schedule_obj.series_obj.series_id,\
                    c_date, end_date, cursor)

        except sqlite3.Error as error:
            connection.rollback()
            connection.close()
            print("ScheduleEntry.series_to_db " +\
                str(ScheduleEntry.__class__) + " error:", error.args[0])
            raise

        connection.commit()
        connection.close()

        # add object to dict containing all subjects
        for obj in obj_list:
            obj_dict[obj.key()] = obj

    @staticmethod
    def update_entry_by_db_id(obj, db_name):

        """
        Update schedule entry db object using db id

        Allow to update everything except the connected series_obj

        Allow for the case
          1. create a series
          2. change start_time and end_time for some single days
          3. change description for some single days
        """

        connection = sqlite3.connect(db_name)
        cursor = connection.cursor()
        try:
            start_time = (datetime.combine(obj.at_date, obj.start_time) -\
                timedelta(hours=obj.start_offset)).time()
            end_time = (datetime.combine(obj.at_date, obj.end_time) -\
                timedelta(hours=obj.start_offset)).time()

            cursor.execute("""UPDATE ScheduleEntry SET
                              StartOffset = {0},
                              StartTime = {1},
                              EndTime = {2},
                              AtDate = {3},
                              Description = '{4}'
                       WHERE ScheduleEntryId = {5}""".format(\
                           obj.start_offset,\
                               HF.time_2_db(start_time),\
                                   HF.time_2_db(end_time),\
                                       HF.date_2_db(obj.at_date),\
                                           HF.escape_quote(obj.description),\
                                               obj.schedule_entry_id))
        except sqlite3.Error as error:
            connection.rollback()
            connection.close()
            print("ScheduleEntry.update_entry_by_db_id " + str(ScheduleEntry.__class__) +\
                " error:", error.args[0])
            raise

        connection.commit()
        connection.close()

    @staticmethod
    def update_series_by_series_id(obj, obj_dict, db_name):

        """
        Update a series by changing subject, type, description
        or start_date and end_date

        If start_date or end_date have been changed remove entries
        outside of the new range or add new entries
        """

        connection = sqlite3.connect(db_name)
        cursor = connection.cursor()
        series_obj = obj.series_obj
        new_obj_list = []
        try:
            start_date = HF.date_2_db(series_obj.start_date)
            end_date = HF.date_2_db(series_obj.end_date)

            cursor.execute("""SELECT StartDate, EndDate
                              FROM ScheduleSeries
                              WHERE ScheduleSeriesId = {0}""".format(\
                                  series_obj.schedule_series_id))
            rows = cursor.fetchall()

            old_start_date = rows[0][0]
            old_end_date = rows[0][1]

            cursor.execute("""UPDATE ScheduleSeries SET
                              TypeId = {0},
                              SubjectId = {1},
                              StartDate = {2},
                              EndDate = {3},
                              Description = '{4}'
                              WHERE ScheduleSeriesId = {5}""".format(\
                                  series_obj.type_id,\
                                      series_obj.subject_id,\
                                          start_date,\
                                              end_date,\
                                                  HF.escape_quote(series_obj.description),\
                                                      series_obj.schedule_series_id))

            cursor.execute("""UPDATE ScheduleEntry SET
                              Description = '{0}'
                       WHERE ScheduleEntryId = {1}""".format(\
                           HF.escape_quote(obj.description),\
                               obj.schedule_entry_id))

            if old_start_date < start_date:
                # remove entries that are outside of the series span now
                cursor.execute("""DELETE FROM ScheduleEntry
                                WHERE ScheduleSeriesId = {0}
                                    AND AtDate < {1}""".format(\
                                        series_obj.schedule_series_id,\
                                            start_date))
                keys = list(obj_dict.keys())
                for i in keys:
                    if obj_dict[i].at_date < series_obj.start_date:
                        del obj_dict[i]

            elif old_start_date > start_date:
                # create new entries to fill the new series span
                new_end_date = HF.date_2_python_date(old_start_date) -\
                    timedelta(hours=24)

                new_schedule_obj = ScheduleEntry.new(\
                    series_obj,\
                        obj.start_offset,\
                            obj.start_time,\
                                obj.end_time,\
                                    obj.at_date,\
                                        "")

                new_obj_list.extend(\
                    ScheduleEntry.__create_entry_series(\
                        new_schedule_obj, series_obj.schedule_series_id, \
                            series_obj.start_date, new_end_date, cursor))

            if old_end_date > end_date:
                # remove entries that are outside of the series span now
                cursor.execute("""DELETE FROM ScheduleEntry
                                WHERE ScheduleSeriesId = {0}
                                    AND AtDate > {1}""".format(\
                                        series_obj.schedule_series_id,\
                                            end_date))
                keys = list(obj_dict.keys())
                for i in keys:
                    if obj_dict[i].at_date > series_obj.end_date:
                        del obj_dict[i]

            elif old_end_date < end_date:
                # create new entries to fill the new series span
                new_start_date = HF.date_2_python_date(old_end_date) +\
                    timedelta(hours=24)

                new_schedule_obj = ScheduleEntry.new(\
                    series_obj,\
                        obj.start_offset,\
                            obj.start_time,\
                                obj.end_time,\
                                    obj.at_date,\
                                        "")

                new_obj_list.extend(\
                    ScheduleEntry.__create_entry_series(\
                        new_schedule_obj, series_obj.schedule_series_id, \
                            new_start_date, series_obj.end_date, cursor))

        except sqlite3.Error as error:
            connection.rollback()
            connection.close()
            print("ScheduleEntry.update_series_by_series_id " + str(ScheduleEntry.__class__) +\
                " error:", error.args[0])
            raise

        connection.commit()
        connection.close()

        # add object to dict containing all subjects
        for s_obj in new_obj_list:
            obj_dict[s_obj.key()] = s_obj

    @staticmethod
    def reload_from_db(obj_dict, start_date, end_date, db_name):

        """
        Load everything that has at_date within start_date and end_date

        The connected series_obj is not shared between all schedule_obj of
        the same series
        """

        start_date_val = HF.date_2_db(start_date)
        end_date_val = HF.date_2_db(end_date)

        connection = sqlite3.connect(db_name)
        cursor = connection.cursor()
        try:
            # for unscheduled StartDate and EndDate mark the outer boundaries
            # presented by the calendar and the unit needs to be within it
            cursor.execute("""SELECT sen.ScheduleEntryId,
                                     sen.StartOffset,
                                     sen.StartTime,
                                     sen.EndTime,
                                     sen.AtDate,
                                     sen.Description AS Description1,
                                     sse.ScheduleSeriesId,
                                     sse.TypeId,
                                     sse.SubjectId,
                                     sse.StartDate,
                                     sse.EndDate,
                                     sse.Description AS Description2
                              FROM ScheduleEntry sen
                              INNER JOIN ScheduleSeries sse
                                      ON sse.ScheduleSeriesId = sen.ScheduleSeriesId
                              WHERE sen.AtDate >= {0} AND sen.AtDate <= {1}
                              ORDER BY ScheduleEntryId""".format(\
                                  start_date_val,\
                                      end_date_val))

            rows = cursor.fetchall()
            obj_dict.clear()

            for row in rows:
                start_time = HF.time_2_python_time(row[2])
                end_time = HF.time_2_python_time(row[3])
                at_date = HF.date_2_python_date(row[4])

                start_time = (datetime.combine(start_date, start_time) +\
                    timedelta(hours=row[1])).time()
                end_time = (datetime.combine(end_date, end_time) +\
                    timedelta(hours=row[1])).time()

                sse_obj = ScheduleSeries.new(\
                    row[7],\
                        row[8],\
                            HF.date_2_python_date(row[9]),\
                                HF.date_2_python_date(row[10]),\
                                    row[11])
                sse_obj.schedule_series_id = row[6]

                sen_obj = ScheduleEntry.new(\
                    sse_obj,\
                        row[1],\
                            start_time,\
                                end_time,\
                                    at_date,\
                                        row[5])
                sen_obj.schedule_entry_id = row[0]

                obj_dict[sen_obj.key()] = sen_obj
        except sqlite3.Error as error:
            connection.rollback()
            connection.close()
            print("ScheduleEntry.reload_from_db " + str(ScheduleEntry.__class__) +\
                " error:", error.args[0])
            raise
        connection.close()

    @staticmethod
    def delete_entry_by_db_id(obj, obj_dict, db_name):

        """
        Delete schedule_obj from db and from corresponding obj_dict

        Don't delete the connected series_obj, allow for single days to be
        deleted in a series
        """

        connection = sqlite3.connect(db_name)
        cursor = connection.cursor()
        try:
            cursor.execute("""DELETE FROM ScheduleEntry WHERE ScheduleEntryId = {0}""".format(\
                obj.schedule_entry_id))

            del obj_dict[obj.key()]
        except sqlite3.Error as error:
            connection.rollback()
            connection.close()
            print("ScheduleEntry.delete_entry_by_db_id " + str(ScheduleEntry.__class__) +\
                " error:", error.args[0])
            raise

        connection.commit()
        connection.close()

    @staticmethod
    def delete_series_by_db_id(obj, obj_dict, db_name):

        """
        Delete one whole data series

        Delete schedule_obj and series_obj
        """

        connection = sqlite3.connect(db_name)
        cursor = connection.cursor()
        series_id = obj.series_obj.schedule_series_id
        try:
            cursor.execute("""DELETE FROM ScheduleEntry WHERE ScheduleSeriesId = {0}""".format(\
                series_id))

            cursor.execute("""DELETE FROM ScheduleSeries WHERE ScheduleSeriesId = {0}""".format(\
                series_id))

            key_list = list(obj_dict.keys())
            for i in key_list:
                if obj_dict[i].series_obj.schedule_series_id == series_id:
                    del obj_dict[i]

        except sqlite3.Error as error:
            connection.rollback()
            connection.close()
            print("ScheduleEntry.delete_series_by_db_id " + str(ScheduleEntry.__class__) +\
                " error:", error.args[0])
            raise

        connection.commit()
        connection.close()

    @staticmethod
    def remove_series_by_db_id(obj, obj_dict, db_name):

        """
        Remove one series by setting single days to every entry of
        the series and afterwards deleting the series in question

        Deletes series_obj but keeps all schedule_obj
        """

        connection = sqlite3.connect(db_name)
        cursor = connection.cursor()
        series_id = obj.series_obj.schedule_series_id
        change_list = []
        try:
            cursor.execute("""SELECT
                                ScheduleEntryId,
                                AtDate
                              FROM ScheduleEntry
                              WHERE ScheduleSeriesId = {0}
                              ORDER BY AtDate ASC""".format(\
                                  series_id))

            rows = cursor.fetchall()
            for row in rows:
                se_date = HF.date_2_python_date(row[1])
                series_obj = ScheduleSeries.new(\
                    obj.series_obj.type_id,\
                        obj.series_obj.subject_id,\
                            se_date,\
                                se_date,\
                                    obj.series_obj.description)

                ScheduleSeries.to_db(series_obj, connection)

                cursor.execute("""UPDATE ScheduleEntry SET ScheduleSeriesId = {0}
                                  WHERE ScheduleEntryId = {1}""".format(\
                                      series_obj.schedule_series_id, row[0]))

                change_list.append((row[0], series_obj))

            cursor.execute("""DELETE FROM ScheduleSeries WHERE ScheduleSeriesId = {0}""".format(\
                series_id))

        except sqlite3.Error as error:
            connection.rollback()
            connection.close()
            print("ScheduleEntry.remove_series_by_db_id " + str(ScheduleEntry.__class__) +\
                " error:", error.args[0])
            raise

        connection.commit()
        connection.close()

        for obj in change_list:
            obj_dict[obj[0]].series_obj = obj[1]

    @staticmethod
    def remove_entry_from_series_by_db_id(obj, db_name):

        """
        Remove the series_obj from one entry and create a new series_obj
        for that entry with just one day

        Leave the series untouched except for that
        """

        connection = sqlite3.connect(db_name)
        cursor = connection.cursor()
        series_obj = None
        try:
            series_obj = ScheduleSeries.new(\
                obj.series_obj.type_id,\
                    obj.series_obj.subject_id,\
                        obj.at_date,\
                            obj.at_date,\
                                obj.series_obj.description)

            ScheduleSeries.to_db(series_obj, connection)

            cursor.execute("""UPDATE ScheduleEntry SET ScheduleSeriesId = {0}
                                WHERE ScheduleEntryId = {1}""".format(\
                                    series_obj.schedule_series_id,\
                                        obj.schedule_entry_id))

        except sqlite3.Error as error:
            connection.rollback()
            connection.close()
            print("ScheduleEntry.remove_entry_from_series_by_db_id " +\
                str(ScheduleEntry.__class__) +\
                " error:", error.args[0])
            raise

        connection.commit()
        connection.close()

        obj.series_obj = series_obj

    @staticmethod
    def compare(obj1, obj2):

        """compare two ScheduleEntry objects"""

        return obj1.schedule_entry_id == obj2.schedule_entry_id and\
            obj1.serial_id == obj2.serial_id and\
                obj1.start_offset == obj2.start_offset and\
                    obj1.start_time == obj2.start_time and\
                        obj1.end_time == obj2.end_time and\
                            obj1.at_date == obj2.at_date and\
                                obj1.description == obj2.description and\
                                    ScheduleSeries.compare(obj1.series_obj, obj2.series_obj)
