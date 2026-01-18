# This is here mainly to enable type declarations in both pending
# and __init__ without causing circular imports.

from abc import ABC, abstractmethod
from collections.abc import Iterator, Sequence
from typing import Any, Callable, Optional, Unpack

from .driver import Driver
from .pending import InsertOperation, UpdateOperation

type Target = Callable[[Unpack[Any]], Any]

class ConnectionBase(ABC):
    _driver: Driver
    _paramstyle: str

    @abstractmethod
    def __init__(self, raw: Any, paramstyle: str, driver: Driver) -> None:
        ...

    @abstractmethod
    def close(self) -> None:
        ...

    @abstractmethod
    def commit(self) -> None:
        ...

    @abstractmethod
    def rollback(self) -> None:
        ...

    @abstractmethod
    def cursor(self) -> CursorBase:
        ...

    @abstractmethod
    def execute(self, query: str, params: Any = {}) -> CursorBase:
        ...

    @abstractmethod
    def executemany(self, query: str, seq: Sequence) -> None:
        ...

    @abstractmethod
    def insert_into(self, table: str) -> InsertOperation:
        ...

    @abstractmethod
    def update(self, table: str) -> UpdateOperation:
        ...

class CursorBase(ABC):
    connection: ConnectionBase

    @abstractmethod
    def __init__(self, raw: Any, connection: ConnectionBase) -> None:
        ...

    @property
    @abstractmethod
    def arraysize(self) -> int:
        ...

    # Ugh. There is no way to define a sequence of a specific length w/ MyPy
    # types. There is a way for tuples, but PEP249 only specifies "a sequence
    # of 7-item sequences" here. So we just use Sequence[Any].
    @property
    @abstractmethod
    def description(self) -> Sequence[Sequence[Any]]:
        ...

    @property
    @abstractmethod
    def rowcount(self) -> int:
        ...

    @abstractmethod
    def callproc(self, procname: str, params: Optional[Sequence[Any]] = None) -> Sequence[Any]:
        ...

    @abstractmethod
    def close(self) -> None:
        ...

    @abstractmethod
    def __del__(self) -> None:
        ...

    @abstractmethod
    def execute(self, operation: str, params: Any = {}) -> CursorBase:
        ...

    @abstractmethod
    def executemany(self, operation: str, seq: Sequence[Any]) -> None:
        ...

    @abstractmethod
    def fetchone(self) -> Optional[Sequence[Any]]:
        ...

    @abstractmethod
    def fetchmany(self, size: Optional[int] = None) -> Sequence[Sequence[Any]] | Sequence[None]:
        ...

    @abstractmethod
    def fetchall(self) -> Sequence[Sequence[Any]]:
        ...

    @abstractmethod
    def nextset(self) -> Optional[bool]:
        ...

    @abstractmethod
    def setinputsizes(self, sizes: Sequence[int | type]) -> None:
        ...

    @abstractmethod
    def setoutputsize(self, size: int, column: Optional[int] = None) -> None:
        ...

    @abstractmethod
    def into(self, target: Target) -> Iterator[Any]:
        ...

    @abstractmethod
    def into1(self, target: Target) -> Any:
        ...

    @abstractmethod
    def insert_into(self, table: str) -> InsertOperation:
        ...

    @abstractmethod
    def update(self, table: str) -> UpdateOperation:
        ...
