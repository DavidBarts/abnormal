# Exceptions. We always throw Error or one of its subclasses, and always
# try to wrap other exceptions in one of our own.

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

class UnexpectedResultError(Error):
    """
    When we expect a single result and either get multiple results,
    or nothing at all.
    """
    # XXX - note that due to the limitations of some PEP 249 database
    # interfaces, unexpected multiple results are not always reliably
    # detected.
    def __init__(self, cause, reason=None):
        self.cause = cause
        super().__init__(reason)

    def __repr__(self):
        return super().__repr__() + f" caused by {self.cause!r}"
