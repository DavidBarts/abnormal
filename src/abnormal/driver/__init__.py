from abc import ABC, abstractmethod
from collections.abc import Callable
from dataclasses import dataclass
from io import StringIO
from types import ModuleType
from typing import Optionsl

from .dbtype import DbType, DBTYPES
from .standard import StandardDriver
from .db2 import Db2Driver
from .oracle import OracleDriver

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
        with StringIO('"') as buf:
            for ch in unquoted:
                if ch == '"':
                    buf.write('""')
                else:
                    buf.write(ch)
            buf.write('"')
            return buf.getvalue()

_DRIVERS: dict[DbType, Callable[[], Driver]] = {
    DbType.DB2: Db2Driver(),
    DbType.SQL_SERVER: StandardDriver("table_catalog", "current_catalog"),
    DbType.MYSQL: StandardDriver("table_schema", "database()"),
    DbType.ORACLE: OracleDriver(),
    DbType.POSTGRESQL: StandardDriver("table_catalog", "current_catalog"),
    DbType.SQLITE3: Sqlite3Driver()
}

def driver_for(base_driver: ModuleType) -> Driver:
    return _DRIVERS[DBTYPES[base_driver.__name__]]
