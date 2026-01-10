# Exceptions. We always throw Error or one of its subclasses, and always
# try to wrap other exceptions in one of our own.

class Error(Exception):
    def __init__(self, reason: str = None):
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
