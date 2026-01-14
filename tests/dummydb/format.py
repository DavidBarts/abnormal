from .common import Connection as BaseConnection, Cursor as BaseCursor

apilevel = "1.0"
threadsafety = 0
paramstyle = "format"

class Connection(BaseConnection):
    pass

class Cursor(BaseCursor):
    pass

def connect(*args, **kwargs):
    return Connection()
