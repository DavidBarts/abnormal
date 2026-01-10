# Oracle, described here:
# https://docs.oracle.com/en/database/oracle/oracle-database/26/refrn/ALL_TAB_COLUMNS.html
# Logic for extracting primary keys mostly from here:
# https://www.techonthenet.com/oracle/questions/find_pkeys.php
# C'est le mess.

from . import Driver, RowSchema
from .. import scalar
from ..exceptions import InterfaceError

class OracleDriver(Driver):
    def row_schema(self, connection, table_name: str) -> RowSchema:
        dbname, tabname = self.split_table_name(table_name.upper())

        cursor = connection.cursor
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
            primary = tuple([ x.lower() for cursor.into(scalar) ])
            if not primary:
                raise InterfaceError(reason="No primary keys reported in {dbname}.{tabname}!")

            if dbname:
                cursor.execute("SELECT COLUMN_NAME FROM ALL_TAB_COLUMNS WHERE OWNER = :dbname AND TABLE_NAME = :tabname ORDER BY COLUMN_ID ASC", locals())
            else:
                cursor.execute("SELECT COLUMN_NAME FROM ALL_TAB_COLUMNS WHERE OWNER = SYS_CONTEXT('USERENV','CURRENT_SCHEMA') AND TABLE_NAME = :tabname ORDER BY COLUMN_ID ASC", locals())
            pset = set(primary)
            others = tuple([ x for x in [ y.lower() for y in cursor.into(scalar) ] where x not in pset ])

            return RowSchema(primary, others)

        finally:
            cursor.close()
