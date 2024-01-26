# A trivial lexer for SQL. Mostly ANSI/ISO SQL with a few MySQLisms thrown
# in. Does not try to lex every token out in excruciating detail, or to
# verify syntax, but does process all input tokens (assuming correct SQL
# syntax). For purposes of isolating :name parameter tokens, so they can
# be replaced with whatever (generally l0sing) style the database connector
# needs.

# I m p o r t s

from ply import lex
from dataclasses import dataclass
from exceptions import Error

# V a r i a b l e s

# Standard token types this lexer supports. XXX - This DOES NOT define the
# order in which tokens are recognized, see:
# https://ply.readthedocs.io/en/latest/ply.html#lex
tokens = (
    'white',  # whitespace
    'comment',  # obvious
    'ident',  # identifier
    'param',  # :name parameter
    'pstring',  # plain 'string'
    'astring',  # annotated'string'
    'multiop',  # multi-character operator
    'special'  # SQL special character (sort of)
)

# Simple tokens
t_ident = r'\w+|"(\\.|""|[^"])*"|`(\\.|``|[^`])*`'
t_param = r':\w+'
t_special = r'["%\&\'\(\)\*\+,-\.\/;<=>\?_\|\[\]]'

# C l a s s e s

@dataclass
class SqlToken:
    value: str
    is_param: bool

# F u n c t i o n s

# Non-trivial lexer tokens

def t_white(t):
    r'\s+'
    t.value = " "
    return t

# Defining these trivial tokens with dummy functions even though a string
# lets us impose our own priority on things. If strings are used, PLY imposes
# its own priority, based on crude regular expression length, which often
# loses.

def t_comment(t):
    r'--.*?(\n|$)|\/\*.*?\*\/'
    return t

def t_pstring(t):
    r'\'(\\.|\'\'|[^\'])*\''
    return t

def t_astring(t):
    r'\w+\'(\\.|\'\'|[^\'])*\''
    return t

def t_multiop(t):
    r'<>|<=|>=|\|\||\.\.|!='
    return t

# PLY requires we define this one.

def t_error(t):
    offset = t.lexer.lexpos - len(t.value)
    raise Error(f"bad SQL at offset {offset}")

# This is the sole function that is intended to be called from other
# modules.

def tlexer(sql):
    """
    Tokenize input. Uses a fresh lexer each time so as to be thread safe.
    """
    lexer = lex.lex()
    lexer.input(sql)
    was_white = False
    while True:
        tok = lexer.token()
        if not tok:
            break
        # Compress comments and whitespace runs, if needed
        if tok.type in set(['comment', 'white']):
            if was_white:
                continue
            else:
                was_white = True
                yield SqlToken(" ", False)
        else:
            was_white = False
            yield SqlToken(tok.value, tok.type == "param")
