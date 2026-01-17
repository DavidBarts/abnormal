# Test updates and inserts. Another one to do near the end, because overall.

# I m p o r t s

import os, sys
import unittest

from dataclasses import dataclass

from abnormal import Connection, Cursor
from abnormal.driver import StandardDriver, Db2Driver, OracleDriver, Sqlite3Driver
from abnormal.exceptions import IncompleteDataError, InvalidStateError

from dummydb.common import CursorResults, RESULTS, Message, MESSAGE
import dummydb.format
import dummydb.named
import dummydb.numeric
import dummydb.pyformat
import dummydb.qmark

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

    def test_insert_mysql_like(self):
        conn = Connection(dummydb.qmark.Connection(), dummydb.qmark.paramstyle, StandardDriver("table_schema", "database()"))
        curs = conn.cursor()
        expected_query_1 = "select column_name, column_key from information_schema.columns where table_name = ? and table_schema = database() order by ordinal_position asc"
        needed_data = [('sno', 'PRI'), ('name', ''), ('status', ''), ('city', '')]
        RESULTS.execute.append([])
        RESULTS.execute.append([])
        RESULTS.fetchone.append(None)
        for i in reversed(needed_data):
            RESULTS.fetchone.append(i)
        for i in range(5):
            RESULTS.description.append([])
        RESULTS.description.append([('column_name', str, None, None, None, None, None), ('column_key', str, None, None, None, None, None)])
        expected_query_2 = 'insert into "suppliers" ( "sno", "name", "status", "city" ) values ( ?, ?, ?, ? )'
        curs.insert_into("suppliers").from_source(DATA_SOURCE)
        msg = MESSAGE.pop()
        self.assertEqual(msg.source, "cursor execute")
        self.assertEqual(msg.details['operation'], expected_query_2)
        while True:
            msg = MESSAGE.pop()
            if msg.source == "cursor execute":
                break
        self.assertEqual(msg.details['operation'], expected_query_1)
        curs.close()
        conn.close()

    # Also MS SQL Server-like.
    def test_insert_postgres_like(self):
        conn = Connection(dummydb.pyformat.Connection(), dummydb.pyformat.paramstyle, StandardDriver("table_catalog", "current_catalog"))
        curs = conn.cursor()
        expected_query_1 = "select column_name, column_key from information_schema.columns where table_name = %(tabname)s and table_catalog = current_catalog order by ordinal_position asc"
        needed_data = [('sno', 'PRI'), ('name', ''), ('status', ''), ('city', '')]
        RESULTS.execute.append([])
        RESULTS.execute.append([])
        RESULTS.fetchone.append(None)
        for i in reversed(needed_data):
            RESULTS.fetchone.append(i)
        expected_query_2 = 'insert into "suppliers" ( "sno", "name", "status", "city" ) values ( %(sno)s, %(name)s, %(status)s, %(city)s )'
        for i in range(5):
            RESULTS.description.append([])
        curs.insert_into("suppliers").from_source(DATA_SOURCE)
        msg = MESSAGE.pop()
        self.assertEqual(msg.source, "cursor execute")
        self.assertEqual(msg.details['operation'], expected_query_2)
        while True:
            msg = MESSAGE.pop()
            if msg.source == "cursor execute":
                break
        self.assertEqual(msg.details['operation'], expected_query_1)
        curs.close()
        conn.close()

    def test_insert_db2_like(self):
        conn = Connection(dummydb.qmark.Connection(), dummydb.qmark.paramstyle, Db2Driver())
        curs = conn.cursor()
        expected_query_1 = "select colname, keyseq from syscat.columns where tabschema = current_schema and tabname = ? order by colno asc"
        needed_data = [('sno', 1), ('name', 0), ('status', None), ('city', 0)]
        RESULTS.execute.append([])
        RESULTS.execute.append([])
        RESULTS.fetchone.append(None)
        for i in reversed(needed_data):
            RESULTS.fetchone.append(i)
        expected_query_2 = 'insert into "suppliers" ( "sno", "name", "status", "city" ) values ( ?, ?, ?, ? )'
        for i in range(5):
            RESULTS.description.append([])
        curs.insert_into("suppliers").from_source(DATA_SOURCE)
        msg = MESSAGE.pop()
        self.assertEqual(msg.source, "cursor execute")
        self.assertEqual(msg.details['operation'], expected_query_2)
        while True:
            msg = MESSAGE.pop()
            if msg.source == "cursor execute":
                break
        self.assertEqual(msg.details['operation'], expected_query_1)
        curs.close()
        conn.close()

    def test_insert_oracle_like(self):
        conn = Connection(dummydb.named.Connection(), dummydb.named.paramstyle, OracleDriver())
        curs = conn.cursor()
        RESULTS.execute.append([])
        RESULTS.execute.append([])
        RESULTS.execute.append([])
        needed_data = [('NAME',), ('STATUS',), ('CITY',)]
        RESULTS.fetchone.append(None)
        for i in reversed(needed_data):
            RESULTS.fetchone.append(i)
        RESULTS.fetchone.append(None)
        RESULTS.fetchone.append(('SNO',))
        for i in range(5):
            RESULTS.description.append([])
        RESULTS.description.append([('COLUMN_NAME', str, None, None, None, None, None)])
        RESULTS.description.append([('cols.table_name', str, None, None, None, None, None)])
        expected_query_2 = 'insert into "suppliers" ( "sno", "name", "status", "city" ) values ( :sno, :name, :status, :city )'
        curs.insert_into("suppliers").from_source(DATA_SOURCE)
        msg = MESSAGE.pop()
        self.assertEqual(msg.source, "cursor execute")
        self.assertEqual(msg.details['operation'], expected_query_2)
        while True:
            msg = MESSAGE.pop()
            if msg.source == "cursor execute":
                break
        self.assertEqual(msg.details['operation'], "SELECT COLUMN_NAME FROM ALL_TAB_COLUMNS WHERE OWNER = SYS_CONTEXT('USERENV','CURRENT_SCHEMA') AND TABLE_NAME = :tabname ORDER BY COLUMN_ID ASC")
        while True:
            msg = MESSAGE.pop()
            if msg.source == "cursor execute":
                break
        self.assertTrue("WHERE cols.owner = SYS_CONTEXT('USERENV','CURRENT_SCHEMA')" in msg.details['operation'])
        self.assertTrue("AND cols.table_name = :tabname" in msg.details['operation'])
        curs.close()
        conn.close()

    def test_insert_sqlite3_like(self):
        conn = Connection(dummydb.qmark.Connection(), dummydb.qmark.paramstyle, Sqlite3Driver())
        curs = conn.cursor()
        expected_query_1 = "pragma table_info(?)"
        needed_data = [
            (0, 'sno', 'TEXT', 1, None, 1),
            (1, 'name', 'TEXT', 1, None, 0),
            (2, 'status', 'INTEGER', 1, None, 0),
            (3, 'city', 'TEXT', 1, None, 0)
        ]
        RESULTS.execute.append([])
        RESULTS.execute.append([])
        RESULTS.fetchone.append(None)
        for i in reversed(needed_data):
            RESULTS.fetchone.append(i)
        expected_query_2 = 'insert into "suppliers" ( "sno", "name", "status", "city" ) values ( ?, ?, ?, ? )'
        for i in range(5):
            RESULTS.description.append([])
        RESULTS.description.append([
            ('cid', int, None, None, None, None, None),
            ('name', str, None, None, None, None, None),
            ('type', str, None, None, None, None, None),
            ('notnull', str, None, None, None, None, None),
            ('dflt_value', str, None, None, None, None, None),
            ('pk', str, None, None, None, None, None),
            ])
        curs.insert_into("suppliers").from_source(DATA_SOURCE)
        msg = MESSAGE.pop()
        self.assertEqual(msg.source, "cursor execute")
        self.assertEqual(msg.details['operation'], expected_query_2)
        while True:
            msg = MESSAGE.pop()
            if msg.source == "cursor execute":
                break
        self.assertEqual(msg.details['operation'], expected_query_1)
        curs.close()
        conn.close()

    def test_insert_numeric(self):
        conn = Connection(dummydb.numeric.Connection(), dummydb.numeric.paramstyle, StandardDriver("table_schema", "database()"))
        curs = conn.cursor()
        expected_query_1 = "select column_name, column_key from information_schema.columns where table_name = :1 and table_schema = database() order by ordinal_position asc"
        needed_data = [('sno', 'PRI'), ('name', ''), ('status', ''), ('city', '')]
        RESULTS.execute.append([])
        RESULTS.execute.append([])
        RESULTS.fetchone.append(None)
        for i in reversed(needed_data):
            RESULTS.fetchone.append(i)
        for i in range(5):
            RESULTS.description.append([])
        RESULTS.description.append([('column_name', str, None, None, None, None, None), ('column_key', str, None, None, None, None, None)])
        expected_query_2 = 'insert into "suppliers" ( "sno", "name", "status", "city" ) values ( :1, :2, :3, :4 )'
        curs.insert_into("suppliers").from_source(DATA_SOURCE)
        msg = MESSAGE.pop()
        self.assertEqual(msg.source, "cursor execute")
        self.assertEqual(msg.details['operation'], expected_query_2)
        while True:
            msg = MESSAGE.pop()
            if msg.source == "cursor execute":
                break
        self.assertEqual(msg.details['operation'], expected_query_1)
        curs.close()
        conn.close()

    def test_insert_format(self):
        conn = Connection(dummydb.format.Connection(), dummydb.format.paramstyle, StandardDriver("table_schema", "database()"))
        curs = conn.cursor()
        expected_query_1 = "select column_name, column_key from information_schema.columns where table_name = %s and table_schema = database() order by ordinal_position asc"
        needed_data = [('sno', 'PRI'), ('name', ''), ('status', ''), ('city', '')]
        RESULTS.execute.append([])
        RESULTS.execute.append([])
        RESULTS.fetchone.append(None)
        for i in reversed(needed_data):
            RESULTS.fetchone.append(i)
        for i in range(5):
            RESULTS.description.append([])
        RESULTS.description.append([('column_name', str, None, None, None, None, None), ('column_key', str, None, None, None, None, None)])
        expected_query_2 = 'insert into "suppliers" ( "sno", "name", "status", "city" ) values ( %s, %s, %s, %s )'
        curs.insert_into("suppliers").from_source(DATA_SOURCE)
        msg = MESSAGE.pop()
        self.assertEqual(msg.source, "cursor execute")
        self.assertEqual(msg.details['operation'], expected_query_2)
        while True:
            msg = MESSAGE.pop()
            if msg.source == "cursor execute":
                break
        self.assertEqual(msg.details['operation'], expected_query_1)
        curs.close()
        conn.close()

    def test_insert_explicit_database(self):
        conn = Connection(dummydb.qmark.Connection(), dummydb.qmark.paramstyle, StandardDriver("table_schema", "database()"))
        curs = conn.cursor()
        expected_query_1 = "select column_name, column_key from information_schema.columns where table_name = ? and table_schema = ? order by ordinal_position asc"
        needed_data = [('sno', 'PRI'), ('name', ''), ('status', ''), ('city', '')]
        RESULTS.execute.append([])
        RESULTS.execute.append([])
        RESULTS.fetchone.append(None)
        for i in reversed(needed_data):
            RESULTS.fetchone.append(i)
        for i in range(5):
            RESULTS.description.append([])
        RESULTS.description.append([('column_name', str, None, None, None, None, None), ('column_key', str, None, None, None, None, None)])
        expected_query_2 = 'insert into "example.suppliers" ( "sno", "name", "status", "city" ) values ( ?, ?, ?, ? )'
        curs.insert_into("example.suppliers").from_source(DATA_SOURCE)
        msg = MESSAGE.pop()
        self.assertEqual(msg.source, "cursor execute")
        self.assertEqual(msg.details['operation'], expected_query_2)
        while True:
            msg = MESSAGE.pop()
            if msg.source == "cursor execute":
                break
        self.assertEqual(msg.details['operation'], expected_query_1)
        curs.close()
        conn.close()

    def test_insert_excluding_norm(self):
        conn = Connection(dummydb.qmark.Connection(), dummydb.qmark.paramstyle, StandardDriver("table_schema", "database()"))
        curs = conn.cursor()
        expected_query_1 = "select column_name, column_key from information_schema.columns where table_name = ? and table_schema = database() order by ordinal_position asc"
        needed_data = [('sno', 'PRI'), ('name', ''), ('status', ''), ('city', '')]
        RESULTS.execute.append([])
        RESULTS.execute.append([])
        RESULTS.fetchone.append(None)
        for i in reversed(needed_data):
            RESULTS.fetchone.append(i)
        for i in range(5):
            RESULTS.description.append([])
        RESULTS.description.append([('column_name', str, None, None, None, None, None), ('column_key', str, None, None, None, None, None)])
        expected_query_2 = 'insert into "suppliers" ( "sno", "status", "city" ) values ( ?, ?, ? )'
        curs.insert_into("suppliers").excluding("name").from_source(DATA_SOURCE)
        msg = MESSAGE.pop()
        self.assertEqual(msg.source, "cursor execute")
        self.assertEqual(msg.details['operation'], expected_query_2)
        while True:
            msg = MESSAGE.pop()
            if msg.source == "cursor execute":
                break
        self.assertEqual(msg.details['operation'], expected_query_1)
        curs.close()
        conn.close()

    def test_insert_exluding_pk(self):
        # should not be summarily rejected, often legal!
        conn = Connection(dummydb.qmark.Connection(), dummydb.qmark.paramstyle, StandardDriver("table_schema", "database()"))
        curs = conn.cursor()
        expected_query_1 = "select column_name, column_key from information_schema.columns where table_name = ? and table_schema = database() order by ordinal_position asc"
        needed_data = [('sno', 'PRI'), ('name', ''), ('status', ''), ('city', '')]
        RESULTS.execute.append([])
        RESULTS.execute.append([])
        RESULTS.fetchone.append(None)
        for i in reversed(needed_data):
            RESULTS.fetchone.append(i)
        for i in range(5):
            RESULTS.description.append([])
        RESULTS.description.append([('column_name', str, None, None, None, None, None), ('column_key', str, None, None, None, None, None)])
        expected_query_2 = 'insert into "suppliers" ( "name", "status", "city" ) values ( ?, ?, ? )'
        curs.insert_into("suppliers").excluding("sno").from_source(DATA_SOURCE)
        msg = MESSAGE.pop()
        self.assertEqual(msg.source, "cursor execute")
        self.assertEqual(msg.details['operation'], expected_query_2)
        while True:
            msg = MESSAGE.pop()
            if msg.source == "cursor execute":
                break
        self.assertEqual(msg.details['operation'], expected_query_1)
        curs.close()
        conn.close()

    def test_insert_excluding_mult(self):
        conn = Connection(dummydb.qmark.Connection(), dummydb.qmark.paramstyle, StandardDriver("table_schema", "database()"))
        curs = conn.cursor()
        expected_query_1 = "select column_name, column_key from information_schema.columns where table_name = ? and table_schema = database() order by ordinal_position asc"
        needed_data = [('sno', 'PRI'), ('name', ''), ('status', ''), ('city', '')]
        RESULTS.execute.append([])
        RESULTS.execute.append([])
        RESULTS.fetchone.append(None)
        for i in reversed(needed_data):
            RESULTS.fetchone.append(i)
        for i in range(5):
            RESULTS.description.append([])
        RESULTS.description.append([('column_name', str, None, None, None, None, None), ('column_key', str, None, None, None, None, None)])
        expected_query_2 = 'insert into "suppliers" ( "status", "city" ) values ( ?, ? )'
        curs.insert_into("suppliers").excluding("sno", "name").from_source(DATA_SOURCE)
        msg = MESSAGE.pop()
        self.assertEqual(msg.source, "cursor execute")
        self.assertEqual(msg.details['operation'], expected_query_2)
        while True:
            msg = MESSAGE.pop()
            if msg.source == "cursor execute":
                break
        self.assertEqual(msg.details['operation'], expected_query_1)
        curs.close()
        conn.close()

    def test_insert_excluding_mult_rev(self):
        conn = Connection(dummydb.qmark.Connection(), dummydb.qmark.paramstyle, StandardDriver("table_schema", "database()"))
        curs = conn.cursor()
        expected_query_1 = "select column_name, column_key from information_schema.columns where table_name = ? and table_schema = database() order by ordinal_position asc"
        needed_data = [('sno', 'PRI'), ('name', ''), ('status', ''), ('city', '')]
        RESULTS.execute.append([])
        RESULTS.execute.append([])
        RESULTS.fetchone.append(None)
        for i in reversed(needed_data):
            RESULTS.fetchone.append(i)
        for i in range(5):
            RESULTS.description.append([])
        RESULTS.description.append([('column_name', str, None, None, None, None, None), ('column_key', str, None, None, None, None, None)])
        expected_query_2 = 'insert into "suppliers" ( "status", "city" ) values ( ?, ? )'
        curs.insert_into("suppliers").excluding("name", "sno").from_source(DATA_SOURCE)
        msg = MESSAGE.pop()
        self.assertEqual(msg.source, "cursor execute")
        self.assertEqual(msg.details['operation'], expected_query_2)
        while True:
            msg = MESSAGE.pop()
            if msg.source == "cursor execute":
                break
        self.assertEqual(msg.details['operation'], expected_query_1)
        curs.close()
        conn.close()

    def test_insert_including_pk(self):
        conn = Connection(dummydb.qmark.Connection(), dummydb.qmark.paramstyle, StandardDriver("table_schema", "database()"))
        curs = conn.cursor()
        expected_query_1 = "select column_name, column_key from information_schema.columns where table_name = ? and table_schema = database() order by ordinal_position asc"
        needed_data = [('sno', 'PRI'), ('name', ''), ('status', ''), ('city', '')]
        RESULTS.execute.append([])
        RESULTS.execute.append([])
        RESULTS.fetchone.append(None)
        for i in reversed(needed_data):
            RESULTS.fetchone.append(i)
        for i in range(5):
            RESULTS.description.append([])
        RESULTS.description.append([('column_name', str, None, None, None, None, None), ('column_key', str, None, None, None, None, None)])
        expected_query_2 = 'insert into "suppliers" ( "sno", "status", "city" ) values ( ?, ?, ? )'
        curs.insert_into("suppliers").including("sno", "status", "city").from_source(DATA_SOURCE)
        msg = MESSAGE.pop()
        self.assertEqual(msg.source, "cursor execute")
        self.assertEqual(msg.details['operation'], expected_query_2)
        while True:
            msg = MESSAGE.pop()
            if msg.source == "cursor execute":
                break
        self.assertEqual(msg.details['operation'], expected_query_1)
        curs.close()
        conn.close()

    def test_insert_not_including_pk(self):
        # should work!
        conn = Connection(dummydb.qmark.Connection(), dummydb.qmark.paramstyle, StandardDriver("table_schema", "database()"))
        curs = conn.cursor()
        expected_query_1 = "select column_name, column_key from information_schema.columns where table_name = ? and table_schema = database() order by ordinal_position asc"
        needed_data = [('sno', 'PRI'), ('name', ''), ('status', ''), ('city', '')]
        RESULTS.execute.append([])
        RESULTS.execute.append([])
        RESULTS.fetchone.append(None)
        for i in reversed(needed_data):
            RESULTS.fetchone.append(i)
        for i in range(5):
            RESULTS.description.append([])
        RESULTS.description.append([('column_name', str, None, None, None, None, None), ('column_key', str, None, None, None, None, None)])
        expected_query_2 = 'insert into "suppliers" ( "status", "city" ) values ( ?, ? )'
        curs.insert_into("suppliers").including("status", "city").from_source(DATA_SOURCE)
        msg = MESSAGE.pop()
        self.assertEqual(msg.source, "cursor execute")
        self.assertEqual(msg.details['operation'], expected_query_2)
        while True:
            msg = MESSAGE.pop()
            if msg.source == "cursor execute":
                break
        self.assertEqual(msg.details['operation'], expected_query_1)
        curs.close()
        conn.close()

    def test_update_including_excluding(self):
        # should be rejected w/ InvalidStateError
        conn = Connection(dummydb.qmark.Connection(), dummydb.qmark.paramstyle, StandardDriver("table_schema", "database()"))
        curs = conn.cursor()
        expected_query_1 = "select column_name, column_key from information_schema.columns where table_name = ? and table_schema = database() order by ordinal_position asc"
        needed_data = [('sno', 'PRI'), ('name', ''), ('status', ''), ('city', '')]
        RESULTS.execute.append([])
        RESULTS.execute.append([])
        RESULTS.fetchone.append(None)
        for i in reversed(needed_data):
            RESULTS.fetchone.append(i)
        for i in range(5):
            RESULTS.description.append([])
        RESULTS.description.append([('column_name', str, None, None, None, None, None), ('column_key', str, None, None, None, None, None)])
        expected_query_2 = 'insert into "suppliers" ( "status", "city" ) values ( ?, ? )'
        with self.assertRaises(InvalidStateError):
            curs.insert_into("suppliers").including("status", "city").excluding("sno").from_source(DATA_SOURCE)
        curs.close()
        conn.close()

    def test_update_normal(self):
        conn = Connection(dummydb.qmark.Connection(), dummydb.qmark.paramstyle, StandardDriver("table_schema", "database()"))
        curs = conn.cursor()
        expected_query_1 = "select column_name, column_key from information_schema.columns where table_name = ? and table_schema = database() order by ordinal_position asc"
        needed_data = [('sno', 'PRI'), ('name', ''), ('status', ''), ('city', '')]
        RESULTS.execute.append([])
        RESULTS.execute.append([])
        RESULTS.fetchone.append(None)
        for i in reversed(needed_data):
            RESULTS.fetchone.append(i)
        for i in range(5):
            RESULTS.description.append([])
        RESULTS.description.append([('column_name', str, None, None, None, None, None), ('column_key', str, None, None, None, None, None)])
        expected_query_2 = 'update "suppliers" set "name" = ?, "status" = ?, "city" = ? where "sno" = ?'
        curs.update("suppliers").from_source(DATA_SOURCE)
        msg = MESSAGE.pop()
        self.assertEqual(msg.source, "cursor execute")
        self.assertEqual(msg.details['operation'], expected_query_2)
        while True:
            msg = MESSAGE.pop()
            if msg.source == "cursor execute":
                break
        self.assertEqual(msg.details['operation'], expected_query_1)
        curs.close()
        conn.close()

    def test_update_excluding_normal(self):
        conn = Connection(dummydb.qmark.Connection(), dummydb.qmark.paramstyle, StandardDriver("table_schema", "database()"))
        curs = conn.cursor()
        expected_query_1 = "select column_name, column_key from information_schema.columns where table_name = ? and table_schema = database() order by ordinal_position asc"
        needed_data = [('sno', 'PRI'), ('name', ''), ('status', ''), ('city', '')]
        RESULTS.execute.append([])
        RESULTS.execute.append([])
        RESULTS.fetchone.append(None)
        for i in reversed(needed_data):
            RESULTS.fetchone.append(i)
        for i in range(5):
            RESULTS.description.append([])
        RESULTS.description.append([('column_name', str, None, None, None, None, None), ('column_key', str, None, None, None, None, None)])
        expected_query_2 = 'update "suppliers" set "status" = ?, "city" = ? where "sno" = ?'
        curs.update("suppliers").excluding("name").from_source(DATA_SOURCE)
        msg = MESSAGE.pop()
        self.assertEqual(msg.source, "cursor execute")
        self.assertEqual(msg.details['operation'], expected_query_2)
        while True:
            msg = MESSAGE.pop()
            if msg.source == "cursor execute":
                break
        self.assertEqual(msg.details['operation'], expected_query_1)
        curs.close()
        conn.close()

    def test_update_excluding_pk(self):
        # should be summarily rejected, pk is needed here!
        conn = Connection(dummydb.qmark.Connection(), dummydb.qmark.paramstyle, StandardDriver("table_schema", "database()"))
        curs = conn.cursor()
        expected_query_1 = "select column_name, column_key from information_schema.columns where table_name = ? and table_schema = database() order by ordinal_position asc"
        needed_data = [('sno', 'PRI'), ('name', ''), ('status', ''), ('city', '')]
        RESULTS.execute.append([])
        RESULTS.execute.append([])
        RESULTS.fetchone.append(None)
        for i in reversed(needed_data):
            RESULTS.fetchone.append(i)
        for i in range(5):
            RESULTS.description.append([])
        RESULTS.description.append([('column_name', str, None, None, None, None, None), ('column_key', str, None, None, None, None, None)])
        expected_query_2 = 'update "suppliers" set "status" = ?, "city" = ? where "sno" = ?'
        with self.assertRaises(IncompleteDataError):
            curs.update("suppliers").excluding("sno").from_source(DATA_SOURCE)
        curs.close()
        conn.close()
        
    def test_update_excluding_mult(self):
        conn = Connection(dummydb.qmark.Connection(), dummydb.qmark.paramstyle, StandardDriver("table_schema", "database()"))
        curs = conn.cursor()
        expected_query_1 = "select column_name, column_key from information_schema.columns where table_name = ? and table_schema = database() order by ordinal_position asc"
        needed_data = [('sno', 'PRI'), ('name', ''), ('status', ''), ('city', '')]
        RESULTS.execute.append([])
        RESULTS.execute.append([])
        RESULTS.fetchone.append(None)
        for i in reversed(needed_data):
            RESULTS.fetchone.append(i)
        for i in range(5):
            RESULTS.description.append([])
        RESULTS.description.append([('column_name', str, None, None, None, None, None), ('column_key', str, None, None, None, None, None)])
        expected_query_2 = 'update "suppliers" set "status" = ? where "sno" = ?'
        curs.update("suppliers").excluding("name", "city").from_source(DATA_SOURCE)
        msg = MESSAGE.pop()
        self.assertEqual(msg.source, "cursor execute")
        self.assertEqual(msg.details['operation'], expected_query_2)
        while True:
            msg = MESSAGE.pop()
            if msg.source == "cursor execute":
                break
        self.assertEqual(msg.details['operation'], expected_query_1)
        curs.close()
        conn.close()

    def test_update_excluding_mult_rev(self):
        conn = Connection(dummydb.qmark.Connection(), dummydb.qmark.paramstyle, StandardDriver("table_schema", "database()"))
        curs = conn.cursor()
        expected_query_1 = "select column_name, column_key from information_schema.columns where table_name = ? and table_schema = database() order by ordinal_position asc"
        needed_data = [('sno', 'PRI'), ('name', ''), ('status', ''), ('city', '')]
        RESULTS.execute.append([])
        RESULTS.execute.append([])
        RESULTS.fetchone.append(None)
        for i in reversed(needed_data):
            RESULTS.fetchone.append(i)
        for i in range(5):
            RESULTS.description.append([])
        RESULTS.description.append([('column_name', str, None, None, None, None, None), ('column_key', str, None, None, None, None, None)])
        expected_query_2 = 'update "suppliers" set "status" = ? where "sno" = ?'
        curs.update("suppliers").excluding("city", "name").from_source(DATA_SOURCE)
        msg = MESSAGE.pop()
        self.assertEqual(msg.source, "cursor execute")
        self.assertEqual(msg.details['operation'], expected_query_2)
        while True:
            msg = MESSAGE.pop()
            if msg.source == "cursor execute":
                break
        self.assertEqual(msg.details['operation'], expected_query_1)
        curs.close()
        conn.close()

    def test_update_excluding_mult_pk(self):
        # should also be rejected
        conn = Connection(dummydb.qmark.Connection(), dummydb.qmark.paramstyle, StandardDriver("table_schema", "database()"))
        curs = conn.cursor()
        expected_query_1 = "select column_name, column_key from information_schema.columns where table_name = ? and table_schema = database() order by ordinal_position asc"
        needed_data = [('sno', 'PRI'), ('name', ''), ('status', ''), ('city', '')]
        RESULTS.execute.append([])
        RESULTS.execute.append([])
        RESULTS.fetchone.append(None)
        for i in reversed(needed_data):
            RESULTS.fetchone.append(i)
        for i in range(5):
            RESULTS.description.append([])
        RESULTS.description.append([('column_name', str, None, None, None, None, None), ('column_key', str, None, None, None, None, None)])
        expected_query_2 = 'update "suppliers" set "status" = ?, "city" = ? where "sno" = ?'
        with self.assertRaises(IncompleteDataError):
            curs.update("suppliers").excluding("name", "sno").from_source(DATA_SOURCE)
        curs.close()
        conn.close()

    def test_update_including_pk(self):
        conn = Connection(dummydb.qmark.Connection(), dummydb.qmark.paramstyle, StandardDriver("table_schema", "database()"))
        curs = conn.cursor()
        expected_query_1 = "select column_name, column_key from information_schema.columns where table_name = ? and table_schema = database() order by ordinal_position asc"
        needed_data = [('sno', 'PRI'), ('name', ''), ('status', ''), ('city', '')]
        RESULTS.execute.append([])
        RESULTS.execute.append([])
        RESULTS.fetchone.append(None)
        for i in reversed(needed_data):
            RESULTS.fetchone.append(i)
        for i in range(5):
            RESULTS.description.append([])
        RESULTS.description.append([('column_name', str, None, None, None, None, None), ('column_key', str, None, None, None, None, None)])
        expected_query_2 = 'update "suppliers" set "name" = ?, "status" = ? where "sno" = ?'
        curs.update("suppliers").including("sno", "name", "status").from_source(DATA_SOURCE)
        msg = MESSAGE.pop()
        self.assertEqual(msg.source, "cursor execute")
        self.assertEqual(msg.details['operation'], expected_query_2)
        while True:
            msg = MESSAGE.pop()
            if msg.source == "cursor execute":
                break
        self.assertEqual(msg.details['operation'], expected_query_1)
        curs.close()
        conn.close()

    def test_update_not_including_pk(self):
        # should be rejected w/ IncompleteDataError
        conn = Connection(dummydb.qmark.Connection(), dummydb.qmark.paramstyle, StandardDriver("table_schema", "database()"))
        curs = conn.cursor()
        expected_query_1 = "select column_name, column_key from information_schema.columns where table_name = ? and table_schema = database() order by ordinal_position asc"
        needed_data = [('sno', 'PRI'), ('name', ''), ('status', ''), ('city', '')]
        RESULTS.execute.append([])
        RESULTS.execute.append([])
        RESULTS.fetchone.append(None)
        for i in reversed(needed_data):
            RESULTS.fetchone.append(i)
        for i in range(5):
            RESULTS.description.append([])
        RESULTS.description.append([('column_name', str, None, None, None, None, None), ('column_key', str, None, None, None, None, None)])
        expected_query_2 = 'update "suppliers" set "name" = ?, "status" = ? where "sno" = ?'
        with self.assertRaises(IncompleteDataError):
            curs.update("suppliers").including("name", "status").from_source(DATA_SOURCE)
        curs.close()
        conn.close()

    def test_update_including_excluding(self):
        # should be rejected w/ InvalidStateError
        conn = Connection(dummydb.qmark.Connection(), dummydb.qmark.paramstyle, StandardDriver("table_schema", "database()"))
        curs = conn.cursor()
        expected_query_1 = "select column_name, column_key from information_schema.columns where table_name = ? and table_schema = database() order by ordinal_position asc"
        needed_data = [('sno', 'PRI'), ('name', ''), ('status', ''), ('city', '')]
        RESULTS.execute.append([])
        RESULTS.execute.append([])
        RESULTS.fetchone.append(None)
        for i in reversed(needed_data):
            RESULTS.fetchone.append(i)
        for i in range(5):
            RESULTS.description.append([])
        RESULTS.description.append([('column_name', str, None, None, None, None, None), ('column_key', str, None, None, None, None, None)])
        expected_query_2 = 'update "suppliers" set "name" = ?, "status" = ? where "sno" = ?'
        with self.assertRaises(InvalidStateError):
            curs.update("suppliers").including("sno", "name", "status").excluding("sno").from_source(DATA_SOURCE)
        curs.close()
        conn.close()

# M a i n   P r o g r a m

if __name__ == '__main__':
    unittest.main()
