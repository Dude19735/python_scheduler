"""
Contains test data initializations for global context
"""

from datetime import date, time, timedelta, datetime
from PyQt6.QtGui import QColor
# from dbobj.dbversion import DBVersion
# from dbobj.config import Config
from dbobj.subjectworkunit import SubjectWorkUnit
# from dbobj.workunitentry import WorkUnitEntry
from dbobj.scheduleentry import ScheduleEntry
from dbobj.subjecttype import SubjectType
from dbobj.subject import Subject

class TestData():

    """
    Initialize some test data for the given context
    """

    def __init__(self, context):

        self.context = context

    def generate_test_data(self):

        """generate some testdata to work with"""

        db_name = self.context.db_file_name

        # test data for subjects
        Subject.to_db(Subject.new(\
            "Analysis2",\
                "Analysis II",\
                    QColor(200, 0, 0, 150),\
                        date(2019, 9, 17),\
                            date(2019, 12, 20)),\
                                self.context.subjects,\
                                    db_name)

        Subject.to_db(Subject.new(\
            "DiskMat",\
                "Discrete Mathematics",\
                    QColor(0, 200, 0, 150),\
                        date(2019, 9, 17),\
                            date(2019, 12, 20)),\
                                self.context.subjects,\
                                    db_name)

        Subject.to_db(Subject.new(\
            "AlgoDat",\
                "Algorithms and Datastructures",\
                    QColor(0, 0, 200, 150),\
                        date(2019, 9, 17),\
                            date(2019, 12, 20)),\
                                self.context.subjects,\
                                    db_name)

        Subject.to_db(Subject.new(\
            "EProg",\
                "Introduction to Programming",\
                    QColor(200, 200, 0, 150),\
                        date(2019, 9, 17),\
                            date(2019, 12, 20)),\
                                self.context.subjects,\
                                    db_name)

        Subject.to_db(Subject.new(\
            "LinAlg",\
                "Linear Algebra",\
                    QColor(0, 200, 200, 150),\
                        date(2019, 9, 17),\
                            date(2019, 12, 20)),\
                                self.context.subjects,\
                                    db_name)

        Subject.to_db(Subject.new(\
            "ChFp",\
                "Swiss foreign policy",\
                    QColor(50, 10, 200, 150),\
                        date(2019, 9, 17),\
                            date(2019, 12, 20)),\
                                self.context.subjects,\
                                    db_name)

        Subject.to_db(Subject.new(\
            "CybSec",\
                "Cyber Security",\
                    QColor(50, 200, 50, 150),\
                        date(2019, 9, 17),\
                            date(2019, 12, 20)),\
                                self.context.subjects,\
                                    db_name)

        Subject.to_db(Subject.new(\
            "Study",\
                "Study",\
                    QColor(180, 180, 180, 150),\
                        date(2019, 9, 17),\
                            date(2019, 12, 20)),\
                                self.context.subjects,\
                                    db_name)


        SubjectType.to_db(SubjectType.new("V", "Lecture"), self.context.subject_types, db_name)
        SubjectType.to_db(SubjectType.new("U", "Excercise"), self.context.subject_types, db_name)
        SubjectType.to_db(SubjectType.new("C", "Coffee"), self.context.subject_types, db_name)
        SubjectType.to_db(SubjectType.new("F", "Free Work"), self.context.subject_types, db_name)

        u_type_id = 0
        v_type_id = 0
        for i in self.context.subject_types.items():
            if i[1].name == "U":
                u_type_id = i[0]
            elif i[1].name == "V":
                v_type_id = i[0]

        algo_subject_id = 0
        analysis_subject_id = 0
        for i in self.context.subjects.items():
            if i[1].name == "AlgoDat":
                algo_subject_id = i[0]
            elif i[1].name == "Analysis2":
                analysis_subject_id = i[0]

        # ScheduleEntry.to_db(\
        #     ScheduleEntry.new(u_type_id, 0, algo_subject_id, 1, 5,\
        #         time(hour=8, minute=0), date(2019, 9, 17),\
        #         time(hour=12, minute=0), date(2020, 2, 1), ""),\
        #             self.context.schedule_entries,\
        #                 db_name)

        # ScheduleEntry.to_db(\
        #     ScheduleEntry.new(u_type_id, 0, analysis_subject_id, 1, 5,\
        #         time(hour=13, minute=0), date(2019, 9, 17),\
        #             time(hour=15, minute=0), date(2020, 2, 1), ""),\
        #             self.context.schedule_entries,\
        #                 db_name)

        # ScheduleEntry.to_db(\
        #     ScheduleEntry.new(v_type_id, 4, analysis_subject_id, 1, 5,\
        #         time(hour=13, minute=0), date(2019, 9, 17),\
        #         time(hour=15, minute=0), date(2020, 2, 1), ""),\
        #             self.context.schedule_entries,\
        #                 db_name)

        # SubjectWorkUnit.to_db(\
        #     SubjectWorkUnit.new(1, 3, date(2019, 9, 17), date(2019, 10, 5), "test"),\
        #         self.context.subject_work_units,\
        #             db_name)
        # SubjectWorkUnit.to_db(\
        #     SubjectWorkUnit.new(2, 3, date(2019, 9, 17), date(2019, 10, 5), "test"),\
        #         self.context.subject_work_units,\
        #             db_name)
        # SubjectWorkUnit.to_db(\
        #     SubjectWorkUnit.new(3, 3, date(2019, 9, 17), date(2019, 10, 5), "test"),\
        #         self.context.subject_work_units,\
        #             db_name)
        # SubjectWorkUnit.to_db(\
        #     SubjectWorkUnit.new(4, 3, date(2019, 9, 17), date(2019, 10, 5), "test"),\
        #         self.context.subject_work_units,\
        #             db_name)
        # SubjectWorkUnit.to_db(\
        #     SubjectWorkUnit.new(5, 3, date(2019, 9, 17), date(2019, 10, 5), "test"),\
        #         self.context.subject_work_units,\
        #             db_name)

        # SubjectWorkUnit.to_db(\
        #     SubjectWorkUnit.new(1, 3, date(2019, 9, 17), date(2019, 10, 4), "test"),\
        #         self.context.subject_work_units,\
        #             db_name)
        # SubjectWorkUnit.to_db(\
        #     SubjectWorkUnit.new(2, 3, date(2019, 9, 17), date(2019, 10, 3), "test"),\
        #         self.context.subject_work_units,\
        #             db_name)
        # SubjectWorkUnit.to_db(\
        #     SubjectWorkUnit.new(3, 3, date(2019, 9, 17), date(2019, 10, 2), "test"),\
        #         self.context.subject_work_units,\
        #             db_name)
        # SubjectWorkUnit.to_db(\
        #     SubjectWorkUnit.new(4, 3, date(2019, 9, 17), date(2019, 10, 4), "test"),\
        #         self.context.subject_work_units,\
        #             db_name)
        # SubjectWorkUnit.to_db(\
        #     SubjectWorkUnit.new(5, 3, date(2019, 9, 17), date(2019, 10, 3), "test"),\
        #         self.context.subject_work_units,\
        #             db_name)

        return True

    def reload_data_to_dict(self):

        """reload all data into different dictionaries in order to compare"""

        # start_date = date(2019, 9, 17)
        # end_date = date(2020, 2, 1)
        # db_name = self.context.db_file_name

        # new_subjects = dict()
        # Subject.reload_from_db(new_subjects, start_date, end_date, db_name)

        # new_subject_types = dict()
        # SubjectType.reload_from_db(new_subject_types, db_name)

        # new_schedule_entries = dict()
        # ScheduleEntry.reload_from_db(new_schedule_entries, start_date, end_date, 1, True, db_name)
        # ScheduleEntry.reload_from_db(new_schedule_entries, start_date, end_date, 0, False, db_name)

        # new_subject_work_units = dict()
        # SubjectWorkUnit.reload_from_db(new_subject_work_units, start_date, end_date, db_name)

        # # compare keys first
        # old_subjects = self.context.subjects
        # comp_subjects = new_subjects.keys() == old_subjects.keys()
        # for i in old_subjects.keys():
        #     comp_subjects = comp_subjects and\
        #         Subject.compare(new_subjects[i], old_subjects[i])

        # # compare keys first
        # old_subject_types = self.context.subject_types
        # comp_subject_types = new_subject_types.keys() == old_subject_types.keys()
        # for i in old_subject_types.keys():
        #     comp_subject_types = comp_subject_types and\
        #         SubjectType.compare(new_subject_types[i], old_subject_types[i])

        # # compare keys first
        # old_schedule_entries = self.context.schedule_entries
        # comp_schedule_entries = new_schedule_entries.keys() == old_schedule_entries.keys()
        # for i in old_schedule_entries.keys():
        #     comp_schedule_entries = comp_schedule_entries and\
        #         ScheduleEntry.compare(new_schedule_entries[i], old_schedule_entries[i])

        # # compare keys first
        # old_subject_work_units = self.context.subject_work_units
        # comp_subject_work_units = old_subject_work_units.keys() == old_subject_work_units.keys()
        # for i in old_subject_work_units.keys():
        #     comp_subject_work_units = comp_subject_work_units and\
        #         SubjectWorkUnit.compare(new_subject_work_units[i], old_subject_work_units[i])

        # return (comp_subjects,\
        #     comp_subject_types,\
        #         comp_schedule_entries,\
        #             comp_subject_work_units)

    def update_data_and_compare(self):

        """pick some datasets, update them and compare the results"""

        # start_date = date(2019, 9, 17)
        # end_date = date(2020, 2, 1)
        # db_name = self.context.db_file_name

        # entry = self.context.schedule_entries[1]
        # entry.type_id = entry.type_id + 1
        # entry.day_of_week = entry.day_of_week + 1
        # entry.subject_id = entry.subject_id + 1
        # entry.is_scheduled = entry.is_scheduled
        # entry.start_offset = entry.start_offset + 1

        # n_time = datetime.combine(datetime.today(), entry.start_time) + timedelta(hours=1)
        # entry.start_time = time(n_time.hour, n_time.minute)
        # entry.start_date = entry.start_date - timedelta(days=1)

        # n_time = datetime.combine(datetime.today(), entry.end_time) + timedelta(hours=1)
        # entry.end_time = time(n_time.hour, n_time.minute)
        # entry.end_date = entry.end_date + timedelta(days=1)
        # entry.description = entry.description + "hello"

        # ScheduleEntry.update_by_db_id(entry, db_name)

        # new_schedule_entries = dict()
        # ScheduleEntry.reload_from_db(new_schedule_entries, start_date, end_date, 1, True, db_name)
        # ScheduleEntry.reload_from_db(new_schedule_entries, start_date, end_date, 0, False, db_name)

        # # compare keys first
        # old_schedule_entries = self.context.schedule_entries
        # comp_schedule_entries = new_schedule_entries.keys() == old_schedule_entries.keys()
        # for i in old_schedule_entries.keys():
        #     comp_schedule_entries = comp_schedule_entries and\
        #         ScheduleEntry.compare(new_schedule_entries[i], old_schedule_entries[i])

        # subject = self.context.subjects[1]
        # subject.name = "LOL"
        # subject.description = "Blub"
        # subject.color = QColor(1, 1, 1, 255)
        # subject.start_date = subject.start_date - timedelta(days=1)
        # subject.end_date = subject.end_date + timedelta(days=1)

        # Subject.update_by_db_id(subject, db_name)

        # new_subjects = dict()
        # Subject.reload_from_db(new_subjects, start_date, end_date, db_name)

        # # compare keys first
        # old_subjects = self.context.subjects
        # comp_subjects = new_subjects.keys() == old_subjects.keys()
        # for i in old_subjects.keys():
        #     comp_subjects = comp_subjects and\
        #         Subject.compare(new_subjects[i], old_subjects[i])

        # subject_type = self.context.subject_types[1]
        # subject_type.name = "typo"
        # subject_type.description = "description X"

        # SubjectType.update_by_db_id(subject_type, db_name)

        # new_subject_types = dict()
        # SubjectType.reload_from_db(new_subject_types, db_name)

        # # compare keys first
        # old_subject_types = self.context.subject_types
        # comp_subject_types = new_subject_types.keys() == old_subject_types.keys()
        # for i in old_subject_types.keys():
        #     comp_subject_types = comp_subject_types and\
        #         SubjectType.compare(new_subject_types[i], old_subject_types[i])

        # keys = list(self.context.subject_work_units.keys())
        # subject_work_unit =\
        #     self.context.subject_work_units[keys[0]]
        # # subject_work_unit.subject_id = 2
        # subject_work_unit.work_time = 5
        # # subject_work_unit.set_at_date(subject_work_unit.at_date + timedelta(days=1))
        # subject_work_unit.description = "description X"

        # SubjectWorkUnit.update_by_db_id(subject_work_unit, db_name)

        # new_subject_work_units = dict()
        # SubjectWorkUnit.reload_from_db(new_subject_work_units, start_date, end_date, db_name)

        # # TODO: this test fails if the subject_id or the at_date
        # # are changed because the key is the (subject_id, date_index) pair. find some
        # # testing solution

        # # compare keys first
        # old_subject_work_units = self.context.subject_work_units
        # comp_subject_work_units = old_subject_work_units.keys() == old_subject_work_units.keys()
        # for i in old_subject_work_units.keys():
        #     comp_subject_work_units = comp_subject_work_units and\
        #         SubjectWorkUnit.compare(new_subject_work_units[i], old_subject_work_units[i])

        # return (comp_subjects, comp_subject_types, comp_schedule_entries, comp_subject_work_units)
