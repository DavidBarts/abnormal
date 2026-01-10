# INFORMATION_SCHEMA is the standard way to retrieve schema information.
# Unfortunately, it is not implemented in a completely standard way.

from . import Driver, RowSchema
from .. import sequence
from ..exceptions import InterfaceError

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
