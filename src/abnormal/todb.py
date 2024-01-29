# Helpers for sending data to the database.

# I m p o r t s

from collections.abc import Mapping
from dataclasses import dataclass

from .tlexer import SqlToken, tlexer

# V a r i a b l e s

_INITIALS = {
    'qmark': list,
    'format': list,
    'numeric': list,
    'named': dict,
    'pyformat': dict
}

_qcache = {}

# C l a s s e s

@dataclass(frozen=True)
class CacheKey:
    sql: str
    paramstyle: str

class CacheValue:
    def __init__(self, rawsql, names):
        self.sql = ''.join(rawsql)
        self.names = names

# F u n c t i o n s

def convert(query, params, paramstyle):
    "Convert query and params from vendor-neutral to database-specific form."
    key = CacheKey(query, paramstyle)
    if key in _qcache:
        cached = _qcache[key]
    else:
        cached = _qcache[key] = _CONVERTERS[paramstyle](query, params)
    return _convert(cached, params, _INITIALS[paramstyle](), _APPENDERS[paramstyle])

def _convert(cached, params, initial_params, append_params):
    returned_params = initial_params
    for name in cached.names:
        append_params(returned_params, params, name)
    return (cached.sql, returned_params)

def _positional(query, params, repl):
    rquery = []
    rnames = []
    for token in tlexer(query):
        if token.is_param:
            rquery.append(repl)
            rnames.append(_getname(token.value))
        else:
            rquery.append(token.value)
    return CacheValue(rquery, rnames)

# XXX - PEP0249 never explicitly mentions it, but the parameters in this
# style apparently use 1-based indexing. See:
# https://github.com/python/cpython/issues/99953
def _numeric(query, params):
    rquery = []
    rnames = []
    index = {}
    for token in tlexer(query):
        if token.is_param:
            name = _getname(token.value)
            if name not in index:
                index[name] = str(len(rnames) + 1)
                rnames.append(name)
            rquery.append(':' + index[name])
        else:
            rquery.append(token.value)
    return CacheValue(rquery, rnames)

def _named(query, params, prefix, suffix):
    rquery = []
    rnames = []
    for token in tlexer(query):
        if token.is_param:
            name = _getname(token.value)
            rnames.append(name)
            rquery.append(prefix + name + suffix)
        else:
            rquery.append(token.value)
    return CacheValue(rquery, rnames)

def _getname(cname):
    assert cname.startswith(':')
    return cname[1:]

def _getparam(params, name):
    if isinstance(params, Mapping):
        return params[name]
    else:
        return getattr(params, name)

def _mktuple(rquery, params):
    return (''.join(rquery), params)

def _to_list(accum, params, name):
    accum.append(_getparam(params, name))

def _to_dict(accum, params, name):
    if name not in accum:
        accum[name] = _getparam(params, name)

# XXX - Can only be defined after all internal functions are fully defined.

_APPENDERS = {
    'qmark': _to_list,
    'format': _to_list,
    'numeric': _to_list,
    'named': _to_dict,
    'pyformat': _to_dict
}

_CONVERTERS = {
    'qmark': lambda q, p: _positional(q, p, '?'),
    'format': lambda q, p: _positional(q, p, '%s'),
    'numeric': _numeric,
    'named': lambda q, p: _named(q, p, ':', ''),
    'pyformat': lambda q, p: _named(q, p, '%(', ')s')
}
