# The publicly-usable stuff goes here.

# I m p o r t s

from .exceptions import Error
from .todb import convert

# C l a s s e s

class Connection:
    def __init__(self, raw, paramstyle):
        self.raw = raw
        self.paramstyle = paramstyle

    def close(self):
        self.raw.close()

    def commit(self):
        self.raw.commit()

    def rollback(self):
        self.raw.rollback()

    def cursor(self):
        return Cursor(self.raw.cursor(), self)

    def execute(self, query, params={}):
        return self.cursor().execute(query, params)

class Cursor:
    def __init__(self, raw, parent):
        self.raw = raw
        self.parent = parent
        self._colnames = None

    def callproc(self, procname, params):
        return self.raw.callproc(procname, params)

    def close(self):
        self.raw.close()

    def execute(self, operation, params={}):
        self.raw.execute(*convert(operation, params, self.parent.paramstyle))
        self._colnames = [ x[0].lower() for x in self.raw.description ]
        return self

    # executemany not supported (for now)

    def into(self, target):
        while True:
            value = self._into(target)
            if value is None:
                break
            yield value

    def into1(self, target):
        ret = self._into(target)
        # XXX - some interfaces always return -1 for rowcount
        if abs(self.raw.rowcount) != 1:
            raise Error(f"unexpected row count of {self.raw.rowcount}")
        if ret is None:
            raise Error("unexpected lack of results")
        return ret

    def _into(self, target):
        row = self.raw.fetchone()
        if row is None:
            return None
        kwargs = {}
        col = 0
        for colname in self._colnames:
            kwargs[colname] = row[col]
            col += 1
        return target(**kwargs)

# F u n c t i o n s

def connect(mod, *args, **kwargs):
    """Given a PEP 249 compliant database module and connection parameters,
       return am abnormal Connection object."""
    return Connection(mod.connect(*args, **kwargs), mod.paramstyle)

def mapping(**kwargs):
    "For returning a mapping with .into()"
    return kwargs
