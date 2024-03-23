abnORMal: A Different Sort of ORM
=================================

Is it an ORM at all? Maybe I should call it an anti-ORM, because it
differs so much from any ORM I have used, with the possible exception of
[LINQ](https://en.wikipedia.org/wiki/Language_Integrated_Query).
Regardless of what you want to call it, abnORMal is designed to ease the
job of moving data between the Python world and the SQL database world.

This package is designed to work with Python 3.11 or higher and any
database for which a [PEP 249](https://peps.python.org/pep-0249/)
compliant database interface exists. It requires [PLY (Python Lex
Yacc)](http://www.dabeaz.com/ply/) as a prerequisite.

This is very much a work in progress, and this is a rudimentary README
that will be replaced with a better one some time soon.

Principles
----------

-   Keep it simple, stupid.
-   Queries are best done in an actual query language (e.g. SQL).
-   Object hierarchies are not, and should not be, relations.
-   Relations are not, and should not be, object hierarchies.
-   Objects, however, can be useful for caching relational data and
    thereby reducing database load.
-   Don't go after a fly with a sledgehammer.

A Few Examples
--------------

These all assume the suppliers and parts database from *A Guide to the
SQL Standard* by Date and Darwen.

S:

<table>
<thead>
<tr class="header">
<th>SNO</th>
<th>SNAME</th>
<th>STATUS</th>
<th>CITY</th>
</tr>
</thead>
<tbody>
<tr class="odd">
<td>S1</td>
<td>Smith</td>
<td>20</td>
<td>London</td>
</tr>
<tr class="even">
<td>S2</td>
<td>Jones</td>
<td>10</td>
<td>Paris</td>
</tr>
<tr class="odd">
<td>S3</td>
<td>Blake</td>
<td>30</td>
<td>Paris</td>
</tr>
<tr class="even">
<td>S4</td>
<td>Clark</td>
<td>20</td>
<td>London</td>
</tr>
<tr class="odd">
<td>S5</td>
<td>Adams</td>
<td>30</td>
<td>Athens</td>
</tr>
</tbody>
</table>

P:

<table>
<thead>
<tr class="header">
<th>PNO</th>
<th>PNAME</th>
<th>COLOR</th>
<th>WEIGHT</th>
<th>CITY</th>
</tr>
</thead>
<tbody>
<tr class="odd">
<td>P1</td>
<td>Nut</td>
<td>Red</td>
<td>12</td>
<td>London</td>
</tr>
</tbody>
</table>
