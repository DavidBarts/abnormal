# Insert (insert_into) and update operations support.
# XXX - we don't use type declarations here in constructors (and possibly
# strategically elsewhere) because using them raises circular import
# issues.

from abc import ABC, abstractmethod
from collections.abc import Mapping, Sequence
from typing import Any, Optional

from .exceptions import IncompleteDataError, InvalidStateError

class _PendingOperation(ABC):
    def __init__(self, cursor: Any, table: str, mandatory_pk: bool):
        self.cursor = cursor
        self.table = table
        self.mandatory_pk = mandatory_pk
        self._inc: set[str] = set()
        self._exc: set[str] = set()
        self._row_schema = None

    @abstractmethod
    def from_source(self, obj: Any) -> Optional[Any]:
        ...

    def _from_source(self, obj: Any) -> None:
        self._set_data_object(obj)
        self._check_inc_exc()

    def _set_data_object(self, obj: Any) -> None:
        self._obj = obj
        self._init_names(obj)
        self._init_casemap()
        self._init_row_schema()
        self._map_columns()

    def _check_inc_exc(self) -> None:
        if not self.mandatory_pk:
            return  # we don't care if PK's are missing
        for pk_column in self._pk_columns:
            if self._inc and pk_column not in self._inc:
                raise IncompleteDataError("Must include primary key column {pk_column!r}.")
            if self._exc and pk_column in self._exc:
                raise IncompleteDataError("Must not exclude primary key column {pk_column!r}.")



    def _init_names(self, obj: Any) -> None:
        if isinstance(obj, Mapping):
            self._names = tuple(obj.keys())
        else:
            self._names = tuple(vars(obj).keys())

    def _init_casemap(self) -> None:
        self._casemap: dict[str, str] = {}
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
        if self._row_schema is None:
            self._row_schema = self.cursor.connection._driver.row_schema(self.cursor.connection, self.table)

    def _map_columns(self) -> None:
        self._pk_columns = self._domap(self._row_schema.primary, self.mandatory_pk)
        self._columns = self._domap(self._row_schema.others, False)

    def _domap(self, columns: list[str], mandatory: bool) -> list[str]:
        ret = []
        for column in columns:
            result = self._find(column)
            if result is None:
                if mandatory:
                    raise IncompleteDataError(f"Primary key column {column!r} missing from data source.")
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
        if isinstance(self._obj, Mapping) and name in self._obj:
            return name
        if hasattr(self._obj, name):
            return name
        return None

    def including(self, *args: str) -> _PendingOperation:
        if self._exc:
            raise InvalidStateError("May not use .including when excluding.")
        self._inc = set(args)
        return self

    def excluding(self, *args: str) -> _PendingOperation:
        if self._inc:
            raise InvalidStateError("May not use .excluding when including.")
        self._exc = set(args)
        return self

    def _filter(self, unfiltered: Sequence[str]):
        if self._inc:
            return [ x for x in unfiltered if x in self._inc ]
        elif self._exc:
            return [ x for x in unfiltered if x not in self._exc ]
        else:
            return unfiltered

    def _mustfind(self, unmapped: str) -> str:
        ret = self._find(unmapped)
        assert ret is not None
        return ret

# It is not mandatory to fully specify (or even specify at all) the primary
# key when inserting, because database tables commonly have rules for
# defaulting it.
class InsertOperation(_PendingOperation):
    def __init__(self, cursor, table):
        super().__init__(cursor, table, False)

    def from_source(self, obj: Any) -> Optional[Any]:
        self._from_source(obj)
        cols = self._filter(self._pk_columns + self._columns)
        query = [
            "insert into", self.cursor.connection._driver.quote_identifier(self.table),
            "(", ", ".join([ self.cursor.connection._driver.quote_identifier(x) for x in cols ]), ")",
            "values",
            "(", ", ".join([ ':' + self._mustfind(x) for x in cols ]), ")"
        ]

        return self.cursor.execute(" ".join(query), self._obj)

# It is mandatory to fully specify the primary key when updating, to avoid
# accidentally overwriting a lot of data. (Those who really do want to
# do an update can always do it manually.)
class UpdateOperation(_PendingOperation):
    def __init__(self, cursor, table):
        super().__init__(cursor, table, True)

    def from_source(self, obj: Any) -> Optional[Any]:
        self._from_source(obj)
        query = [ "update ", self.cursor.connection._driver.quote_identifier(self.table), " set" ]

        needs_comma = False
        for col in self._filter(self._columns):
            if needs_comma:
                query.append(", ")
            else:
                query.append(" ")
                needs_comma = True
            query.append(self.cursor.connection._driver.quote_identifier(col))
            query.append(" = :")
            query.append(self._mustfind(col))

        query.append(" where")
        needs_and = False
        for col in self._filter(self._pk_columns):
            if needs_and:
                query.append(" and ")
            else:
                query.append(" ")
                needs_comma = True
            query.append(self.cursor.connection._driver.quote_identifier(col))
            query.append(" = :")
            query.append(self._mustfind(col))

        return self.cursor.execute("".join(query), self._obj)
