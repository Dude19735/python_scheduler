# pylint: disable=too-many-lines
"""
Module provides interface to db and corresponding
class entities for data tables
"""

import sqlite3
import os
import shutil
from datetime import datetime, timedelta

from dbobj.dbversion import DBVersion
from dbobj.config import Config
from dbobj.subjectworkunit import SubjectWorkUnit
from dbobj.workunitentry import WorkUnitEntry
from dbobj.scheduleseries import ScheduleSeries
from dbobj.scheduleentry import ScheduleEntry
from dbobj.subjecttype import SubjectType
from dbobj.subject import Subject
from dbobj.todolistitem import TodoListItem
from dbobj.helperfunctions import HelperFunctions as HF

# these don't represent actual db models
# pylint: disable=unused-import
from dbobj.workdaysubjecttimepercentage\
    import WorkDaySubjectTimePercentage
from dbobj.workdaytimeunits import WorkDayTimeUnits
from dbobj.workdaytimepercentage import WorkDayTimePercentage
from dbobj.worktotaltimepercentage import WorkTotalTimePercentage
from dbobj.worksubjecttimepercentage import WorkSubjectTimePercentage
from dbobj.summary import Summary
from dbobj.unittypes import UnitTypes
from dbobj.subjecttypes import SubjectTypes

# TODO: write tests for update_by_db_id

