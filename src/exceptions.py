# Exceptions. We always throw Error or one of its subclasses, and always
# try to wrap other exceptions in one of our own.
# TODO: Remove the note about wrapping (we don't), try and simplify to
# just Error, move Error to __init__ if we can.

class Error(Exception):
    def __init__(self, reason=None):
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

class SqlDriverException(Error):
    """
    Wrap exceptions from the SQL driver in this one.
    """
    def __init__(self, cause, reason=None):
        self.cause = cause
        super().__init__(reason)

    def __repr__(self):
        return super().__repr__() + f" caused by {self.cause!r}"
