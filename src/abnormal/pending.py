# Insert (insert_into) and update operations support.
# XXX - we don't use type declarations here in constructors (and possibly
# strategically elsewhere) because using them raises circular import
# issues.

from abc import ABC, abstractmethod
from collections.abc import Mapping, Sequence
from typing import Any, Optional

from .driver import driver_for
from .todb import convert

class _PendingOperation(ABC):
    def __init__(self, cursor: Any, table: str, mandatory_pk: bool):
        self.cursor = cursor
        self.table = table
        self.mandatory_pk = mandatory_pk
        self._inc = set()
        self._exc = set()
        self._init_names(obj)
        self._init_casemap()
        self._init_row_schema()
        self._map_columns()

    @abstractmethod
    def from_source(self, obj: Any) -> Optional[Any]:
        ...

    def _init_names(self, obj: Any) -> None:
        if isinstance(obj, Mapping):
            self._names = tuple(obj.keys())
        else:
            self._names = tuple(vars(obj).keys())

    def _init_casemap(self) -> None:
        self._casemap = {}
        ambiguous = set()
        for name in self._names:
            lcname = name.lower()
            if name == lcname:
                continue
            if lcname in self._casemap:
                ambiguous.add(lcname)
            else:
                self._casemap[lcname] = name
        for a in ambiguous:
            del self._casemap[a]

    def _init_row_schema(self) -> None:
        self._row_schema = self.cursor.driver.row_schema(self.table)

    def _map_columns(self) -> None:
        self._pk_columns = self._domap(self._row_schema.primary, self.mandatory_pk)
        self._columns = self._domap(self._row_schema.others, False)

    def _domap(self, columns: list[str], mandatory: bool) -> list[str]:
        ret = []
        for column in columns:
            result = self.find(column)
            if result is None:
                if mandatory:
                    raise IncompleteDataError(f"Primary key column {pkc!r} missing from data source.")
                else:
                    continue
            ret.append(column)
        return ret

    def _find(self, unmapped: str) -> Optional[str]:
        name = self._dofind(unmapped)
        if name is not None:
            return unmapped
        if unmapped in self._casemap:
            return self._dofind(self._casemap[unmapped.lower()])
        return None

    def _dofind(self, name: str) -> Optional[str]:
        if isinstance(self.obj, Mapping) and name in self.obj:
            return name
        if hasattr(self.obj, name):
            return name
        return None

    def including(self, *args: str) -> _PendingOperation:
        temp = set(args)
        if self.mandatory_pk:
            for pk_column in self._pk_columns:
                if pk_column not in temp:
                    raise ValueError("Must include primary key column {pk_column!r}.")
        self._inc = temp
        if self._exc:
            self._exc = set()
        return self

    def excluding(self, *args: str) -> _PendingOperation:
        temp = set(args)
        if self.mandatory_pk:
            for pk_column in self._pk_columns:
                if pk_column in temp:
                    raise ValueError("Cannot exclude primary key column {pk_column!r}.")
        if self._inc:
            self._inc = set()
        self._exc = temp
        return self

    def _filter(self, unfiltered: Sequence[str]):
        if self.inc:
            return [ x for x in unfiltered if x in self.inc ]
        elif self.exc:
            return [ x for x in unfiltered if x not in self.exc ]
        else:
            return unfiltered

# It is not mandatory to fully specify (or even specify at all) the primary
# key when inserting, because database tables commonly have rules for
# defaulting it.
class InsertOperation(_PendingOperation):
    def __init__(self, cursor, table):
        super().__init__(cursor, table, False)

    def from_source(self, obj: Any) -> Optional[Any]:
        cols = self._filter(self._pk_columns + self._columns)
        query = [
            "insert into", self.cursor.driver.quote_identifier(self.table),
            "(", ", ".join([ driver.quote_identifier(x) for x in cols ]), ")",
            "values",
            "(", ", ".join([ ':' + self.find(x) for x in cols ]), ")"
        ]

        return self.cursor.execute(" ".join(query), params)

# It is mandatory to fully specify the primary key when updating, to avoid
# accidentally overwriting a lot of data. (Those who really do want to
# do an update can always do it manually.)
class UpdateOperation(_PendingOperation):
    def __init__(self, cursor, table):
        super().__init__(cursor, table, True)

    def from_source(self, obj: Any) -> Optional[Any]:
        query = [ "update ", self.cursor.driver.quote_identifier(self.table), " set" ]

        needs_comma = False
        for col in self._filter(self._columns):
            if needs_comma:
                query.append(", ")
            else:
                query.append(" ")
                needs_comma = True
            query.append(self.cursor.driver.quote_identifier(col))
            query.append(" = :")
            query.append(self.find(col))

        query.append(" where")
        needs_and = False
        for col in self._filter(self._pk_columns):
            if needs_and:
                query.append(" and ")
            else:
                query.append(" ")
                needs_comma = True
            query.append(self.cursor.driver.quote_identifier(col))
            query.append(" = :")
            query.append(self.find(col))

        return self.cursor.execute("".join(query), vals)