# db interface classes and entities
class DB():

    """
    Class represents one database interface manager
    """

    def __init__(self, db_name):
        self.db_name = db_name

    def init(self):

        """insert initial data into db"""

        print("initializing content...")
        connection = sqlite3.connect(self.db_name)
        Subject.init(connection)
        SubjectType.init(connection)
        connection.commit()
        connection.close()

    def seed(self, software_version, db_version):

        """seed new empty database"""

        if software_version == db_version:
            return False

        diff = 0.01
        connection = sqlite3.connect(self.db_name)
        while software_version >= db_version:
            # Version 1.0
            # do all seedings from the start and change db version on the fly
            # no need for special data migrations
            if db_version == 1.0 - diff:
                DBVersion.seed(connection)
                Subject.seed(connection)
                SubjectType.seed(connection)
                ScheduleEntry.seed(connection)
                WorkUnitEntry.seed(connection)
                SubjectWorkUnit.seed(connection)

                DBVersion.create_new_version(\
                    "Initial seed",\
                        db_version + diff,\
                            self.db_name)
                db_version = db_version + diff

                # initial migrations for 1.01
                Config.seed(connection)

                DBVersion.create_new_version(\
                    "Create Config table",\
                        db_version + diff,\
                            self.db_name)
                db_version = db_version + diff

                # initial migrations for 1.02
                TodoListItem.seed(connection)

                DBVersion.create_new_version(\
                    "Create TodoListItem",\
                        db_version + diff,\
                            self.db_name)
                db_version = db_version + diff

                # initial migrations for 1.03
                DBVersion.create_new_version(\
                    "Remove scheduled entries",\
                        db_version + diff,\
                            self.db_name)
                db_version = db_version + diff

                # initial migrations for 1.04
                DBVersion.create_new_version(\
                    "Add active flag for Subjects",\
                        db_version + diff,\
                            self.db_name)
                db_version = db_version + diff

                # initial migrations for 1.05
                DBVersion.create_new_version(\
                    "Add SubjectType",\
                        db_version + diff,\
                            self.db_name)
                db_version = db_version + diff

            # Version 1.01
            if db_version == 1.01 - diff:
                Config.seed(connection)

                DBVersion.create_new_version(\
                    "Create Config table",\
                        db_version + diff,\
                            self.db_name)

            # Version 1.02
            if db_version == 1.02 - diff:
                TodoListItem.seed(connection)

                DBVersion.create_new_version(\
                    "Create TodoListItem",\
                        db_version + diff,\
                            self.db_name)

            if db_version == 1.03 - diff:

                shutil.copyfile("data.db", "data.db.old")
                try:
                    stmt_check = """SELECT name FROM sqlite_master
                                    WHERE type IN ('table', 'index')
                                      AND name IN ('{0}', '{1}', '{2}', '{3}', '{4}', '{5}')"""

                    stmt_schedule_1 = "ALTER TABLE ScheduleEntry RENAME TO ScheduleEntryOld"
                    stmt_schedule_2 = "DROP INDEX ScheduleEntry_SeriesId_I"
                    stmt_schedule_3 = "DROP INDEX ScheduleEntry_AtDate_I"
                    stmt_series_1 = "ALTER TABLE ScheduleSeries RENAME TO ScheduleSeriesOld"
                    stmt_series_2 = "DROP INDEX ScheduleSeries_DateIndex_I"
                    stmt_series_3 = "DROP INDEX ScheduleSeries_EndDate_I"
                    cursor = connection.cursor()

                    cursor.execute(stmt_check.format(\
                        "ScheduleEntry",\
                            "ScheduleSeries",\
                                "ScheduleEntry_SeriesId_I",\
                                    "ScheduleEntry_AtDate_I",\
                                        "ScheduleSeries_DateIndex_I",\
                                            "ScheduleSeries_EndDate_I"))
                    check_rows = cursor.fetchall()

                    for row in check_rows:
                        if row[0] == "ScheduleEntry":
                            cursor.execute(stmt_schedule_1)
                        elif row[0] == "ScheduleEntry_SeriesId_I":
                            cursor.execute(stmt_schedule_2)
                        elif row[0] == "ScheduleEntry_AtDate_I":
                            cursor.execute(stmt_schedule_3)
                        elif row[0] == "ScheduleSeries":
                            cursor.execute(stmt_series_1)
                        elif row[0] == "ScheduleSeries_DateIndex_I":
                            cursor.execute(stmt_series_2)
                        elif row[0] == "ScheduleSeries_EndDate_I":
                            cursor.execute(stmt_series_3)

                    ScheduleEntry.seed(connection)

                    stmt_select =\
                        """
                        SELECT
                          TypeId,
                          SubjectId,
                          StartOffset,
                          StartTime,
                          EndTime,
                          StartDate,
                          EndDate,
                          Description,
                          IsScheduled,
                          DayOfWeek
                        FROM ScheduleEntryOld
                        ORDER BY ScheduleEntryId ASC
                        """

                    # do one commit here, since if something fails here, we have a backup
                    # of the db file
                    connection.commit()

                    print("Migrate ScheduleEntry... ")
                    cursor.execute(stmt_select)
                    rows = cursor.fetchall()
                    for row in rows:

                        is_scheduled = row[8]
                        day_of_week = row[9]
                        start_offset = row[2]
                        start_date = HF.date_2_python_date(row[5])
                        end_date = HF.date_2_python_date(row[6])

                        if is_scheduled == 1:
                            start_date = start_date + timedelta(hours=(day_of_week-1)*24)

                        start_time = HF.time_2_python_time(row[3])
                        end_time = HF.time_2_python_time(row[4])

                        start_time = (datetime.combine(start_date, start_time) +\
                            timedelta(hours=start_offset)).time()
                        end_time = (datetime.combine(start_date, end_time) +\
                            timedelta(hours=start_offset)).time()

                        series_obj = ScheduleSeries.new(\
                            row[0], row[1], start_date, end_date, "")

                        schedule_obj =\
                            ScheduleEntry.new(\
                                series_obj, start_offset, start_time, end_time,\
                                    start_date, end_date)
                        obj_dict = dict()
                        schedule_obj.series_to_db(schedule_obj, obj_dict, self.db_name)

                    print(" Complete")

                    print("Create new DB version... ")
                    DBVersion.create_new_version(\
                        "Remove scheduled entries",\
                            db_version + diff,\
                                self.db_name)
                    print(" Complete",)

                    print("Create new indices... ")
                    cursor.execute(\
                        "CREATE INDEX WorkUnitEntry_StartDate_I ON WorkUnitEntry (StartDate)")
                    cursor.execute(\
                        "CREATE INDEX WorkUnitEntry_EndDate_I ON WorkUnitEntry (EndDate)")
                    cursor.execute(\
                        "CREATE INDEX Subject_StartDate_I ON Subject (StartDate)")
                    cursor.execute(\
                        "CREATE INDEX Subject_EndDate_I ON Subject (EndDate)")
                    cursor.execute(\
                        "CREATE INDEX SubjectWorkUnit_AtDate_I ON SubjectWorkUnit (AtDate)")
                    cursor.execute(\
                        "CREATE INDEX SubjectWorkUnit_SubjectId_I ON SubjectWorkUnit (SubjectId)")
                    cursor.execute(\
                        "CREATE INDEX TodoListItem_DeadlineDate_I ON TodoListItem (DeadlineDate)")

                    print(" Complete")

                    print("Drop old ScheduleEntry... ")
                    stmt_schedule_drop_1 = "DROP TABLE ScheduleEntryOld"
                    stmt_series_drop_1 = "DROP TABLE ScheduleSeriesOld"

                    for row in check_rows:
                        if row[0] == "ScheduleEntry":
                            cursor.execute(stmt_schedule_drop_1)
                        elif row[0] == "ScheduleSeries":
                            cursor.execute(stmt_series_drop_1)
                    print(" Complete")

                except:
                    # something went wrong
                    connection.commit()
                    connection.close()
                    raise Exception(\
                        """
                        ********************************
                        Migration to version 1.03 failed
                        ********************************
                        """)

                # migration successfull
                os.remove("data.db.old")

            if db_version == 1.04 - diff:

                stmt1 = "ALTER TABLE Subject ADD Active integer DEFAULT 1"
                stmt2 = "DROP INDEX Subject_StartDate_I"
                stmt3 = "DROP INDEX Subject_EndDate_I"
                stmt4 = "CREATE INDEX Subject_StartDate_I ON Subject (StartDate, Active)"
                stmt5 = "CREATE INDEX Subject_EndDate_I ON Subject (EndDate, Active)"
                cursor = connection.cursor()

                try:
                    cursor.execute(stmt1)
                    cursor.execute(stmt2)
                    cursor.execute(stmt3)
                    cursor.execute(stmt4)
                    cursor.execute(stmt5)

                    DBVersion.create_new_version(\
                    "Add active flag for Subjects",\
                        db_version + diff,\
                            self.db_name)
                except:
                    # something went wrong
                    connection.rollback()
                    connection.close()
                    raise Exception(\
                        """
                        ********************************
                        Migration to version 1.04 failed
                        ********************************
                        """)

            if db_version == 1.05 - diff:

                stmt1 = "ALTER TABLE Subject ADD SubjectType integer DEFAULT 0"
                stmt2 = "CREATE INDEX Subject_Active_I ON Subject (Active)"
                stmt3 = "CREATE INDEX Subject_SubjectType_I ON Subject (SubjectType)"

                stmt4 = "DROP INDEX Subject_StartDate_I"
                stmt5 = "DROP INDEX Subject_EndDate_I"
                stmt6 = "CREATE INDEX Subject_StartDate_I ON Subject (StartDate)"
                stmt7 = "CREATE INDEX Subject_EndDate_I ON Subject (EndDate)"
                stmt8 = "UPDATE Subject SET SubjectType = 1 WHERE Name = 'Study'"

                cursor = connection.cursor()
                try:
                    DBVersion.create_new_version(\
                    "Add SubjectType",\
                        db_version + diff,\
                            self.db_name)

                    cursor.execute(stmt1)
                    cursor.execute(stmt2)
                    cursor.execute(stmt3)
                    cursor.execute(stmt4)
                    cursor.execute(stmt5)
                    cursor.execute(stmt6)
                    cursor.execute(stmt7)
                    cursor.execute(stmt8)
                except:
                    connection.rollback()
                    connection.close()
                    raise Exception(\
                        """
                        ********************************
                        Migration to version 1.05 failed
                        ********************************
                        """)

            if db_version == 1.06 - diff:

                # this migration was sort of included in the initial seed, that's why it only
                # creates a new version here

                cursor = connection.cursor()
                try:
                    DBVersion.create_new_version_extern_conn(\
                        "Add ScheduleEntry WorkUnitEntry connection",\
                            db_version + diff,\
                                connection)
                except:
                    connection.rollback()
                    connection.close()
                    raise Exception(\
                        """
                        ********************************
                        Migration to version 1.06 failed
                        ********************************
                        """)

            db_version = db_version + diff

        connection.commit()
        connection.close()

        with open("./VERSION.INFO", "w") as e_file:
            e_file.write(str(software_version))

        return True
