.. Abnormal documentation master file, created by
   sphinx-quickstart on Tue Feb  6 18:28:12 2024.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Abnormal, the Un-ORM
====================

Abnormal is a Python library to make getting data from an SQL database into
Python, and the reverse process, easier. It works with any PEP 249 compliant
database interface module, and itself has a design similar to such a module.

It does the above while allowing the programmer the full expressive power of SQL
and without requiring the programmer to write lots of boilerplate defining
the object to relational mapping ahead of time.

Abnormal consists of an SQL Translator (i.e. maps standardized SQL into a
database-specific form) and a data mapper (i.e. simplifies getting data to
and from an SQL database).

Requirements
------------

* Python 3.11 or higher (may support earlier versions of Python 3, but
  has not been tested with them).
* PLY (Python Lex Yacc) 3.11 or higher (again, may work with earlier
  versions, but has not been tested with them).
* Any PEP 249 compliant database interface module.

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   introduction
   principles
   quickstart
   api

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
