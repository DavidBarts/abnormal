# The publicly-usable stuff goes here.

# I m p o r t s

from .driver import driver_for as _driver_for
from .exceptions import Error, DataError, InterfaceError, ProgrammingError
from .misc import Namespace
from .todb import convert as _convert

# V a r i a b l e s

# PEP 249 support. We ARE NOT fully PEP 249 compliant! TODO: Hopefully some
# day.
apilevel = "2.0"
threadsafety = 0  # TODO: ensure thread safety
paramstyle = "named"

# C l a s s e s

class Connection:
    def __init__(self, raw, paramstyle, driver):
        self.raw = raw
        self._paramstyle = paramstyle
        self._driver = driver

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

    def executemany(self, query, seq):
        cursor = self.cursor()
        cursor.executemany(query, seq)
        return cursor

class Cursor:
    def __init__(self, raw, connection):
        self.raw = raw
        self.connection = connection
        self._colnames = None

    @property
    def arraysize(self):
        return self.raw.arraysize

    @property
    def description(self):
        return self.raw.description

    @property
    def rowcount(self):
        return self.raw.rowcount

    def callproc(self, procname, params=None):
        if params is None:
            return self.raw.callproc(procname)
        else:
            return self.raw.callproc(procname, params)

    def close(self):
        self.raw.close()

    def __del__(self):
        self.raw.__del__()

    def execute(self, operation, params={}):
        self.raw.execute(*_convert(operation, params, self.connection._paramstyle))
        if self.raw.description is None:
            self._colnames = []
        else:
            self._colnames = [ x[0].lower() for x in self.raw.description ]
        return self

    def executemany(self, operation, seq):
        # TODO: see if we can make this sequence evaluation lazy (should we?)
        rseq = [ _convert(operation, params, self.connection.paramstyle) for params in seq ]
        if rseq:
            self.raw.executemany(rseq[0][0], [ x[1] for x in rseq ])
        self._colnames = []  # results not allowed here

    def fetchone(self):
        return self.raw.fetchone()

    def fetchmany(self, size=self.arraysize):
        return self.raw.fetchmany(size)

    def fetchall(self):
        return self.raw.fetchall()

    def nextset(self):
        return self.raw.nextset()

    def setinputsizes(self, sizes):
        return self.raw.setinputsizes(sizes)

    def setoutputsize(self, column=None):
        if column is None:
            return self.raw.setoutputsize()
        else:
            return self.raw.setoutputsize(column)

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
            raise DataError(reason=f"unexpected row count of {self.raw.rowcount}")
        if ret is None:
            raise DataError(reason="unexpected lack of results")
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
    return Connection(mod.connect(*args, **kwargs), mod.paramstyle, _driver_for(mod))

def mapping(**kwargs):
    "For returning a mapping with .into()"
    return kwargs

def scalar(**kwargs):
    "For returning a 1-column row as a scalar."
    ncols = len(kwargs)
    if ncols == 1:
        return next(iter(kwargs.values()))
    else:
        raise DataError(reason=f"unexpected column count of {ncols}")

def sequence(**kwargs):
    "For returning a row as a sequence."
    # This should never be called directly; it is merely detected.
    raise NotImplementedError("sequence should never be called directly")

def namespace(**kwargs):
    "For returning a namespace."
    return Namespace(kwargs)
