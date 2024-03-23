Introduction
============

Abnormal is a Python library to make getting data from an SQL database into
Python, and the reverse process, easier. It works with any
`PEP 249 <https://peps.python.org/pep-0249/>`_ compliant
database interface module, and itself has a design similar to what PEP 249
specifies. It consists of an SQL translator and a data mapper.

The SQL translator is currently quite limited. It maps the ``named`` paramstyle
(see PEP 249) into whatever the database being used expects to see… and that's
it. I would like to add support for some of the other commonly-used nonstandard
aspects of SQL (see `here <https://en.wikibooks.org/wiki/SQL_Dialects_Reference>`_
for full list). Hopefully soon. Until then, it turns out that mapping
paramstyles alone does *a lot* to smooth out the differences between SQL
dialects.

The data mapper works both when sending data to the database and receiving
data from it. Going to the database, it can read data from most python objects.
Coming from the database, it can produce mappings, sequences, dataclasses,
and anything for which a factory method capable of supporting keyword arguments
exists. It does all this without requiring the programmer to produce undue
amounts of boilerplate code ahead of time specifying how things are to be
mapped.

Is Abnormal an ORM or isn't it? Ultimately, this is not as important to me as
asking if Abnormal is useful or not. I find it useful, and easier to use than
any ORM (or perhaps, any other ORM) that I have tried.