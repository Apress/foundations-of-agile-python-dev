#legalStuff jr05
# Copyright 2005 John H. Roth Jr.
# Released under the terms of the General Public License (GPL), Release 2.1 or later
# See license.txt for terms and disclaimer of all warrenties and liability.
# Last updated for Release 0.8a1
#endLegalStuff

# fixtures for acceptance tests for various cell handlers.

from fit.ColumnFixture import ColumnFixture
from fit.TypeAdapter import ExceptionCellHandlerParameters

class StringCellHandlers(ColumnFixture):
    _typeDict = {".display": "on",
                 ".markup": "off",
                 "input": "String",
                 "input.addCellHandlers": ["AsisCellHandler"],
                 "input.columnType": "given",
                 "Notes.columnType": "comment",
                 "output": "String",
                 "output.addCellHandlers": ["AsisCellHandler"],
                 "output.columnType": "result",
                 "stringLength": "Integer",
                 "stringLength.columnType": "result",
                 }

    input = ""

    def stringLength(self):
        if self.input is None:
            return -1
        return len(self.input)

    def output(self):
        return self.input

class ParseExceptionCellHandler(ColumnFixture):
    _typeDict = {
        ".display": "on",
        ".markup": "off",
        "contents": ExceptionCellHandlerParameters,
        "contents.columnType": "given",
        "message": "String",
        "message.columnType": "result",
        "messageLength": "Int",
        "messageLength.columnType": "result",
        "Notes.columnType": "comment",
        "type": "String",
        "type.columnType": "result",
        "value": "String",
        "value.columnType": "result",
        "valueLength": "Int",
        "valueLength.columnType": "result",
        }

    contents = None    

    def message(self):
        return self.contents.exceptionMsg

    def messageLength(self):
        return self._getLen(self.contents.exceptionMsg)

    def type(self):
        return self.contents.exceptionType

    def value(self):
        return self.contents.value

    def valueLength(self):
        return self._getLen(self.contents.value)

    def _getLen(self, value):
        if value is None:
            return None
        return len(value)

class RaiseExceptionOnEqualsTypeAdapter(object):
    def __init__(self, value):
        self.value = str(value)

    def __eq__(self, unused='other'):
        __pychecker__ = "no-classattr"
        raise Exception(self._message)
    
    def __str__(self):
        __pychecker__ = "no-classattr"
        return self._value

class RaiseExceptionOnGivenTypeAdapter(object):
    def __init__(self, unused='value'):
        __pychecker__ = "no-classattr"
        raise Exception(self._message)

    def __eq__(self, unused='other'):
        __pychecker__ = "no-classattr"
        raise Exception(self._message)
    
    def __str__(self):
        __pychecker__ = "no-classattr"
        return self._value

class ExceptionCellHandler(ColumnFixture):
    _typeDict = {
        ".markup": "off",
        "check_": RaiseExceptionOnEqualsTypeAdapter,
        "check.columnType": "result",
        "check.renameTo": "check_",
        "get": "String",
        "get.columnType": "result",
        "message": "String",
        "message.columnType": "given",
        "Notes.columnType": "comment",
        "store": RaiseExceptionOnGivenTypeAdapter,
        "store.columnType": "given",
        "type": "String",
        "type.columnType": "given",
        "value": "String",
        "value.columnType": "given",
        }

    def type(self, value):
        self._type = value
        RaiseExceptionOnEqualsTypeAdapter._type = value
        RaiseExceptionOnGivenTypeAdapter._type = value

    def message(self, value):
        self._message = value
        RaiseExceptionOnEqualsTypeAdapter._message = value
        RaiseExceptionOnGivenTypeAdapter._message = value

    def value(self, value):
        self._value = value
        RaiseExceptionOnEqualsTypeAdapter._value = value
        RaiseExceptionOnGivenTypeAdapter._value = value


    def get(self):
        if self._type == "Exception":
            raise Exception(self._message)
        return None

    def check_(self):
        return False # temp
