# Insert (insert_into) and update operations support.
# XXX - we don't use type declarations here in constructors (and possibly
# strategically elsewhere) because using them raises circular import
# issues.

from collections.abc import Mapping

from .driver import driver_for
from .todb import convert

class PendingInsert:
    def __init__(self, cursor, table):
        self.cursor = cursor
        self.table = table

    def source(self, params):
        driver = cursor.connection._driver
        row_schema = driver.row_schema(self.table)
        
        # Find many params as we can, case insensitive, w/o ambiguity.
        names = _names_from_params(params)
        casemap = _case_map_for_names(names)
        for name in row_schema.primary + row_schema.others:
            if name in names:
                found.append(name)
                continue
            lcname = name.lower()
            elif lcname in casemap:
                found.append(casemap[lcname])
        
        # Construct query to grab as much as we can from our params
        query = [
            "insert into", driver.quote_identifier(self.table),
            "(", ", ".join([ x.lower() for x in found ]), ")",
            "values",
            "(", ", ".join([ ':' + x for x in found ]), ")" 
        ]
        
        # Do the thing
        return cursor.execute(" ".join(query), params)

class PendingUpdate:
    def __init__(self, cursor, table):
        self.cursor = cursor
        self.table = table

    def source(self, obj):
        driver = cursor.connection._driver
        row_schema = driver.row_schema(self.table)
        
        

def _names_from_params(params: Any) -> list[str]:
    if isinstance(params, Mapping):
        return list(params.keys())
    else:
        return list(vars(params).keys())

def _case_map_for_names(names: list[str]) -> Mapping[str, str]:
    ret = { }
    ambiguous = set()
    for name in names:
        lcname = name.lower()
        if name == lcname:
            continue
        if lcname in casemap:
            ambiguous.add(lcname)
        else:
            ret[lcname] = name
    for a in ambiguous:
        del ret[a]
    return ret

def _find_names(names: list[str], casemap: Mapping[str, str]) -> list[str]:
    ret = [ ]
    unfolded = set(names)
    for name in names:
        if name in unfolded:
            ret.append(name)
            continue
        lcname = name.lower()
        elif lcname in casemap:
            ret.append(casemap[lcname])
    return ret
