# A production lexer for SQL. Not much more complex than the trivial one,
# actually, but unlike that one designed to work with yacc. As with the
# trivial lexer, parses something that is mostly ANSI/ISO SQL with a few
# MySQLisms thrown in. Does not try to lex every token out in excruciating
# detail, or to verify syntax, but does process all input tokens (assuming
# correct SQL syntax). For purposes of isolating :name parameter tokens,
# so they can be replaced with whatever (generally l0sing) style the
# database connector needs.

# I m p o r t s

from ply import lex
from dataclasses import dataclass

from .exceptions import Error

# V a r i a b l e s

# Standard token types this lexer supports. We SHOUT here so that
# terminals (i.e. these lex tokens) can be distinguished as what they are
# in the compile (yacc) stage. XXX - This DOES NOT define the order in
# which tokens are recognized, see:
# https://ply.readthedocs.io/en/latest/ply.html#lex
tokens = (
    'WHITE',  # whitespace
    'COMMENT',  # obvious
    'IDENT',  # identifier
    'PARAM',  # :name parameter
    'PSTRING',  # plain 'string'
    'ASTRING',  # annotated'string'
    'MULTIOP',  # multi-character operator
    'SPECIAL'  # SQL special character (sort of)
)

# Key words (both reserved and unreserved), which we also SHOUT, even
# though (per the SQL standard) they are case-insensitive. We don't
# currently make use of all of these, but we do recognize them.
reserved = {
    'ABSOLUTE': None,
    'ACTION': None,
    'ADD': None,
    'ALL': None,
    'ALLOCATE': None,
    'ALTER': None,
    'AND': None,
    'ANY': None,
    'ARE': None,
    'AS': None,
    'ASC': None,
    'ASSERTION': None,
    'AT': None,
    'AUTHORIZATION': None,
    'AVG': None,
    'BEGIN': None,
    'BETWEEN': None,
    'BIT': None,
    'BIT_LENGTH': None,
    'BOTH': None,
    'BY': None,
    'CASCADE': None,
    'CASCADED': None,
    'CASE': None,
    'CAST': None,
    'CATALOG': None,
    'CHAR': 'CHARACTER',
    'CHARACTER': None,
    'CHAR_LENGTH': 'CHARACTER_LENGTH',
    'CHARACTER_LENGTH': None,
    'CHECK': None,
    'CLOSE': None,
    'COALESCE': None,
    'COLLATE': None,
    'COLLATION': None,
    'COLUMN': None,
    'COMMIT': None,
    'CONNECT': None,
    'CONNECTION': None,
    'CONSTRAINT': None,
    'CONSTRAINTS': None,
    'CONTINUE': None,
    'CONVERT': None,
    'CORRESPONDING': None,
    'COUNT': None,
    'CREATE': None,
    'CROSS': None,
    'CURRENT': None,
    'CURRENT_DATE': None,
    'CURRENT_TIME': None,
    'CURRENT_TIMESTAMP': None,
    'CURRENT_USER': None,
    'CURSOR': None,
    'DATE': None,
    'DAY': None,
    'DEALLOCATE': None,
    'DEC': 'DECIMAL',
    'DECIMAL': None,
    'DECLARE': None,
    'DEFAULT': None,
    'DEFERRABLE': None,
    'DEFERRED': None,
    'DELETE': None,
    'DESC': None,
    'DESCRIBE': None,
    'DESCRIPTOR': None,
    'DIAGNOSTICS': None,
    'DISCONNECT': None,
    'DISTINCT': None,
    'DOMAIN': None,
    'DOUBLE': None,
    'DROP': None,
    'ELSE': None,
    'END': None,
    'END-EXEC': None,
    'ESCAPE': None,
    'EXCEPT': None,
    'EXCEPTION': None,
    'EXEC': None,
    'EXECUTE': None,
    'EXISTS': None,
    'EXTERNAL': None,
    'EXTRACT': None,
    'FALSE': None,
    'FETCH': None,
    'FIRST': None,
    'FLOAT': None,
    'FOR': None,
    'FOREIGN': None,
    'FOUND': None,
    'FROM': None,
    'FULL': None,
    'GET': None,
    'GLOBAL': None,
    'GO': None,
    'GOTO': None,
    'GRANT': None,
    'GROUP': None,
    'HAVING': None,
    'HOUR': None,
    'IDENTITY': None,
    'IMMEDIATE': None,
    'IN': None,
    'INDICATOR': None,
    'INITIALLY': None,
    'INNER': None,
    'INPUT': None,
    'INSENSITIVE': None,
    'INSERT': None,
    'INT': 'INTEGER',
    'INTEGER': None,
    'INTERSECT': None,
    'INTERVAL': None,
    'INTO': None,
    'IS': None,
    'ISOLATION': None,
    'JOIN': None,
    'KEY': None,
    'LANGUAGE': None,
    'LAST': None,
    'LEADING': None,
    'LEFT': None,
    'LEVEL': None,
    'LIKE': None,
    'LOCAL': None,
    'LOWER': None,
    'MATCH': None,
    'MAX': None,
    'MIN': None,
    'MINUTE': None,
    'MODULE': None,
    'MONTH': None,
    'NAMES': None,
    'NATIONAL': None,
    'NATURAL': None,
    'NCHAR': None,
    'NEXT': None,
    'NO': None,
    'NOT': None,
    'NULL': None,
    'NULLIF': None,
    'NUMERIC': None,
    'OCTET_LENGTH': None,
    'OF': None,
    'ON': None,
    'ONLY': None,
    'OPEN': None,
    'OPTION': None,
    'OR': None,
    'ORDER': None,
    'OUTER': None,
    'OUTPUT': None,
    'OVERLAPS': None,
    'PAD': None,
    'PARTIAL': None,
    'POSITION': None,
    'PRECISION': None,
    'PREPARE': None,
    'PRESERVE': None,
    'PRIMARY': None,
    'PRIOR': None,
    'PRIVILEGES': None,
    'PROCEDURE': None,
    'PUBLIC': None,
    'READ': None,
    'REAL': None,
    'REFERENCES': None,
    'RELATIVE': None,
    'RESTRICT': None,
    'REVOKE': None,
    'RIGHT': None,
    'ROLLBACK': None,
    'ROWS': None,
    'SCHEMA': None,
    'SCROLL': None,
    'SECOND': None,
    'SECTION': None,
    'SELECT': None,
    'SESSION': None,
    'SESSION_USER': None,
    'SET': None,
    'SIZE': None,
    'SMALLINT': None,
    'SOME': None,
    'SPACE': None,
    'SQL': None,
    'SQLCODE': None,
    'SQLERROR': None,
    'SQLSTATE': None,
    'SUBSTRING': None,
    'SUM': None,
    'SYSTEM_USER': None,
    'TABLE': None,
    'TEMPORARY': None,
    'THEN': None,
    'TIME': None,
    'TIMESTAMP': None,
    'TIMEZONE_HOUR': None,
    'TIMEZONE_MINUTE': None,
    'TO': None,
    'TRAILING': None,
    'TRANSACTION': None,
    'TRANSLATE': None,
    'TRANSLATION': None,
    'TRIM': None,
    'TRUE': None,
    'UNION': None,
    'UNIQUE': None,
    'UNKNOWN': None,
    'UPDATE': None,
    'UPPER': None,
    'USAGE': None,
    'USER': None,
    'USING': None,
    'VALUE': None,
    'VALUES': None,
    'VARCHAR': None,
    'VARYING': None,
    'VIEW': None,
    'WHEN': None,
    'WHENEVER': None,
    'WHERE': None,
    'WITH': None,
    'WORK': None,
    'WRITE': None,
    'YEAR': None,
    'ZONE': None,
}

