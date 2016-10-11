# Python translation of fit..
#legalStuff cc02 sm02 jr03-05
# Original Java version Copyright 2002 Cunningham and Cunningham, Inc.
# Released under the terms of the General Public License (GPL), Release 2.1 or later
# See license.txt for terms and disclaimer of all warrenties and liability.
# Original translation to Python Copyright 2002 Simon Michael
# changes Copyright 2003-2005 John H. Roth Jr.
# Last updated for Release 0.8a1
#endLegalStuff

import types
from fit.FitException import FitException
from fit.Fixture import Fixture
from fit.Parse import Parse
from fit import TypeAdapter
from fit import taProtocol as taPro
from fit.Utilities import em

try:
    False
except: #pragma: no cover
    True = 1
    False = 0

class RowFixtureBase(Fixture):
    actuals = []
    def __init__(self, collection = None, typeDict = None):
        super(RowFixtureBase, self).__init__()
        self.paramCollection = collection
        self.paramTypeDict = typeDict

    def setActualCollection(self):
        collection = self.paramCollection
#        typeDict = self.paramTypeDict
        if collection is None:
            args = self.getArgCells()
            if len(args) == 2 and self.__class__.__name__ in (
                            "RowFixture", "ArrayFixture",
                            "SetFixture", "SubsetFixture"):
                try:
                    argObj = self.getSymbol(args[1].text())
                except Exception:
                    self.exception(args[1],
                        FitException("SymbolNotDefined", args[1].text()))
                    raise FitException("IgnoreException")
                collection = argObj.collection
                RowFixture._typeDict = argObj.metaData
#                typeDict = argObj.metaData
            else:
                collection = self.query()
#                typeDict = self.getTargetClass()._typeDict
        if isinstance(collection, dict):
            aList = collection.items()
            aList.sort()
            self.actuals = [y for x, y in aList]
        elif (isinstance(collection, types.StringTypes)):
            raise FitException("UnsupportedCollectionType", type(collection))
        else:
            try:
                self.actuals = [x for x in collection]
            except Exception:
                raise FitException("UnsupportedCollectionType", type(collection))

    def query(self): #pragma: no cover     ## get rows to be compared
        return None

    def getTargetClass(self):
        return self.__class__

    def processLabel(self, label, colNum): #pragma: no cover
        raise Exception("Error in RowFixture subclass: processLabel is not"
                        " overridden. label: %s colNum: %s" %
                        (label, colNum))

    # returns [(TypeAdapter, fieldName, columnType),...]
    # XXX Code Smell - duplicates code in ArrayFixture
    def bind(self, labels):
        wasError = False
#        usedField = [False] * labels.size()
        adapters = []
        fieldNames = []
        symRefs = []
#        targetClass = self.getTargetClass()
        typeDict = self.paramTypeDict
        typeDict = typeDict or getattr(self, "_typeDict", None) # legacy
        typeDict = typeDict or self.getTargetClass()._typeDict
        extendedLabelProcess = typeDict.get(".extendedLabelProcess", "off")
        colNum = 0
        while labels is not None:
            fieldName = labels.text()
            if extendedLabelProcess == "on":
                colType, camelName = self.processLabel(fieldName, colNum)
                isSymRef = (colType == "checkSymbol")
            else:
                isSymRef, camelName = self._decodeLabel(fieldName, typeDict)
            if not self._isFieldInAnyObject(camelName, self.actuals):
                self.exception(labels,
                    FitException("FieldNotInCollection"))
                wasError = True
                accessor = None
            else:
#                metaData = typeDict.get(camelName)
                colType = typeDict.get(camelName + ".columnType")
                if colType == "checkSymbol":
                    isSymRef = True
                try:
                    accessor = TypeAdapter.on(self, camelName, typeDict,
#                            {camelName: metaData},
                            accClass = TypeAdapter.AccessorBaseClass)
                except FitException, e:
                    self.exception(labels, e)
                    accessor = None
            adapters.append(accessor)
            fieldNames.append(camelName)
            symRefs.append(isSymRef)
            labels = labels.more
            colNum += 1
        if wasError:
            raise FitException("IgnoreException")
        self.columnBindings = zip(adapters, fieldNames, symRefs)
        return self.columnBindings

    def _decodeLabel(self, fieldName, typeDict):
        mapType = typeDict.get(".useToMapLabel")
        markup = typeDict.get(".markup", "on")
        if markup == "off":
            return False, self.camel(fieldName, mapType)
        if not fieldName.endswith("="):
            return False, self.camel(fieldName, mapType)
        return True, self.camel(fieldName[:-1], mapType)

    def _isFieldInAnyObject(self, fieldName, actuals):
        # ??? Do we want to provide an option to avoid checking?
        if len(actuals) == 0:
            return True
        for objectOrDict in actuals:
            hasKey, obj = self._getObj(fieldName, objectOrDict)
            if hasKey:
                return True
        return False

    def _getObj(self, name, objectOrDict):
        result = False, None
        if isinstance(objectOrDict, dict):
            if objectOrDict.has_key(name):
                result = True, objectOrDict.get(name)
        else:
            if hasattr(objectOrDict, name): 
                result = True, getattr(objectOrDict, name, None)
                if callable(result[1]):
                    result = True, result[1]()
        return result

