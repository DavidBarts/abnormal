# Test updates and inserts. Another one to do near the end, because overall.

# I m p o r t s

import os, sys
import unittest

from dataclasses import dataclass

from abnormal import Connection, Cursor
from abnormal.driver import StandardDriver

from dummydb.common import CursorResults, RESULTS, Message, MESSAGE
import dummydb.format
import dummydb.named
import dummydb.numeric
import dummydb.pyformat
import dummydb.qmark

DRIVER = StandardDriver("table_catalog", "current_catalog")

@dataclass
class Suppliers:
    sno: str
    name: str
    status: int
    city: str

DATA_SOURCE = Suppliers(sno='s1', name='Smith', status=20, city='London')

class TestUpdatesInserts(unittest.TestCase):
    def tearDown(self):
        MESSAGE.clear()
        RESULTS.clear()

    def test_insert_normal(self):
        conn = Connection(dummydb.qmark.Connection(), dummydb.qmark.paramstyle, DRIVER)
        curs = conn.cursor()
        expected_query_1 = "select column_name, column_key from information_schema.columns where table_name = ? and table_schema = database() order by ordinal_position asc"
        needed_data = [('sno', 'PRI'), ('name', ''), ('status', ''), ('city', '')]
        RESULTS.execute.append([])
        RESULTS.execute.append([])
        RESULTS.fetchone.append(None)
        for i in reversed(needed_data):
            RESULTS.fetchone.append(i)
        expected_query_2 = 'insert into "suppliers" ( "sno", "name", "status", "city" ) values ( ?, ?, ?, ? )'
        curs.insert_into("suppliers").from_source(DATA_SOURCE)
        msg = MESSAGE.pop()
        self.assertEqual(msg.source, "cursor execute")
        self.assertEqual(msg.details['operation'], expected_query_2)
        msg = MESSAGE.pop()
        self.assertEqual(msg.source, "cursor execute")
        self.assertEqual(msg.details['operation'], expected_query_1)
        self.assertFalse(bool(MESSAGE))
        curs.close()
        conn.close()

    def test_insert_excluding_norm(self):
        # curs.insert_into("suppliers").excluding("name").from_source(DATA_SOURCE)
        pass

    def test_insert_exluding_pk(self):
        # should not be summarily rejected, often legal!
        # curs.insert_into("suppliers").excluding("sno").from_source(DATA_SOURCE)
        pass

    def test_insert_excluding_mult(self):
        # curs.insert_into("suppliers").excluding("sno", "name").from_source(DATA_SOURCE)
        pass

    def test_insert_excluding_mult_rev(self):
        # curs.insert_into("suppliers").excluding("name", "sno").from_source(DATA_SOURCE)
        pass

    def test_update_normal(self):
        # curs.update("suppliers").from_source(DATA_SOURCE)
        pass

    def test_update_excluding_normal(self):
        # curs.update("suppliers").excluding("name").from_source(DATA_SOURCE)
        pass

    def test_update_excluding_pk(self):
        # should be summarily rejected, pk is needed!
        # curs.update("suppliers").excluding("sno").from_source(DATA_SOURCE)
        pass
        
    def test_update_excluding_mult(self):
        # curs.update("suppliers").excluding("name", "city").from_source(DATA_SOURCE)
        pass

    def test_update_excluding_mult_rev(self):
        # curs.update("suppliers").excluding("city", "name").from_source(DATA_SOURCE)
        pass

    def test_update_excluding_mult_pk(self):
        # should also be rejected
        # curs.update("suppliers").excluding("name", "sno").from_source(DATA_SOURCE)
        pass

# Need to test the other drivers besides the standard one.
# Need to test the standard one w/ other params.
# Can we grab from the dict?

# M a i n   P r o g r a m

if __name__ == '__main__':
    unittest.main()
