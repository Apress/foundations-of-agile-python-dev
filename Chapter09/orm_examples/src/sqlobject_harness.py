import os
import random

from decorator import decorator
from pymock import dummy, override, replay, use_pymock, verify
from sqlobject import ForeignKey, MultipleJoin, RelatedJoin, SQLObject, StringCol
import sqlobject

def sqlite_connect(abs_path):
    connection_uri = 'sqlite://' + abs_path
    connection = sqlobject.connectionForURI(connection_uri)
    sqlobject.sqlhub.processConnection = connection

@use_pymock
def _sqlite_connect():
    f = '/x'
    uri = 'sqlite:///x'
    connection = dummy()
    override(sqlobject, 'connectionForURI').expects(uri).\
    returns(connection)
    replay()
    sqlite_connect(f)
    assert sqlobject.sqlhub.processConnection is connection
    verify()
    
def random_string(length):
    seq = [chr(x) for x in range(ord('a'), ord('z')+1)]
    return ''.join([x for x in random.sample(seq, length)])

def with_sqlobject_and_schema(schema_func, tst):
    f = os.path.abspath(random_string(8) + '.db')
    sqlite_connect(f)
    try:
        schema_func()
        tst()
    finally:
        sqlobject.sqlhub.processConnection.cache.clear()
        sqlobject.sqlhub.processConnection.close()
        del sqlobject.sqlhub.processConnection
        if os.path.exists(f):
            os.unlink(f)

