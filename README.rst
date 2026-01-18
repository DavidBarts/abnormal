######################
abnORMal: The Anti-ORM
######################

Is it an ORM at all? Maybe I should call it an anti-ORM, because it differs
so much from any ORM I have used, with the possible exception of
`LINQ <https://en.wikipedia.org/wiki/Language_Integrated_Query>`_.
Regardless of what you want to call it, abnORMal is designed to ease the job
of moving data between the Python world and the SQL database world.

This module is very much in the same spirit as the
`SQLX <https://github.com/jmoiron/sqlx>`_
library for the Go programming language, which I became aware of partway
through writing this package. That package's author falls short of
calling his package an ORM, saying it merely focuses on data marshalling
and unmarshalling, so I guess that's probably the best way to describe
this package.

I have long disliked both ORM's (which, contrary to the claims their
advocates make require *a lot* of boilerplate in my experience, and at
any rate lack most of the power and flexibility of SQL), and raw database
connections (which require their own set of tedious work to retrieve
and send data).

This package is designed to work with Python 3.11 or higher and any database
for which a `PEP 249 <https://peps.python.org/pep-0249/>`_ compliant
database interface exists. It does not itself have any prerequisites.

Principles
==========

* Keep it simple, stupid.
* Queries are best done in an actual query language (e.g. SQL).
* Object hierarchies are not, and should not be, relations.
* Relations are not, and should not be, object hierarchies.
* Objects, however, can be useful for caching relational data and
  thereby reducing database load.
* Don't go after a fly with a sledgehammer.
* Do automate repetitive tasks.
* Avoid making the programmer stutter.

A Few Examples
==============

The package's features are mostly described in this section. More comprehensive
API documentation is coming soon.

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

Of course, we can read parameters from object attributes as well.
Assuming the ``Supplier`` dataclass::

    from abnormal import scalar
    def get_others(supplier):
        curs = conn.cursor()
        return list(curs.execute("select name from suppliers where city = :city and sno <> :sno", supplier).into(scalar))

Abnormal is smart enough to know the basics of SQL syntax, and won't be
fooled by things like the following (which will set the supplier name
literally to ":name")::

    curs.execute("update suppliers set name = ':name' where id = 'S5'", locals())

Inserts and Updates
-------------------

These can lead to what software engineers sometimes call "stuttering,"
the presence of repetitive identifiers in code. The classic one often
comes up when declaring a new object variable in Java::

    Connection connection = new Connection();

With abnORMal, stuttering commonly can rear its head when inserting
or updating::

    conn.execute("insert into suppliers (sno, name, status, city) values (:sno, :name, :status, :city)", locals())
    conn.execute("update suppliers set name = :name, status = :status, city = :city where sno = :sno", locals())

Thanks to the ``insert_into`` and ``update`` methods, this awkwardness and
verbosity is not necessary::

    conn.insert_into("suppliers").from_source(locals())
    conn.update("suppliers").from_source(locals())

With both convenience methods, column names are matched up to attribute
or key names (case insensitively, if need be); the match must be
non-ambiguous (e.g. if the data source contains both ``sno`` and
``SNO``, the match will fail). The information in the database's own
internal schema is be used to accomplish this.

Rows to update are located by primary key, so all primary key fields
must have a corresponding item in the data source, else
``IncompleteDataError`` will be raised.  Note that it is *not* mandatory
for all (or even any) primary key fields to be defined in the data
source when inserting. This is because such fields often have defaults
to defined in the schema (if they don't, you will get an error from the
database itself).

It is possible to filter out or select specific fields to update or insert,
using the ``exclude`` and ``include`` methods respectively::

    conn.insert_into("suppliers").excluding("city, status").from_source(locals())
    conn.update("suppliers").including("sno", "status", "city").from_source(locals())

Note that you may use ``including`` or ``excluding`` but not specify both
at once.
