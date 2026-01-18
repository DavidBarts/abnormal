from enum import auto, Enum

class DbType(Enum):
    DB2 = auto()
    MYSQL = auto()
    ORACLE = auto()
    POSTGRESQL = auto()
    SQLITE3 = auto()
    SQL_SERVER = auto()

DBTYPES: dict[str, DbType] = {
    "connector": DbType.MYSQL,
    "ibm_db": DbType.DB2,
    "ibm_db_dbi": DbType.DB2,
    "mssql_python": DbType.SQL_SERVER,
    "mysql.connector": DbType.MYSQL,
    "oracledb": DbType.ORACLE,
    "psycopg": DbType.POSTGRESQL,
    "pymssql": DbType.SQL_SERVER,
    "pyodbc": DbType.SQL_SERVER,
    "sqlite3": DbType.SQLITE3,
}
