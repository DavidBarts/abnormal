# Helpers for sending data to the database.
# TODO: implement caching (pass paramstyle to all but possibly _numeric).

# I m p o r t s

from collections.abc import Mapping

from tlexer import SqlToken, tlexer

# F u n c t i o n s

def convert(query, params, paramstyle):
    "Convert query and params from vendor-neutral to database-specific form."
    return _DISPATCH[paramstyle](query, params)

def _positional(query, params, repl):
    rquery = []
    rparams = []
    for token in tlexer(query):
        if token.is_param:
            rquery.append(repl)
            rparams.append(_getparam(params, _getname(token.value)))
        else:
            rquery.append(token.value)
    return _mktuple(rquery, rparams)

# XXX - PEP0249 never explicitly mentions it, but the parameters in this
# style apparently use 1-based indexing. See:
# https://github.com/python/cpython/issues/99953
def _numeric(query, params):
    rquery = []
    rparams = []
    index = {}
    for token in tlexer(query):
        if token.is_param:
            name = _getname(token.value)
            if name not in index:
                index[name] = str(len(rparams) + 1)
                rparams.append(_getparam(params, name))
            rquery.append(':' + index[name])
        else:
            rquery.append(token.value)
    return _mktuple(rquery, rparams)

def _named(query, params, prefix, suffix):
    rquery = []
    rparams = {}
    for token in tlexer(query):
        if token.is_param:
            name = _getname(token.value)
            if name not in rparams:
                rparams[name] = _getparam(params, name)
            rquery.append(prefix + name + suffix)
        else:
            rquery.append(token.value)
    return _mktuple(rquery, rparams)

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

# XXX - Can only be defined after all internal functions are fully defined.
_DISPATCH = {
    'qmark': lambda q, p: _positional(q, p, '?'),
    'format': lambda q, p: _positional(q, p, '%s'),
    'numeric': _numeric,
    'named': lambda q, p: _named(q, p, ':', ''),
    'pyformat': lambda q, p: _named(q, p, '%(', ')s')
}
