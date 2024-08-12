"""
This file contains version number and description as well as
all migrations for the data base
"""

import os
import sqlite3
import dbobj.dbwrapper as dbwrapper

# description of what was achieved with the current version
DESCRIPTION = "loaded from db"

# current version number (format: [#.##])
# smallest difference between versions is 0.01
# this number has to be the same as the highest
# DBVersion.Value
# If it's not, the db version doesn't fit to the
# current code!
VERSION = 1.06

# name of db file
DB_NAME = "-load-from-dbconfig.txt-"
if not os.path.exists("./dbconfig.txt"):
    p = os.path.split(os.path.realpath(__file__).replace('\\', '/'))[0] + "/data.db"
    DB_NAME_STR = p
    DB_NAME = DB_NAME_STR
else:
    with open("dbconfig.txt", "r", newline=None) as e_file:
        DB_NAME_STR = e_file.readline().replace("\n", "")
        DB_NAME = DB_NAME_STR

def special_migration(db_name):

    """execute all migrations up to current state"""

    # initial version where db migrations are introduced
    # this migration doesn't work if version is not hardcoded
    # to 1.0 because it was added later on!!!
    print("Special migration ...")
    connection = sqlite3.connect(db_name)
    dbwrapper.DBVersion.seed(connection)
    dbwrapper.DBVersion.create_new_version("Added Config", 1.01, db_name)
    print("...OK")

if __name__ == "__main__":
    special_migration("data.db")
else:
    DB_VERSION = 0
    try:
        DB_VERSION = dbwrapper.DBVersion.get_current_version(DB_NAME).value
    except sqlite3.Error:
        # no db there yet, do initial seed
        DB_VERSION = 0.99
        print("initial seed required...")

    # try to migrate as long as possible
    if DB_VERSION < VERSION:
        DB_OBJ = dbwrapper.DB(DB_NAME)
        DB_OBJ.seed(VERSION, DB_VERSION)
        DB_OBJ.init()

        # now if there is no db version, there is something weird
        DB_VERSION = dbwrapper.DBVersion.get_current_version(DB_NAME).value

    if DB_VERSION != VERSION:
        ERROR_MSG =\
        """
        ############################################\n
        # DB version error: code version is: {0}\n
        #                   db version is:   {1}\n
        ############################################\n
        """.format(str(VERSION), str(DB_VERSION))

        with open("./DB_VERSION_ERROR.TXT", "w") as e_file:
            e_file.write(ERROR_MSG)

        raise Exception(ERROR_MSG)
    else:
        if os.path.isfile("./DB_VERSION_ERROR.TXT"):
            os.remove("./DB_VERSION_ERROR.TXT")
