# Exceptions. We always throw Error or one of its subclasses, and always
# try to wrap other exceptions in one of our own.

class Error(Exception):
    def __init__(self, reason=None, cause=None):
        self.reason = reason
        if reason is None and cause is not None and hasattr(cause, "reason"):
            self.reason = cause.reason
        self.cause = cause
        super().__init__()

    def __str__(self):
        return self._getname() if self.reason is None else self.reason

    def __repr__(self):
        if self.cause is None:
            caused_by = ""
        else:
            caused_by = " (caused by " + self._getname(cause) + ")"
        if self.reason is None:
            return self._getname() + ": " + self.reason + caused_by
        else:
            return self._getname() + caused_by

    def _getname(self, other=None):
        klass = self.__class__ if other is None else other.__class__
        return klass.__module__ + "." + klass.__qualname__

class DataError(Error):
    """
    Currently, we throw this when we expect a single result and either get
    multiple results, or nothing at all.
    """
    pass

class InterfaceError(Error):
    """
    We throw this for our own internal errors.
    """
    pass

class ProgrammingError(Error):
    """
    Currently, we throw this one when we detect an SQL syntax error.
    """
    pass
