# The publicly-usable stuff goes here.

# I m p o r t s

from .exceptions import Error, UnexpectedResultError
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
        if self.raw.description is None:
            self._colnames = []
        else:
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
            raise UnexpectedResultError(f"unexpected row count of {self.raw.rowcount}")
        if ret is None:
            raise UnexpectedResultError("unexpected lack of results")
        return ret

    def _into(self, target):
        row = self.raw.fetchone()
        # XXX - this test is ugly, but it is the easiest way to make something
        # be concise on the user end.
        if target == sequence:
            return row
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

def scalar(**kwargs):
    "For returning a 1-column row as a scalar with .into()"
    ncols = len(kwargs)
    if ncols == 1:
        for entry in kwargs.values():
            return entry
    else:
        raise UnexpectedResultError(f"unexpected column count of {ncols}")

def sequence(**kwargs):
    "For returning a row as a sequence."
    # This should never be called directly; it is merely detected.
    raise NotImplementedError("sequence should never be called directly")
