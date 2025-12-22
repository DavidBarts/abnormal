# IBM DB2, from "Db2 for Linux, UNIX and Windows", described here:
# https://www.ibm.com/docs/en/db2
# DB2 running on z/os is rather different, sigh. So we currently don't
# support it.

from . import Driver, RowSchema
from .. import sequence
from ..exceptions import InterfaceError

class Db2Driver(Driver):
    def row_schema(self, connection: Connection, table_name: str) -> RowSchema:
        dbname, tabname = self.split_table_name(table_name)
        primary = []
        others = []

        if dbname:
            cursor = connection.execute("select colname, keyseq from syscat.columns where tabschema = :dbname and tabname = :tabname order by colno asc", locals())
        else:
            cursor = connection.execute("select colname, keyseq from syscat.columns where tabschema = current_schema and tabname = :tabname order by colno asc", locals())

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
