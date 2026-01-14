from abc import ABC, abstractmethod
from collections.abc import Callable
from dataclasses import dataclass
from importlib import import_module
from io import StringIO
from types import ModuleType
from typing import Optional

from .dbtype import DbType, DBTYPES
from .exceptions import InterfaceError

@dataclass
class RowSchema:
    primary: tuple[str]
    others: tuple[str]

class Driver(ABC):
    @abstractmethod
    def row_schema(self, connection, table_name: str):
        ...

    def split_table_name(self, unsplit: str) -> tuple[Optional[str], str]:
        n1, _, n2 = unsplit.partition(".")
        if n2:
            return (n1, n2)
        else:
            return (None, n1)

    # I think this should work everyplace; it is the standard. But putting
    # it here future-proofs us because we can override on braindamaged
    # DBMS's.
    def quote_identifier(self, unquoted):
        with StringIO() as buf:
            buf.write('"')
            for ch in unquoted:
                if ch == '"':
                    buf.write('""')
                else:
                    buf.write(ch)
            buf.write('"')
            return buf.getvalue()

def driver_for(base_driver: ModuleType) -> Driver:
    return _DRIVERS[DBTYPES[base_driver.__name__]]

# DB2

class Db2Driver(Driver):
    def row_schema(self, connection, table_name: str) -> RowSchema:
        dbname, tabname = self.split_table_name(table_name)
        primary = []
        others = []

        if dbname:
            cursor = connection.execute("select colname, keyseq from syscat.columns where tabschema = :dbname and tabname = :tabname order by colno asc", locals())
        else:
            cursor = connection.execute("select colname, keyseq from syscat.columns where tabschema = current_schema and tabname = :tabname order by colno asc", locals())

        sequence = import_module("abnormal").sequence
        try:
            for colname, keyseq in cursor.into(sequence):
                if keyseq is not None and keyseq > 0:
                    primary.append(colname.lower())
                else:
                    others.append(colname.lower())
            if not primary:
                raise InterfaceError(reason="No primary keys reported in {dbname}.{tabname}!")
            return RowSchema(primary=tuple(primary), others=tuple(others))

        finally:
            cursor.close()

# Oracle, described here:
# https://docs.oracle.com/en/database/oracle/oracle-database/26/refrn/ALL_TAB_COLUMNS.html
# Logic for extracting primary keys mostly from here:
# https://www.techonthenet.com/oracle/questions/find_pkeys.php
# C'est le mess.

class OracleDriver(Driver):
    def row_schema(self, connection, table_name: str) -> RowSchema:
        dbname, tabname = self.split_table_name(table_name.upper())

        cursor = connection.cursor
        scalar = import_module("abnormal").scalar
        try:
            if dbname:
                cursor.execute("""SELECT cols.table_name
                    FROM all_constraints cons, all_cons_columns cols
                    WHERE cols.owner = :dbname AND cols.table_name = :tabname
                        AND cons.constraint_name = cols.constraint_name
                        AND cons.owner = cols.owner
                        AND cons.table_name = cols.table_name
                        AND cons.constraint_type = 'P'
                    ORDER BY cols.position""", locals())
            else:
                cursor.execute("""SELECT cols.table_name
                    FROM all_constraints cons, all_cons_columns cols
                    WHERE cols.owner = SYS_CONTEXT('USERENV','CURRENT_SCHEMA')
                        AND cols.table_name = :tabname
                        AND cons.constraint_name = cols.constraint_name
                        AND cons.owner = cols.owner
                        AND cons.table_name = cols.table_name
                        AND cons.constraint_type = 'P'
                    ORDER BY cols.position ASC""", locals())
            primary = tuple([ x.lower() for x in cursor.into(scalar) ])
            if not primary:
                raise InterfaceError(reason="No primary keys reported in {dbname}.{tabname}!")

            if dbname:
                cursor.execute("SELECT COLUMN_NAME FROM ALL_TAB_COLUMNS WHERE OWNER = :dbname AND TABLE_NAME = :tabname ORDER BY COLUMN_ID ASC", locals())
            else:
                cursor.execute("SELECT COLUMN_NAME FROM ALL_TAB_COLUMNS WHERE OWNER = SYS_CONTEXT('USERENV','CURRENT_SCHEMA') AND TABLE_NAME = :tabname ORDER BY COLUMN_ID ASC", locals())
            pset = set(primary)
            others = tuple([ x for x in [ y.lower() for y in cursor.into(scalar) ] if x not in pset ])

            return RowSchema(primary, others)

        finally:
            cursor.close()

# Sqlite3

class Sqlite3Driver(Driver):
    def row_schema(self, connection, table_name: str) -> RowSchema:
        primary = []
        others = []

        cursor = connection.execute("pragma table_info(:table_name)", locals())
        namespace = import_module("abnormal").namespace
        try:
            for entry in cursor.into(namespace):
                if entry.pk:
                    primary.append(entry.name)
                else:
                    others.append(entry.name)
            if not primary:
                raise InterfaceError(reason="No primary keys reported in {tabname}!")
            return RowSchema(primary=tuple(primary), others=tuple(others))

        finally:
            cursor.close()

# Standard: INFORMATION_SCHEMA is the standard way to retrieve schema
# information.  Unfortunately, it is not implemented in a completely
# standard way, even when it is implemented

class StandardDriver(Driver):
    def __init__(self, db_term: str, get_current_db: str) -> None:
        self.db_term = db_term
        self.get_current_db = get_current_db

    def row_schema(self, connection, table_name: str) -> RowSchema:
        dbname, tabname = self.split_table_name(table_name)
        primary = []
        others = []

        if dbname:
            cursor = connection.execute(f"select column_name, column_key from information_schema.columns where table_name = :tabname and {self.db_term} = :dbname order by ordinal_position asc", locals())
        else:
            cursor = connection.execute(f"select column_name, column_key from information_schema.columns where table_name = :tabname and {self.db_term} = {self.get_current_db} order by ordinal_position asc", locals())

        sequence = import_module("abnormal").sequence
        try:
            for column_name, column_key in cursor.into(sequence):
                if column_key is not None and column_key.lower() == "pri":
                    primary.append(column_name.lower())
                else:
                    others.append(column_name.lower())
            if not primary:
                raise InterfaceError(reason="No primary keys reported in {dbname}.{tabname}!")
            return RowSchema(primary=tuple(primary), others=tuple(others))

        finally:
            cursor.close()

# Has to be last, because driver classes have to be defined first.

_DRIVERS: dict[DbType, Driver] = {
    DbType.DB2: Db2Driver(),
    DbType.SQL_SERVER: StandardDriver("table_catalog", "current_catalog"),
    DbType.MYSQL: StandardDriver("table_schema", "database()"),
    DbType.ORACLE: OracleDriver(),
    DbType.POSTGRESQL: StandardDriver("table_catalog", "current_catalog"),
    DbType.SQLITE3: Sqlite3Driver()
}