class RowFixture(RowFixtureBase):
    missing = []
    surplus = []

    def doRows(self,rows):
        self.setActualCollection()
        if rows is None:
            raise FitException("ColumnHeadsMissing")
        try:
            self.bind(rows.parts)
            self.missing = []
            self.surplus = []
            rowList = self._checkForShortRows(rows.more)
            self.match(rowList, self.actuals, 0)
            last = rows.last()
            last.more = self.buildRows(self.surplus)
            self.markRows(last.more, "surplus")
            self.markList(self.missing, "missing")
        except Exception, e:
            self.exception(rows.leaf(), e)

    def _checkForShortRows(self, rows):
        minLen = len(self.columnBindings)
        rowList = []
        while rows is not None:
            # !!! Following test is for a condition that gets a Parse exception
            #     See test named:
            #       shouldMarkRowWithoutCellsAsMissingWithExceptiion
            if rows.parts is not None:
                rowLen = rows.parts.size()
                if rowLen < minLen:
                    self.exception(rows.parts, FitException("RowTooShort"))
                    self.missing.append(rows)
                else:
                    rowList.append(rows)
            else: #pragma: no cover
                newCell = Parse(tag='td colspan="%s"' % minLen,
                                body = "[Cell inserted by RowFixture]")
                self.exception(newCell, FitException("noCells"))
                rows.parts = newCell
                self.missing.append(rows)
            rows = rows.more
        return rowList

    def match(self, expected, computed, col):
        if col >= len(self.columnBindings):
            self.check(expected, computed)
        elif self.columnBindings[col][0] is None:
            self.match (expected, computed, col + 1)
        else:
            keyMap = {}
            self.ePartition(expected, col, keyMap)
            self.cPartition(computed, col, keyMap)
            for key, value in keyMap.items():
                eList, cList = value
                if not eList:
                    self.surplus.extend(cList)
                elif not cList:
                    self.missing.extend(eList)
                elif (len(eList)==1 and len(cList)==1):
                    self.check(eList, cList)
                else:
                    self.match(eList, cList, col+1)

    def ePartition(self, rows, col, map):
        a, colName, isSymRef = self.columnBindings[col]
        for row in rows:
            cell = row.parts.at(col) # !!! returns last one on short row.
            try:
                if a is None: #pragma: no cover # shouldn't happen - yet.
                    key = cell.text()
                elif isSymRef:
                    key = self._getSymRefObj(cell)
                else:
                    key = a.parse(cell.text())
                self.insureKeyExists(map, key)
                map[key][0].append(row)
            except Exception, e:
                self.exception(cell, e)
                # mark the rest of the row as ignored (i.e. grey it out)
                rest = cell.more
                while rest:
                    self.ignore(rest)
                    rest = rest.more
        return
    
    def cPartition(self, collection, column, map):
        a, name, isSym = self.columnBindings[column]
        for anObject in collection:
            try:
                a.target = anObject
                hasValue, value = self._getObj(name, anObject)
                if hasValue:
                    a.set(value)
                    self.insureKeyExists(map, value)
                    map[value][1].append(anObject)
                else:
                    self.surplus.append(anObject)
            except Exception: #pragma: no cover # shouldn't happen?
                ## surplus anything with bad keys, including None
                self.surplus.append(anObject)
        return

    def insureKeyExists(self, map, key):
        if map.has_key(key):
            return
        map[key] = [[], []]
        return
    
    def check (self, eList, cList):
        # called either when both sizes are one, or we've run out of columns
        # to compare. The first set of tests stops the recursion; neither one
        # should trigger on the initial entry from match(...)
        if not eList:
            self.surplus.extend(cList)
            return
        if not cList:
            self.missing.extend(eList)
            return
        # There is at least one in each list. Process the first one,
        # and then recurse on the shorter lists
        # ??? Recursion is neat, but this might blow the stack for very
        #     large numbers of duplicates. Should I recast this routine
        #     as an iterative loop?
        row = eList.pop(0)
        cell = row.parts
        obj = cList.pop(0)
        for a, name, isSymRef in self.columnBindings:
            hasKey, value = self._getObj(name, obj)
            if not hasKey:
                self.ignore(cell)
            elif a is None:
                self.checkString(cell, value)
            else:
                a.target = obj
                a.set(value)
                if isSymRef:
                    self._checkRef(a, cell, value)
                else:
                    super(RowFixture, self).check(cell, a)
            cell = cell.more
        self.check(eList, cList)

    def checkString(self, cell, value):
        strValue = str(value)
        if strValue == cell.text():
            self.right(cell)
            return
        self.wrong(cell, strValue)

    def _checkRef(self, adapter, cell, value):
        refObj = self._getSymRefObj(cell)
        if adapter.equals(refObj, value):
            self.right(cell)
            return
        self.wrong(cell, str(value))

    def _getSymRefObj(self, cell):
        if hasattr(cell, "symbolName"):
            symName = cell.symbolName
            obj = self.getSymbol(symName)
        else:
            symName = cell.text()
            cell.symbolName = symName
            obj = self.getSymbol(symName)
            cell.addToBody(self.gray(" = " + str(obj)))
        return obj

    def markRows(self, rows, message):
        annotation = self.label(message)
        while rows:
            if not (rows.parts.tagIsError() or rows.parts.tagIsWrong()):
                self.wrong(rows.parts)
            rows.parts.addToBody(annotation)
            rows = rows.more

    def markList(self, rows, message):
        annotation = self.label(message)
        for row in rows:
            if not (row.parts.tagIsError() or row.parts.tagIsWrong()):
                self.wrong(row.parts)
            row.parts.addToBody(annotation)

    def buildRows(self, rows):
        root = Parse(tag="xx")
        for row in rows:
            newRow = Parse(tag="tr", parts=self.buildCells(row))
            newRow.more = root.more
            root.more = newRow
        return root.more

    def buildCells(self, obj):
        next = root = Parse(tag="xx")
        for a, name, isSymRef in self.columnBindings:
            next.more = Parse(tag="td", body="")
            next = next.more
            hasKey, value = self._getObj(name, obj)
            if not hasKey:
                next.info("[missing attribute]")
            else:
                if not a:
                    try:
                        next.body = str(value)
                    except Exception:
                        next.info("[error extracting value]")
                else:
                    try:
                        a.target = obj
                        a.set(value)
                        next.body = a.toString(a.get())
                    except Exception, e: #pragma: no cover # shouldn't be possible
                        self.exception(next, e)
        return root.more
