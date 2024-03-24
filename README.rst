#################################
abnORMal: A Different Sort of ORM
#################################

Is it an ORM at all? Maybe I should call it an anti-ORM, because it differs
so much from any ORM I have used, with the possible exception of
`LINQ <https://en.wikipedia.org/wiki/Language_Integrated_Query>`_.
Regardless of what you want to call it, abnORMal is designed to ease the job
of moving data between the Python world and the SQL database world.

This package is designed to work with Python 3.11 or higher and any database
for which a `PEP 249 <https://peps.python.org/pep-0249/>`_ compliant
database interface exists. It requires
`PLY (Python Lex Yacc) <http://www.dabeaz.com/ply/>`_ as a prerequisite.

This is very much a work in progress, and this is a rudimentary README that
will be replaced with a better one some time soon.

Principles
==========

* Keep it simple, stupid.
* Queries are best done in an actual query language (e.g. SQL).
* Object hierarchies are not, and should not be, relations.
* Relations are not, and should not be, object hierarchies.
* Objects, however, can be useful for caching relational data and
  thereby reducing database load.
* Don't go after a fly with a sledgehammer.

A Few Examples
==============

These examples all assume a database containing the following ``suppliers`` table:

===  =====  ======  ======
SNO  NAME   STATUS  CITY
===  =====  ======  ======
S1   Smith  20      London
S2   Jones  10      Paris
S3   Blake  30      Paris
S4   Clark  20      London
S5   Adams  30      Athens
===  =====  ======  ======

Connecting to the Database
--------------------------

An abnORMal connection simply wraps a PEP 249 connection object, so one way
to connect might be::

    import sqlite3
    import abnormal
    conn = abnormal.Connection(sqlite3.connect("suppliers_parts.db"), sqlite3.paramstyle)

However, it is a little repetitive and error-prone to have to pass the
paramstyle value, so a convenience routine exists to make connecting a
bit more concise (and a bit more like PEP 249)::

    import sqlite3
    import abnormal
    conn = abnormal.connect(sqlite3, "suppliers_parts.db")

All subsequent examples assume an abnORMal connection object, ``conn``.

Retrieve an Entry as a Dict
---------------------------

Perhaps the most basic thing is to retrieve something by its primary key::

    from abnormal import mapping
    curs = conn.cursor()
    result = curs.execute("select * from suppliers where sno = 'S1'").into1(mapping)
    print("Supplier name is", result['name'])

Retrieve an Entry as a Data Class
---------------------------------

Of course, it can be much more useful to extract the result into an object.
abnORMal is designed to play nice with Python ``dataclass`` objects::

    from dataclasses import dataclass

    @dataclass
    class Supplier:
        sno: str
        name: str
        status: int
        city: str

    curs = conn.cursor()
    result = curs.execute("select * from suppliers where sno = 'S1'").into1(Supplier)
    print(f"Supplier name is {result.name}.")

Retrieve an Entry as a Sequence
-------------------------------

Fans of old school PEP 249 will be happy to learn you can retrieve results as
sequences, too::

    from abnormal import sequence
    curs = conn.cursor()
    result = curs.execute("select * from suppliers where sno = 'S1'").into1(sequence)
    print("Supplier name is", result[0])

Retrieve a Single Column as a Scalar
------------------------------------

If you are just interested in a single field, however, it can be simpler to
extract the data into a scalar::

    from abnormal import scalar
    curs = conn.cursor()
    result = curs.execute("select name from suppliers where sno = 'S1'").into1(scalar)
    print(f"Supplier name is {result}.")

Retrieving Multiple Rows
------------------------

Extraction of multiple results is done via the ``into`` generator::

    # same Supplier dataclass as above
    curs = conn.cursor()
    for result in curs.execute("select * from suppliers where city = 'Paris'").into(Supplier):
        print(f"Supplier {result.name} is in Paris with status {result.status}")

``into`` supports unrolling into the same sorts of things as ``into1`` does::

    from abnormal import scalar
    curs = conn.cursor()
    parisians = list(curs.execute("select name from suppliers where city = 'Paris'").into(scalar))

Using Parameterized Queries
---------------------------


No matter what query paramstyle the PEP 249 connector uses, abnORMal always
uses the *named* one, so as to smooth out the differences between the various
connectors::

    from abnormal import scalar
    def get_suppliers_in(city):
        curs = conn.cursor()
        return list(curs.execute("select name from suppliers where city = :city", {'city': city}).into(scalar))

But that is getting needlessly repetitive. Thankfully, it is trivial to get
abnORMal to read from local variables::

    from abnormal import scalar
    def get_suppliers_in(city):
        curs = conn.cursor()
        return list(curs.execute("select name from suppliers where city = :city", locals()).into(scalar))

Of course, we can read parameters from object attributes as well. Assuming the ``Supplier`` dataclass::

    from abnormal import scalar
    def get_others(supplier):
        curs = conn.cursor()
        return list(curs.execute("select name from suppliers where city = :city and sno <> :sno", supplier).into(scalar))
