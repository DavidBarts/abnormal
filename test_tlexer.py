# I m p o r t s

import tlexer
import unittest

# V a r i a b l e s

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
    
    def _mktokens(self, seq, is_param=False):
        return [ tlexer.SqlToken(x, is_param) for x in seq ]

# M a i n   P r o g r a m

if __name__ == '__main__':
    unittest.main()
