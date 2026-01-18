# The publicly-usable stuff goes here.

# I m p o r t s

from collections.abc import Iterator as _Iterator, Mapping as _Mapping, Sequence as _Sequence
from typing import Any as _Any, Callable as _Callable, Optional as _Optional, Unpack as _Unpack
from types import ModuleType as _ModuleType

from .base import ConnectionBase as _ConnectionBase, CursorBase as _CursorBase, Target as _Target, PendingOperationBase as _PendingOperationBase
from .driver import driver_for as _driver_for, Driver
from .exceptions import Error, UnexpectedResultError, SqlError, IncompleteDataError
from .misc import Namespace
from .pending import InsertOperation, UpdateOperation
from .todb import QueryConverter as _QueryConverter

# V a r i a b l e s

# PEP 249 support. We ARE NOT fully PEP 249 compliant (and we probably
# never will be). There are good reasons for that. Just for openers,
# module globals like apilevel and threadsafety depend on the module
# we wrap, and therefore there cannot be globally-correct values for
# them. Also note that threadsafety below is OUR threadsafety level
# ONLY. The overall threadsafety level is the lesser of this and that
# of the wrapped connector.
apilevel = "2.0"
threadsafety = 2
paramstyle = "named"

# C l a s s e s

class Connection(_ConnectionBase):
    def __init__(self, raw: _Any, paramstyle: str, driver: Driver) -> None:
        for name in ['close', 'commit', 'rollback', 'cursor']:
            if not callable(getattr(raw, name, None)):
                raise TypeError("Passed object is not a connection.")
        self.raw = raw
        self._paramstyle = paramstyle
        self._driver = driver

    def close(self) -> None:
        self.raw.close()

    def commit(self) -> None:
        self.raw.commit()

    def rollback(self) -> None:
        self.raw.rollback()

    def cursor(self) -> _CursorBase:
        return Cursor(self.raw.cursor(), self)

    def execute(self, query: str, params: _Any = {}) -> _CursorBase:
        return self.cursor().execute(query, params)

    def executemany(self, query: str, seq: _Sequence) -> None:
        cursor = self.cursor()
        cursor.executemany(query, seq)

    def insert_into(self, table: str) -> _PendingOperationBase:
        return self.cursor().insert_into(table)

    def update(self, table: str) -> _PendingOperationBase:
        return self.cursor().update(table)

class Cursor(_CursorBase):
    def __init__(self, raw, connection) -> None:
        self.raw = raw
        self.connection = connection
        self._colnames: _Optional[_Sequence[str]] = None
        self._converter = _QueryConverter()

    @property
    def arraysize(self) -> int:
        return self.raw.arraysize

    @property
    def description(self) -> _Sequence[_Sequence[_Any]]:
        return self.raw.description

    @property
    def rowcount(self) -> int:
        return self.raw.rowcount

    def callproc(self, procname: str, params: _Optional[_Sequence[_Any]] = None) -> _Sequence[_Any]:
        if params is None:
            return self.raw.callproc(procname)
        else:
            return self.raw.callproc(procname, params)

    def close(self) -> None:
        self.raw.close()

    def __del__(self) -> None:
        if hasattr(self.raw, '__del__'):
            self.raw.__del__()

    def execute(self, operation: str, params={}) -> _CursorBase:
        self.raw.execute(*self._converter.convert(operation, params, self.connection._paramstyle))
        descr = self.raw.description
        if descr is None:
            self._colnames = []
        else:
            self._colnames = [ x[0].lower() for x in descr ]
        return self

    def executemany(self, operation: str, seq: _Sequence[_Any]) -> None:
        # TODO: see if we can make this sequence evaluation lazy (should we?)
        rseq = [ self._converter.convert(operation, params, self.connection._paramstyle) for params in seq ]
        if rseq:
            self.raw.executemany(rseq[0][0], [ x[1] for x in rseq ])
        self._colnames = []  # results not allowed here

    def fetchone(self) -> _Optional[_Sequence[_Any]]:
        return self.raw.fetchone()

    def fetchmany(self, size: _Optional[int] = None) -> _Sequence[_Sequence[_Any]] | _Sequence[None]:
        if size is None:
            size = self.arraysize
        return self.raw.fetchmany(size)

    def fetchall(self) -> _Sequence[_Sequence[_Any]]:
        return self.raw.fetchall()

    def nextset(self) -> _Optional[bool]:
        return self.raw.nextset()

    def setinputsizes(self, sizes: _Sequence[int | type]) -> None:
        self.raw.setinputsizes(sizes)

    def setoutputsize(self, size: int, column: _Optional[int] = None) -> None:
        if column is None:
            self.raw.setoutputsize(size)
        else:
            self.raw.setoutputsize(size, column)

    def into(self, target: _Target) -> _Iterator[_Any]:
        while True:
            value = self._into(target)
            if value is None:
                break
            yield value

    def into1(self, target: _Target) -> _Any:
        ret = self._into(target)
        # XXX - some interfaces always return -1 for rowcount
        if abs(self.raw.rowcount) != 1:
            raise UnexpectedResultError(f"unexpected row count of {self.raw.rowcount}")
        if ret is None:
            raise UnexpectedResultError("unexpected lack of results")
        return ret

    def _into(self, target: _Target) -> _Optional[_Any]:
        row = self.raw.fetchone()
        # XXX - this test is ugly, but it is the easiest way to make something
        # be concise on the user end.
        if target == sequence:
            return row
        if row is None:
            return None
        kwargs = {}
        col = 0
        assert self._colnames is not None
        for colname in self._colnames:
            kwargs[colname] = row[col]
            col += 1
        return target(**kwargs)

    def insert_into(self, table: str) -> InsertOperation:
        return InsertOperation(self, table)

    def update(self, table: str) -> UpdateOperation:
        return UpdateOperation(self, table)

# F u n c t i o n s

def connect(mod: _ModuleType, *args, **kwargs) -> _ConnectionBase:
    """Given a PEP 249 compliant database module and connection parameters,
       return am abnormal Connection object."""
    return Connection(mod.connect(*args, **kwargs), mod.paramstyle, _driver_for(mod))

def mapping(**kwargs) -> _Mapping[str, _Any]:
    "For returning a mapping with .into()"
    return kwargs

def scalar(**kwargs) -> _Any:
    "For returning a 1-column row as a scalar."
    ncols = len(kwargs)
    if ncols == 1:
        return next(iter(kwargs.values()))
    else:
        raise UnexpectedResultError(f"unexpected column count of {ncols}")

def sequence(**kwargs) -> _Sequence[_Any]:
    "For returning a row as a sequence."
    # This should never be called directly; it is merely detected.
    raise NotImplementedError("sequence should never be called directly")

def namespace(**kwargs) -> Namespace:
    "For returning a namespace."
    return Namespace(kwargs)
