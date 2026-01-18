# Abstract base type declarations. This module MUST NOT depend on
# any other abnormal module, to avoid circular import problems.

from abc import ABC, abstractmethod
from collections.abc import Iterator, Sequence
from dataclasses import dataclass
from typing import Any, Callable, Optional, Unpack

type Target = Callable[[Unpack[Any]], Any]

class ConnectionBase(ABC):
    _driver: DriverBase
    _paramstyle: str

    @abstractmethod
    def __init__(self, raw: Any, paramstyle: str, driver: DriverBase) -> None:
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
    def insert_into(self, table: str) -> PendingOperationBase:
        ...

    @abstractmethod
    def update(self, table: str) -> PendingOperationBase:
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
    def insert_into(self, table: str) -> PendingOperationBase:
        ...

    @abstractmethod
    def update(self, table: str) -> PendingOperationBase:
        ...

class DriverBase(ABC):
    @abstractmethod
    def row_schema(self, connection: ConnectionBase, table_name: str) -> RowSchema:
        ...

    @abstractmethod
    def split_table_name(self, unsplit: str) -> tuple[Optional[str], str]:
        ...

    @abstractmethod
    def quote_identifier(self, unquoted: str) -> str:
        ...

@dataclass
class RowSchema:
    primary: tuple[str]
    others: tuple[str]


class PendingOperationBase(ABC):
    @abstractmethod
    def from_source(self, obj: Any) -> Optional[Any]:
        ...

    @abstractmethod
    def including(self, *args: str) -> PendingOperationBase:
        ...

    @abstractmethod
    def excluding(self, *args: str) -> PendingOperationBase:
        ...
