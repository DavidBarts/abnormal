# This contains the objects PEP 249 specifies. It does not contain the
# module globals. The individual types (one per paramstyle) do that.
# All share these objects.

from collections.abc import Sequence, Mapping
from dataclasses import dataclass, field
from typing import Any, Optional

from abnormal.base import ConnectionBase, CursorBase

class Warning(Exception):
    pass

class Error(Exception):
    pass

class InterfaceError(Error):
    pass

class DatabaseError(Error):
    pass

class DataError(DatabaseError):
    pass

class OperationalError(DatabaseError):
    pass

class IntegrityError(DatabaseError):
    pass

class InternalError(DatabaseError):
    pass

class ProgrammingError(DatabaseError):
    pass

class NotSupportedError(DatabaseError):
    pass

class Connection(ConnectionBase):
    def close(self) -> None:
        _log_use("connection close")

    def commit(self) -> None:
        _log_use("connection commit")

    def rollback(self) -> None:
        _log_use("connection rollback")

    def cursor(self) -> CursorBase:
        _log_use("connection cursor")
        return Cursor()

class Cursor(CursorBase):
    def __init__(self):
        _log_use("cursor __init__")
        self.rowcount = -1
        self.arraysize = 1

    @property
    def description(self) -> -> Sequence[Sequence[str, type, Optional[int], Optional[int], Optional[int], Optional[bool]]]:
        return RESULTS.description.pop()

    def callproc(self, procname: str, parameters: Sequence) -> Sequence:
        _log_use("cursor callproc", **locals())
        return RESULTS.callproc.pop()

    def close(self) -> None:
        _log_use("cursor close")

    def execute(self, operation: str, parameters: Sequence | Mapping | None = None) -> Optional[Any]:
        _log_use("cursor execute", **locals())
        return RESULTS.execute.pop()

    def executemany(self, operation: str, seq_of_parameters: Sequence[Sequence] | Sequence[Mapping]) -> Optional[Any]:
        _log_use("cursor executemany", **locals())
        return RESULTS.executemany.pop()

    def fetchone(self) -> Optional[Sequence]:
        _log_use("cursor fetchone")
        return RESULTS.fetchone.pop()

    def fetchmany(self, size: int = -1) -> Sequence[Sequence] | Sequence:
        if size < 0:
            size = self.arraysize
        _log_use("cursor fetchmany", **locals())
        return RESULTS.fetchmany.pop()

    def fetchall(self) -> Sequence[Sequence] | Sequence:
        _log_use("cursor fetchall")
        return RESULTS.fetchall.pop()

    def nextset(self) -> Optional[bool]:
        _log_use("cursor nextset")
        return RESULTS.nextset.pop()

    def setinputsizes(self, sizes: int) -> None:
        _log_use("cursor setinputsizes", **locals())

    def setoutputsize(self, size:int, column: Optional[str] = None) -> None:
        _log_use("cursor setoutputsize", **locals())

# Mocking of the input and outputs is shamelessly unithreaded. Due to how
# cursors are the store of thread-private data, and how they are created
# one-off all over the place, doing it any other way would be painful.

@dataclass
class CursorResults:
    callproc: list[Optional[Any]] = field(default_factory=list)
    execute: list[Optional[Any]] = field(default_factory=list)
    executemany: list[Optional[Any]] = field(default_factory=list)
    fetchone: list[Optional[Sequence]] = field(default_factory=list)
    fetchmany: list[Sequence[Sequence] | Sequence] = field(default_factory=list)
    fetchall: list[Sequence[Sequence] | Sequence] = field(default_factory=list)
    nextset: list[Optional[bool]] = field(default_factory=list)
    description: list[Sequence[tuple[str, type, None, None, None, None, None]]] = field(default_factory=list)

    def clear(self):
        self.callproc.clear()
        self.execute.clear()
        self.executemany.clear()
        self.fetchone.clear()
        self.fetchmany.clear()
        self.fetchall.clear()
        self.nextset.clear()
        self.description.clear()

RESULTS = CursorResults()

@dataclass
class Message:
    source: str
    details: dict[Any]

MESSAGE: list[Message] = []

def _log_use(what, **kwargs):
    print_args = [ "DUMMY:", what ]
    for k, v in kwargs.items():
        print_args.append(", " + k + " =")
        print_args.append(repr(v))
    print(*print_args)
    MESSAGE.append(Message(source=what, details=kwargs))