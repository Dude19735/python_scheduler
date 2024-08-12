"""
Module starts timer

Author: dumenim@student.ethz.ch
"""

import sys
from PyQt6.QtWidgets import QApplication
from PyQt6.QtWidgets import QStyleFactory

# put this at the top of all custom imports!
# at import the current version of the db is
# checked and if necessary a warning is printed
import version
# ------------------------------------------

import timer
# import mainconfigwindow
import globalcontext
import communicator
import dbobj.dbwrapper as dbwrapper
# import testdata

# load basic versioning values
CONTEXT = globalcontext.GlobalContext()
CONTEXT.db_file_name = version.DB_NAME
CONTEXT.db_version = version.VERSION
CONTEXT.db_description = version.DESCRIPTION

COMMUNICATOR = communicator.Communicator()

# with open(CONTEXT.output_file_name, "a") as e_file:
    # e_file.write(\
        # datetime.today().strftime(CONTEXT.output_date_format) +\
            # ": " + "Start...\n")

# something usable to create an initial db
# testdata.TestData(CONTEXT).generate_test_data()

# load configs and types from db
dbwrapper.SubjectType.reload_from_db(\
    CONTEXT.subject_types,\
        CONTEXT.db_file_name)

dbwrapper.Subject.reload_from_db(\
    CONTEXT.subjects,\
        dbwrapper.SubjectTypes.SUBJECT_TYPE,\
            1,\
                CONTEXT.db_file_name)

# load study subject
TEMP = dict()
dbwrapper.Subject.reload_from_db(\
    TEMP,\
        dbwrapper.SubjectTypes.STUDY_TYPE,\
            1,\
                CONTEXT.db_file_name)

CONTEXT.study_subject = list(TEMP.values())[0]

for i in CONTEXT.subject_types.items():
    if i[1].name == "F":
        CONTEXT.free_work_subject_type_key = i[0]
        break

APP = QApplication(sys.argv)
# APP.setStyle("QPushButton { border-style: outset }")
MAIN_WIDGET = timer.Timer(COMMUNICATOR, CONTEXT)
# MAIN_WIDGET.setFont(CONTEXT.font)
# MAIN_WIDGET.setStyleSheet(CONTEXT.style)

def disableAll(except_widget):
    x = APP.allWidgets()
    for i in x:
        if i != except_widget:
            i.setEnabled(False)
CONTEXT.disable_all = disableAll

APP.exec()
del MAIN_WIDGET

# with open(CONTEXT.output_file_name, "a") as e_file:
    # e_file.write(\
        # datetime.today().strftime(CONTEXT.output_date_format) +\
            # ": " + "...Shutdown\n")
