from enum import auto, Enum

class DbType(Enum):
    DB2 = auto()
    MYSQL = auto()
    ORACLE = auto()
    POSTGRESQL = auto()
    SQLITE3 = auto()
    SQL_SERVER = auto()

DBTYPES: dict[str, DbType] = {
    "connector": MYSQL,
    "ibm_db": DB2,
    "ibm_db_dbi": DB2,
    "mssql_python": SQL_SERVER,
    "mysql.connector": MYSQL,
    "oracledb": ORACLE,
    "psycopg": POSTGRESQL,
    "pymssql": SQL_SERVER,
    "pyodbc": SQL_SERVER,
    "sqlite3": SQLITE3,
}
