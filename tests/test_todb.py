# I m p o r t s

import unittest
from dataclasses import dataclass
import abnormal.todb as todb

# C l a s s e s

@dataclass
class Suppliers:
    sno: str
    name: str
    status: int
    city: str

# V a r i a b l e s

_Q1 = "insert into suppliers (sno, name, status, city) values (:sno, :name, :status, :city)"
_Q2 = "select * from suppliers where sno = :sno"
_STDREC = { 'sno': 's1', 'name': 'Smith', 'status': 42, 'city': 'London' }
_STDOBJ = Suppliers(**_STDREC)

# T e s t s

class TestTodb(unittest.TestCase):
    # This and the next case should use qmark; if this is changed, test_qmark
    # will have to be more than a no-op.
    def test_mapping(self):
        result = todb.convert(_Q1, _STDREC, 'qmark')
        self.assertEqual(result[0], "insert into suppliers (sno, name, status, city) values (?, ?, ?, ?)")
        self.assertEqual(result[1], [_STDOBJ.sno, _STDOBJ.name, _STDOBJ.status, _STDOBJ.city])
        result = todb.convert(_Q2, _STDREC, 'qmark')
        self.assertEqual(result[0], "select * from suppliers where sno = ?")
        self.assertEqual(result[1], [_STDOBJ.sno])

    def test_popo(self):
        result = todb.convert(_Q1, _STDOBJ, 'qmark')
        self.assertEqual(result[0], "insert into suppliers (sno, name, status, city) values (?, ?, ?, ?)")
        self.assertEqual(result[1], [_STDOBJ.sno, _STDOBJ.name, _STDOBJ.status, _STDOBJ.city])
        result = todb.convert(_Q2, _STDOBJ, 'qmark')
        self.assertEqual(result[0], "select * from suppliers where sno = ?")
        self.assertEqual(result[1], [_STDOBJ.sno])

    # This one is a no-op because qmark is already tested in the above
    # two.
    def test_qmark(self):
        pass

    def test_format(self):
        result = todb.convert(_Q1, _STDOBJ, 'format')
        self.assertEqual(result[0], "insert into suppliers (sno, name, status, city) values (%s, %s, %s, %s)")
        self.assertEqual(result[1], [_STDOBJ.sno, _STDOBJ.name, _STDOBJ.status, _STDOBJ.city])
        result = todb.convert(_Q2, _STDREC, 'format')
        self.assertEqual(result[0], "select * from suppliers where sno = %s")
        self.assertEqual(result[1], [_STDOBJ.sno])

    def test_numeric(self):
        result = todb.convert(_Q1, _STDOBJ, 'numeric')
        self.assertEqual(result[0], "insert into suppliers (sno, name, status, city) values (:1, :2, :3, :4)")
        self.assertEqual(result[1], [_STDOBJ.sno, _STDOBJ.name, _STDOBJ.status, _STDOBJ.city])
        result = todb.convert(_Q2, _STDREC, 'numeric')
        self.assertEqual(result[0], "select * from suppliers where sno = :1")
        self.assertEqual(result[1], [_STDOBJ.sno])

    def test_named(self):
        result = todb.convert(_Q1, _STDOBJ, 'named')
        self.assertEqual(result[0], _Q1)
        self.assertEqual(result[1], _STDREC)
        result = todb.convert(_Q2, _STDREC, 'named')
        self.assertEqual(result[0], _Q2)
        self.assertEqual(result[1], { 'sno': _STDOBJ.sno })

    def test_pyformat(self):
        result = todb.convert(_Q1, _STDOBJ, 'pyformat')
        self.assertEqual(result[0], "insert into suppliers (sno, name, status, city) values (%(sno)s, %(name)s, %(status)s, %(city)s)")
        self.assertEqual(result[1], _STDREC)
        result = todb.convert(_Q2, _STDREC, 'pyformat')
        self.assertEqual(result[0], "select * from suppliers where sno = %(sno)s")
        self.assertEqual(result[1], { 'sno': _STDOBJ.sno })

    def test_badrefs(self):
        query = "select * from suppliers where sno = :gunk"
        self.assertRaises(AttributeError, todb.convert, query, _STDOBJ, 'qmark')
        self.assertRaises(KeyError, todb.convert, query, _STDREC, 'qmark')

    def test_caching(self):
        query = "select * from parts where pno = :pno"
        pno = "p1"
        before = len(todb._qcache)
        result1 = todb.convert(query, locals(), 'qmark')
        after = len(todb._qcache)
        self.assertGreater(after, before)
        result2 = todb.convert(query, locals(), 'qmark')
        self.assertEqual(len(todb._qcache), after)
        self.assertEqual(result1, result2)

# M a i n   P r o g r a m

if __name__ == '__main__':
    unittest.main()
