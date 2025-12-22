# Sqlite3

from . import Driver, RowSchema
from .. import namespace
from ..exceptions import InterfaceError

class Sqlite3Driver(Driver):
    def row_schema(self, connection: Connection, table_name: str) -> RowSchema:
        primary = []
        others = []

        cursor = connection.execute("pragma table_info(:table_name)", locals())
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
