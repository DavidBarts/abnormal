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

These all assume the suppliers and parts database from
*A Guide to the SQL Standard* by Date and Darwen.

S:

===  =====  ======  ======
SNO  SNAME  STATUS  CITY
===  =====  ======  ======
S1   Smith  20      London
S2   Jones  10      Paris
S3   Blake  30      Paris
S4   Clark  20      London
S5   Adams  30      Athens
===  =====  ======  ======

P:

===  =====  =====  ======  ======
PNO  PNAME  COLOR  WEIGHT  CITY
===  =====  =====  ======  ======
P1   Nut    Red    12      London
===  =====  =====  ======  ======
