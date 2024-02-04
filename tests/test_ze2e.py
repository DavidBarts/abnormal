# End to end tests. Begins with z to run last.

# I m p o r t s

import os, sys

import sqlite3
import unittest
from dataclasses import dataclass

from abnormal import connect, mapping, scalar, sequence, Error, UnexpectedResultError

# C l a s s e s

@dataclass
class Suppliers:
    sno: str
    name: str
    status: int
    city: str

# V a r i a b l e s

DBFILE = "e2e.db"

# T e s t s

class TestEndToEnd(unittest.TestCase):
    def setUp(self):
        self.conn = connect(sqlite3, DBFILE)
        curs = self.conn.cursor()
        curs.execute("create table suppliers ( sno integer not null primary key, name text, status integer, city text )")
        curs.executemany("insert into suppliers (sno, name, status, city) values (:sno, :name, :status, :city)",
            [
                Suppliers(1, "Smith", 20, "London"),
                Suppliers(2, "Jones", 10, "Paris"),
                Suppliers(3, "Blake", 30, "Paris"),
                Suppliers(4, "Clark", 20, "London"),
                Suppliers(5, "Adams", 30, "Athens")
            ])
        curs.close()

    def tearDown(self):
        self.conn.close()
        os.remove(DBFILE)

    # def test_cursor(self):
    #     # Already tested in self.setUp.
    #     pass

    def test_executemany_conn(self):
        # We have tested this on a cursor, try testing it on a connection
        oldcount = self.conn.execute("select count(*) from suppliers").into1(scalar)
        self.conn.executemany("insert into suppliers (sno, name, status, city) values (:sno, :name, :status, :city)",
            [
                Suppliers(oldcount + 1, "Herrera", 15, "Madrid"),
                Suppliers(oldcount + 2, "Schmidt", 15, "Berlin")
            ])
        newrecs = set(self.conn.execute("select name from suppliers where sno > :oldcount", locals()).into(scalar))
        self.assertIn("Herrera", newrecs)
        self.assertIn("Schmidt", newrecs)
        self.assertEqual(len(newrecs), 2)

    # def test_execute_conn(self):
    #     # Already tested in many other tests.
    #     pass

    # def test_execute_curs(self):
    #     # Tested in test_mapping.
    #     pass

    def test_scalar(self):
        # General case already in setUp; test the multi-result case here
        curs = self.conn.execute("select * from suppliers where sno = 1")
        self.assertRaises(UnexpectedResultError, curs.into1, scalar)

    def test_sequence(self):
        name, status = self.conn.execute("select name, status from suppliers where sno = 1").into1(sequence)
        self.assertEqual(name, "Smith")
        self.assertEqual(status, 20)

    def test_into1(self):
        self.assertEqual(self.conn.execute("select name from suppliers where sno = 1").into1(scalar), "Smith")
        curs = self.conn.execute("select name from suppliers where sno = 99")
        self.assertRaises(UnexpectedResultError, curs.into1, scalar)

    def test_into(self):
        results = list(self.conn.execute("select * from suppliers where city = 'Paris'").into(Suppliers))
        self.assertEqual(len(results), 2)
        self.assertEqual(results[0].city, 'Paris')
        self.assertEqual(results[1].city, 'Paris')
        results = list(self.conn.execute("select * from suppliers where city = 'Moscow'").into(Suppliers))
        self.assertEqual(len(results), 0)

    def test_mapping(self):
        curs = self.conn.cursor()
        d = curs.execute("select * from suppliers where sno = 1").into1(mapping)
        self.assertEqual(d['sno'], 1)
        self.assertEqual(d['name'], 'Smith')
        self.assertEqual(d['status'], 20)
        self.assertEqual(d['city'], 'London')
        self.assertEqual(len(d), 4)

# M a i n   P r o g r a m

if __name__ == '__main__':
    unittest.main()