# Simple tokens
t_PARAM = r':\w+'
t_SPECIAL = r'["%\&\'\(\)\*\+,-\.\/;<=>\?_\|\[\]]'

# C l a s s e s

@dataclass
class SqlToken:
    value: str
    is_param: bool

# F u n c t i o n s

# Defining these otherwise simple tokens with dummy functions instead of a
# string lets us impose our own priority on things. If strings are used,
# PLY imposes its own priority, based on crude regular expression length,
# which often loses.

def t_ignore_WHITE(t):
    r'\s'
    return t

def t_ignore_COMMENT(t):
    r'--.*?(\n|$)|\/\*.*?\*\/'
    return t

def t_PSTRING(t):
    r'\'(\\.|\'\'|[^\'])*\''
    return t

def t_ASTRING(t):
    r'\w+\'(\\.|\'\'|[^\'])*\''
    return t

def t_MULTIOP(t):
    r'<>|<=|>=|\|\||\.\.|!='
    return t

def t_IDENT(t):
    r'\w+|"(\\.|""|[^"])*"|`(\\.|``|[^`])*`'
    shouted = t.value.upper()
    t.type = reserved.get(shouted, 'IDENT') or shouted
    return t

# PLY requires we define this one.

def t_error(t):
    offset = t.lexer.lexpos - len(t.value)
    raise Error(f"bad SQL token at offset {offset}")
