
"""
Test cases for all scheduler components
"""

import unittest
import dbobj.dbwrapper as dbwrapper
import testdata
import globalcontext

class TestDB(unittest.TestCase):

    """Test class for DB class"""

    def test_seeding(self):

        """initiate db and see if it gets seeded properly"""

        db_obj = dbwrapper.DB(db_name="test_data.db")
        db_obj.seed()

    # @unittest.skip("check seeding first")
    def test_insert_test_data(self):

        """insert data and check if it gets inserted properly"""

        context = globalcontext.GlobalContext()
        context.db_file_name = "test_data.db"

        db_obj = dbwrapper.DB(db_name=context.db_file_name)
        db_obj.seed()
        test = testdata.TestData(context)

        gen = test.generate_test_data()
        assert gen

        load = test.reload_data_to_dict()
        assert load[0]
        assert load[1]
        assert load[2]
        assert load[3]

        update = test.update_data_and_compare()
        assert update[0]
        assert update[1]
        assert update[2]
        assert update[3]

unittest.main()
