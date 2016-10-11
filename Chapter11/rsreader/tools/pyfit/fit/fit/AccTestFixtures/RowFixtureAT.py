# Row Fixture Acceptance Test support module
# Copyright 2005, John H. Roth Jr.
# Released under the terms of the GNU General Public License, version 2.0 or later

from fit.Fixture import Fixture
from fit.RowFixture import RowFixture
from fit.Utilities import em

class Object1(object):
    pass

class Object2(object):
    pass

class ClassObjHandler(object):
    def __init__(self, objType):
        self.errCode = None
        self.errMsg = ""
        if objType == "object1":
            self.obj = Object1()
        elif objType == "object2":
            self.obj = Object2()
        else:
            self.obj = Object1()
            self.errCode = 1
            self.errMsg = "Not an existing object"

    def addAttribute(self, key, value):
        setattr(self.obj, key, value)

class DictObjHandler(ClassObjHandler):
    def __init__(self):
        self.errCode = None
        self.errMsg = ""
        self.obj = {}

    def addAttribute(self, key, value):
        self.obj[key] = value

class CollectionReturnValue(object):
    def __init__(self, collection, metaData):
        self.collection = collection
        self.metaData = metaData

class ListCollectionHandler(object):
    def __init__(self):
        self.collection = []
        self.metaData = {}

    def _newObject(self, objType, unused='key'):
        if objType == "dict":
            self.objHandler = DictObjHandler()
        else:
            self.objHandler = ClassObjHandler(objType)
        return (self.objHandler.obj,
                self.objHandler.errCode,
                self.objHandler.errMsg)

    def newObject(self, objType, key):
        obj, errCode, errMsg = self._newObject(objType, key)
        self.collection.append(obj)
        return errCode, errMsg

    def addAttribute(self, key, value):
        self.objHandler.addAttribute(key, value)
        self.metaData[key] = "String"

    def removeMetaData(self, key):
        if self.metaData.has_key(key):
            del self.metaData[key]
            return None, ""
        else:
            return 1, "Key does not exist"

    def _getCollection(self):
        return self.collection

    def getCollection(self):
        return CollectionReturnValue(self._getCollection(), self.metaData)

class TupleCollectionHandler(ListCollectionHandler):
    def _getCollection(self):
        return tuple(self.collection)

class DictCollectionHandler(ListCollectionHandler):
    def __init__(self):
        self.collection = {}
        self.metaData = {}

    def newObject(self, objType, key):
        obj, errCode, errMsg = self._newObject(objType, key)
        self.collection[key] = obj
        return errCode, errMsg

class ListBuilder(Fixture):
    def __init__(self):
        super(ListBuilder, self).__init__()
        self.cells = [None] * 3
        
    def doRows(self, rows):
        while rows:
            self.doRow(rows)
            rows = rows.more

    def doRow(self, row):
        self.oper, self.cells[0], next = self._extract(row.parts)
        self.op1, self.cells[1], next = self._extract(next)
        self.op2, self.cells[2], next = self._extract(next)
        # operation
        if self.oper == "new collection":
            errCode, errMsg = self.newCollection()
            self.annotateResult(errCode, errMsg)
        elif self.oper == "new object":
            errCode, errMsg = self.collectionHandler.newObject(self.op1, self.op2)
            self.annotateResult(errCode, errMsg)
        elif self.oper == "attribute":
            self.collectionHandler.addAttribute(self.op1, self.op2)
            self.annotateResult(None, "")
        elif self.oper == "set symbol":
            self.setSymbol(self.op1 or "theList",
                           self.collectionHandler.getCollection())
            self.annotateResult(None, "")
        elif self.oper == "remove metadata":
            self.collectionHandler.removeMetaData(self.op1)
            self.annotateResult(None, "")
        else:
            self.annotateResult(0, "unknown operation")

    def annotateResult(self, errCode, errMsg):
        if errCode is None:
            self.right(self.cells[0])
        else:
            self.wrong(self.cells[errCode], errMsg)

    def newCollection(self):
        if self.op1 == "list":
            self.collectionHandler = ListCollectionHandler()
        elif self.op1 == "tuple":
            self.collectionHandler = TupleCollectionHandler()
        elif self.op1 == "dict":
            self.collectionHandler = DictCollectionHandler()
        else:
            return (1, "unknown collection type")
        return (None, "")

    def _extract(self, cell):
        if cell is None:
            return None, None, None
        return cell.text(), cell, cell.more

class RowFixtureAT(RowFixture):
    def query(self):
        return self.getSymbol("theList").collection

    def getTargetClass(self):
        RowFixtureAT._typeDict = self.getSymbol("theList").metaData
        return self
