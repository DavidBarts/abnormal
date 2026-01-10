# Helpers for sending data to the database.
# TODO: needs to be class-based, so can have one instance per connection,
# so each connection gets its own private query cache. Or kill the cache.

# I m p o r t s

from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass
from typing import Any

from .tlexer import SqlToken, tlexer

# V a r i a b l e s

_INITIALS = {
    'qmark': list,
    'format': list,
    'numeric': list,
    'named': dict,
    'pyformat': dict
}

# Also see below at end of file.

type Params = list[Any] | dict[str, Any]

# C l a s s e s

@dataclass(frozen=True)
class CacheKey:
    sql: str
    paramstyle: str

class CacheValue:
    def __init__(self, rawsql, names):
        self.sql = ''.join(rawsql)
        self.names = names

class QueryConverter:
    def __init__(self):
        self._qcache: map[CacheKey, CacheValue] = {}

    def convert(self, query: str, params: Any, paramstyle: str):
        "Convert query and params from vendor-neutral to database-specific form."
        key = CacheKey(query, paramstyle)
        if key in self._qcache:
            cached = self._qcache[key]
        else:
            cached = self._qcache[key] = _CONVERTERS[paramstyle](query, params)
        return self._convert(cached, params, _INITIALS[paramstyle], _APPENDERS[paramstyle])

def _convert(self, cached: CacheValue, params: Any, initial_params: Callable[[], Params], append_params: Callable[[Params, Any, str], None]) -> tuple[str, Params]:
        returned_params = initial_params()
        for name in cached.names:
            append_params(returned_params, params, name)
        return (cached.sql, returned_params)

# F u n c t i o n s

def _positional(query: str, params: Any, repl: str) -> CacheValue:
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
def _numeric(query: str, params: Any) -> CacheValue:
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

def _named(query: str, params: Any, prefix: str, suffix: str) -> CacheValue:
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

def _getname(cname: str) -> str:
    assert cname.startswith(':')
    return cname[1:]

def _getparam(params: Any, name: str) -> Any:
    if isinstance(params, Mapping):
        return params[name]
    else:
        return getattr(params, name)

def _to_list(accum: list[Any], params: Any, name: str) -> None:
    accum.append(_getparam(params, name))

def _to_dict(accum: dict[str, Any], params: Any, name: str) -> None:
    if name not in accum:
        accum[name] = _getparam(params, name)

# Can only be defined after all internal functions are fully defined.

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
