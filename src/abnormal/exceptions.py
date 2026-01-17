# Exceptions. We always throw Error or one of its subclasses, and always
# try to wrap other exceptions in one of our own.

from typing import Optional

class Error(Exception):
    def __init__(self, reason: Optional[str] = None):
        self.reason = reason
        super().__init__()

    def __str__(self):
        return self._getname() if self.reason is None else self.reason

    def __repr__(self):
        if self.reason is None:
            return self._getname() + ": " + self.reason
        else:
            return self._getname()

    def _getname(self):
        klass = self.__class__
        return klass.__module__ + "." + klass.__qualname__

class UnexpectedResultError(Error):
    """
    When we expect a single result and either get multiple results,
    or nothing at all.
    """
    pass

class SqlError(Error):
    """
    When we can't make sense of the SQL that has been fed to us.
    """
    pass

class IncompleteDataError(Error):
    """
    When an .insert_into or .update is fed inufficient data, i.e. data
    with a missing or incomplete primary key.
    """

class InterfaceError(Error):
    """
    Something went wrong attempting to interface with the database.
    Currently used to report a failure to determine primary key columns
    in a table.
    """

class InvalidStateError(Error):
    """
    When the user attempts to do something for which the state of an
    object is not valid. Currently used to report an attempt to use the
    mutually-exclusive .including and .excluding modifiers to a
    PendingOperation.
    """
