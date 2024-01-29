# I m p o r t s

import abnormal.tlexer as tlexer
import unittest

# T e s t s

class TestTlexer(unittest.TestCase):
    def test_whitespace(self):
        "All whitespace should be treated equal."
        queries = [ "select * from suppliers", "select\t* from suppliers",
            "select  * from suppliers", "select\n* from suppliers",
            "select\r\n* from suppliers" ]
        expected = [ tlexer.SqlToken("select", False),
            tlexer.SqlToken(" ", False), tlexer.SqlToken("*", False),
            tlexer.SqlToken(" ", False), tlexer.SqlToken("from", False),
            tlexer.SqlToken(" ", False), tlexer.SqlToken("suppliers", False) ]
        self._vqueries(queries, expected)

    def _vqueries(self, queries, expected):
        for query in queries:
            result = list(tlexer.tlexer(query))
            for i in range(len(result)):
                self.assertTrue(i < len(expected),
                    f"query = {query!r}, overly long result!")
                self.assertEqual(result[i], expected[i],
                    f"query = {query!r}, token = {i}")
            self.assertEqual(len(result), len(expected),
                f"query = {query!r}, runt result!")

    def test_comments(self):
        "Both C and SQL style comments map to whitespace."
        queries = [ "select-- a comment\n* from suppliers",
            "select -- comment with space before\n* from suppliers",
            "select/* C-style comment */* from suppliers",
            "select /* C-style with spaces */ * from suppliers" ]
        expected = [ tlexer.SqlToken("select", False),
            tlexer.SqlToken(" ", False), tlexer.SqlToken("*", False),
            tlexer.SqlToken(" ", False), tlexer.SqlToken("from", False),
            tlexer.SqlToken(" ", False), tlexer.SqlToken("suppliers", False) ]
        self._vqueries(queries, expected)

    def test_param(self):
        "Test :parameters."
        q1 = "insert into suppliers (sno, sname, status, city) values (:sno, :sname, :status, :city)"
        e1 = [ tlexer.SqlToken('insert', False), tlexer.SqlToken(' ', False),
            tlexer.SqlToken('into', False), tlexer.SqlToken(' ', False),
            tlexer.SqlToken('suppliers', False), tlexer.SqlToken(' ', False),
            tlexer.SqlToken('(', False), tlexer.SqlToken('sno', False),
            tlexer.SqlToken(',', False), tlexer.SqlToken(' ', False),
            tlexer.SqlToken('sname', False), tlexer.SqlToken(',', False),
            tlexer.SqlToken(' ', False), tlexer.SqlToken('status', False),
            tlexer.SqlToken(',', False), tlexer.SqlToken(' ', False),
            tlexer.SqlToken('city', False), tlexer.SqlToken(')', False),
            tlexer.SqlToken(' ', False), tlexer.SqlToken('values', False),
            tlexer.SqlToken(' ', False), tlexer.SqlToken('(', False),
            tlexer.SqlToken(':sno', True), tlexer.SqlToken(',', False),
            tlexer.SqlToken(' ', False), tlexer.SqlToken(':sname', True),
            tlexer.SqlToken(',', False), tlexer.SqlToken(' ', False),
            tlexer.SqlToken(':status', True), tlexer.SqlToken(',', False),
            tlexer.SqlToken(' ', False), tlexer.SqlToken(':city', True),
            tlexer.SqlToken(')', False) ]
        self._vqueries([q1], e1)
        q2 = "select * from suppliers where sno = :sno"
        e2 = [ tlexer.SqlToken('select', False), tlexer.SqlToken(' ', False),
            tlexer.SqlToken('*', False), tlexer.SqlToken(' ', False),
            tlexer.SqlToken('from', False), tlexer.SqlToken(' ', False),
            tlexer.SqlToken('suppliers', False), tlexer.SqlToken(' ', False),
            tlexer.SqlToken('where', False), tlexer.SqlToken(' ', False),
            tlexer.SqlToken('sno', False), tlexer.SqlToken(' ', False),
            tlexer.SqlToken('=', False), tlexer.SqlToken(' ', False),
            tlexer.SqlToken(':sno', True) ]
        self._vqueries([q2], e2)

    def test_strings(self):
        query = "insert into suppliers (sno, sname) values ('s1', ':starts_with_colon')"
        expected = [ tlexer.SqlToken('insert', False),
            tlexer.SqlToken(' ', False), tlexer.SqlToken('into', False),
            tlexer.SqlToken(' ', False), tlexer.SqlToken('suppliers', False),
            tlexer.SqlToken(' ', False), tlexer.SqlToken('(', False),
            tlexer.SqlToken('sno', False), tlexer.SqlToken(',', False),
            tlexer.SqlToken(' ', False), tlexer.SqlToken('sname', False),
            tlexer.SqlToken(')', False), tlexer.SqlToken(' ', False),
            tlexer.SqlToken('values', False), tlexer.SqlToken(' ', False),
            tlexer.SqlToken('(', False), tlexer.SqlToken("'s1'", False),
            tlexer.SqlToken(',', False), tlexer.SqlToken(' ', False),
            tlexer.SqlToken("':starts_with_colon'", False),
            tlexer.SqlToken(')', False) ]
        self._vqueries([query], expected)
        q2 = "insert into suppliers (sno, sname) values (en_US's1', en_CA':starts_with_colon')"
        e2 = [ tlexer.SqlToken('insert', False),
            tlexer.SqlToken(' ', False), tlexer.SqlToken('into', False),
            tlexer.SqlToken(' ', False), tlexer.SqlToken('suppliers', False),
            tlexer.SqlToken(' ', False), tlexer.SqlToken('(', False),
            tlexer.SqlToken('sno', False), tlexer.SqlToken(',', False),
            tlexer.SqlToken(' ', False), tlexer.SqlToken('sname', False),
            tlexer.SqlToken(')', False), tlexer.SqlToken(' ', False),
            tlexer.SqlToken('values', False), tlexer.SqlToken(' ', False),
            tlexer.SqlToken('(', False), tlexer.SqlToken("en_US's1'", False),
            tlexer.SqlToken(',', False), tlexer.SqlToken(' ', False),
            tlexer.SqlToken("en_CA':starts_with_colon'", False),
            tlexer.SqlToken(')', False) ]
        self._vqueries([q2], e2)

    def test_strings_quotes(self):
        query = r"select * from suppliers where sname = 'O''Rourke' || sname = 'O\'Brien'"
        expected = [ tlexer.SqlToken('select', False),
            tlexer.SqlToken(' ', False), tlexer.SqlToken('*', False),
            tlexer.SqlToken(' ', False), tlexer.SqlToken('from', False),
            tlexer.SqlToken(' ', False), tlexer.SqlToken('suppliers', False),
            tlexer.SqlToken(' ', False), tlexer.SqlToken('where', False),
            tlexer.SqlToken(' ', False), tlexer.SqlToken('sname', False),
            tlexer.SqlToken(' ', False), tlexer.SqlToken('=', False),
            tlexer.SqlToken(' ', False), tlexer.SqlToken("'O''Rourke'", False),
            tlexer.SqlToken(' ', False), tlexer.SqlToken('||', False),
            tlexer.SqlToken(' ', False), tlexer.SqlToken('sname', False),
            tlexer.SqlToken(' ', False), tlexer.SqlToken('=', False),
            tlexer.SqlToken(' ', False), tlexer.SqlToken("'O\\'Brien'", False) ]
        self._vqueries([query], expected)

    def test_quoted_idents(self):
        q1 = "select * from `suppliers`"
        e1 = [ tlexer.SqlToken( 'select',  False),
            tlexer.SqlToken( ' ',  False), tlexer.SqlToken( '*',  False),
            tlexer.SqlToken( ' ',  False), tlexer.SqlToken( 'from',  False),
            tlexer.SqlToken( ' ',  False),
            tlexer.SqlToken( '`suppliers`',  False) ]
        self._vqueries([q1], e1)
        q2 = r"select * from ```suppliers\``"
        e2 = e1
        e2[-1].value = r"```suppliers\``"
        self._vqueries([q2], e2)
        q3 = 'select * from "suppliers"'
        e3 = [ tlexer.SqlToken( 'select',  False),
            tlexer.SqlToken( ' ',  False), tlexer.SqlToken( '*',  False),
            tlexer.SqlToken( ' ',  False), tlexer.SqlToken( 'from',  False),
            tlexer.SqlToken( ' ',  False),
            tlexer.SqlToken( '"suppliers"',  False) ]
        self._vqueries([q3], e3)
        q4 = r'select * from "\"suppliers"""'
        e4 = e3
        e4[-1].value = r'"\"suppliers"""'
        self._vqueries([q4], e4)

    def test_multiop(self):
        query = "select * from suppliers where sname <> 'O''Rourke' || sname <= 'O''Brien'"
        expected = [ tlexer.SqlToken('select', False),
            tlexer.SqlToken(' ', False), tlexer.SqlToken('*', False),
            tlexer.SqlToken(' ', False), tlexer.SqlToken('from', False),
            tlexer.SqlToken(' ', False), tlexer.SqlToken('suppliers', False),
            tlexer.SqlToken(' ', False), tlexer.SqlToken('where', False),
            tlexer.SqlToken(' ', False), tlexer.SqlToken('sname', False),
            tlexer.SqlToken(' ', False), tlexer.SqlToken('<>', False),
            tlexer.SqlToken(' ', False), tlexer.SqlToken("'O''Rourke'", False),
            tlexer.SqlToken(' ', False), tlexer.SqlToken('||', False),
            tlexer.SqlToken(' ', False), tlexer.SqlToken('sname', False),
            tlexer.SqlToken(' ', False), tlexer.SqlToken('<=', False),
            tlexer.SqlToken(' ', False), tlexer.SqlToken("'O''Brien'", False)]
        self._vqueries([query], expected)

    def _mktokens(self, seq, is_param=False):
        return [ tlexer.SqlToken(x, is_param) for x in seq ]

# M a i n   P r o g r a m

if __name__ == '__main__':
    unittest.main()
