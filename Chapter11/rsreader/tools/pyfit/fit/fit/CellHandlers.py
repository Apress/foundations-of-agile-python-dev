# Cell Handlers
#legalStuff jr05
# Copyright 2005 John H. Roth Jr.
# Released under the terms of the General Public License (GPL), Release 2.1 or later
# See license.txt for terms and disclaimer of all warrenties and liability.
# Last updated for Release 0.8a1
#endLegalStuff

# the exception[], Fail[] and error cell handlers are in the
# basic adapter logic, since they have to trap exceptions.


import re
import sys
import types

from fit.FitException import FitException
from fit.InitEnvironment import FG
from fit.Parse import Parse
from fit import taTable
from fit.Utilities import em

OK = "ok"
NEXT = "next"
ERROR = "error"

def fbool(anInt): #pragma: no cover
    if anInt == -1:
        return False
    else:
        return True

class CellHandler(object):
    def __new__(cls, aName):
        if isinstance(aName, CellHandler):
            return aName
        return object.__new__(cls)

    def __init__(self, aName):
        if isinstance(aName, CellHandler):
            return
        if isinstance(aName, types.StringTypes):
            self.name = aName
            self.handlerClass = FG.appConfigInterface("mapCellHandler",
                                                      (aName,))
            if self.handlerClass is False:
                return
            if aName.startswith("@"):
                if self.handlerClass in (None, True):
                    return
                self.classToNameCache[self.handlerClass] = aName
                self.nameToClassCache[aName] = self.handlerClass
            else:
                self.handlerClass = taTable.cellHandlerTable.get(aName)
                if self.handlerClass is None:
                    self.handlerClass = self.nameToClassCache.get(aName)
        elif (issubclass(aName, object)):
            self.handlerClass = FG.appConfigInterface("mapCellHandler",
                                                      (aName,))
            if self.handlerClass is False:
                self.name = self.handlerClass
                self.handlerClass = aName
                return
            self.handlerClass = aName
            try:
                self.name = taTable.cellHandlerClassToName[aName]
                return
            except KeyError:
                pass
            self.name = self._nameFromClassCache(aName)

    def __eq__(self, other):
        if not other.isValid():
            return False
        if not self.isValid(): #pragma: no cover
            return False
        return self.handlerClass is other.handlerClass

    def isValid(self):
        if self.name in (True, False, None):
            return False
        if self.handlerClass in (True, False, None):
            return False
        return True

    def _nameFromClassCache(cls, aClass):
        name = cls.classToNameCache.get(aClass)
        if name is not None:
            return name
        name = aClass.__name__
        cls.classToNameCache[aClass] = name
        cls.nameToClassCache[name] = aClass
        return name
    _nameFromClassCache = classmethod(_nameFromClassCache)

    classToNameCache = {}
    nameToClassCache = {}

    def _testInit(cls):
        cls.classToNameCache = {}
        cls.nameToClassCache = {}
    _testInit = classmethod(_testInit)

    def __repr__(self): #pragma: no cover # I don't care...
        return "<CellHandler('%s')>" % self.name

class CellHandlers(object):
    def __init__(self, aList=None):
        self.handlerList = []
        if aList is not None:
            self.addHandlers(aList)

    def addHandler(self, handler):
        obj = CellHandler(handler)
        if not obj.isValid():
            return
        for item in self.handlerList:
            if obj == item:
                return
        self.handlerList.append(obj)

    def addHandlers(self, aList):
        [self.addHandler(x) for x in aList]

    def removeHandler(self, handler):
        obj = CellHandler(handler)
        i = 0
        while i < len(self.handlerList):
            if self.handlerList[i] == obj:
                del self.handlerList[i]
                break
            i += 1

    def removeHandlers(self, aList):
        [self.removeHandler(x) for x in aList]

    def __getitem__(self, key):
        if isinstance(key, int):
            if 0 <= key < len(self.handlerList):
                return self.handlerList[key]
            raise IndexError, key
        raise TypeError("Arguement must be an integer")

    def __len__(self):
        return len(self.handlerList)

    def tailorCellHandlerList(self, accessor, identifier,
                              typeName, metadata):
        
        # get dictionary from application exit
        chDict = FG.appConfigInterface("manageCellHandlers",
                                              typeName)
        
        # different paths if False, None or dictionary
        #    False - remove default list and return
        #    None - do requested metadata updates and return
        if chDict is False:
            self.handlerList = []
            return
        if chDict is None:
            self._tailorCellHandlersUsingMetadata(accessor, identifier, metadata)
            self._removeInapplicableCellHandlersFromList(accessor, typeName)
            return

        # process .noDefault
        if chDict.get(".startWithDefaultList") == "no":
            self.handlerList = []

        # 0.9 - type adapter add list

        # process add and remove lists
        addList = self._extractCellHandlerList(chDict, "add")
        self.addHandlers(addList)
        removeList = self._extractCellHandlerList(chDict, "remove")
        self.removeHandlers(removeList)

        # update from metadata
        if chDict.get(".updateFromMetadata") != "no":
            permitList = self._extractCellHandlerList(chDict, "permit")
            addList = metadata.get("%s.addCellHandlers" % identifier, [])
            if permitList: #pragma: no cover # better tests in 0.9
                for request in addList:
                    if chDict.get(request) == "permit":
                        self.addHandler(request)
            else:
                self.addHandlers(addList)
            delList = metadata.get("%s.removeCellHandlers" % identifier, [])
            self.removeHandlers(delList)
            
        # process required and prohibited lists
        addList = self._extractCellHandlerList(chDict, "require")
        self.addHandlers(addList)
        removeList = self._extractCellHandlerList(chDict, "prohibit")
        self.removeHandlers(removeList)

        # cross-validate ch and ta
        self._removeInapplicableCellHandlersFromList(accessor, typeName)
        return

    def _extractCellHandlerList(self, chDict, keyword):
        return [item[0] for item in chDict.items()
                        if item[1] == keyword]

    def _tailorCellHandlersUsingMetadata(self, unused, identifier, metaData):
        addList = metaData.get("%s.addCellHandlers" % identifier, [])
        self.addHandlers(addList)
        delList = metaData.get("%s.removeCellHandlers" % identifier, [])
        self.addHandlers(delList)

    def _removeInapplicableCellHandlersFromList(self, accessor, typeName):
        removeList = []
        for wrapper in self.handlerList:
            ch = wrapper.handlerClass()
            if hasattr(ch, "isTypeAdapterApplicable"):
                applicable = ch.isTypeAdapterApplicable(typeName)
            if applicable is None:
                ta = accessor.adapter
                if hasattr(ta, "isCellHandlerApplicable"):
                    applicable = ta.isCellHandlerApplicable(wrapper.name)
            if applicable is False:
                removeList.append(wrapper.name)
        self.removeHandlers(removeList)
        return

class CellHandlerBase(object):
    canParse = True
    canCheck = True
    canCheckAfter = False

    def isTypeAdapterApplicable(self, taName):
        result = self._checkTAList(taName, "includeList", True, False)
        if result is True:
            return True
        return self._checkTAList(taName, "excludeList", False, None)

    def _checkTAList(self, name, listName, found, notFound):
        theList = getattr(self, listName, None)
        if theList is None:
            return None
        try:
            theList.index(name)
        except ValueError:
            return notFound
        return found

    def getEditedText(self, cell):
        if isinstance(cell, Parse):
            return cell.text()
        if isinstance(cell, types.StringTypes):
            return cell
        raise FitException("invalidCellHandlerType", type(cell), cell)

    def getRawText(self, cell):    
        if isinstance(cell, Parse):
            return cell.body
        if isinstance(cell, types.StringTypes):
            return cell
        raise FitException("invalidCellHandlerType", type(cell), cell)

class BlankCellHandler(CellHandlerBase):
    includeList = ["StringAdapter"]
    
    def parse(self, cell, unused):
        if self.getEditedText(cell) == "blank":
            return (OK, "")
        else:
            return (NEXT, None)

    def check(self, cell, obj, unused):
        if self.getEditedText(cell) != "blank":
            return (NEXT, None)
        elif obj == "":
            return OK, True
        else:
            return OK, False # normal error processing for mismatch.
taTable.cellHandlerTable["Blank"] = BlankCellHandler
taTable.cellHandlerTable["BlankCellHandler"] = BlankCellHandler
taTable.cellHandlerClassToName[BlankCellHandler] = "Blank"

class NullCellHandler(CellHandlerBase):
    def parse(self, cell, unused):
        if self.getEditedText(cell) == "null":
            return (OK, None)
        else:
            return (NEXT, None)

    def check(self, cell, obj, unused):
        if self.getEditedText(cell) != "null":
            return (NEXT, None)
        elif obj is None:
            return OK, True
        else:
            return OK, False # normal error processing for mismatch.
taTable.cellHandlerTable["Null"] = NullCellHandler
taTable.cellHandlerTable["NullCellHandler"] = NullCellHandler
taTable.cellHandlerClassToName[NullCellHandler] = "Null"

class AsisCellHandler(CellHandlerBase):
    includeList = ["StringAdapter"]
    asisRE = re.compile(r"^asis\[(.*)\]$", re.I)

    def _rawMatch(self, reObj, cell):
        text = self.getRawText(cell)
        match = reObj.match(text)
        if match is None:
            return None
        return match.group(1)

    def parse(self, cell, unused):
        result = self._rawMatch(self.asisRE, cell)
        if result is None:
            return NEXT, None
        return OK, result

    def check(self, cell, aString, unused):
        result = self._rawMatch(self.asisRE, cell)
        if result is None:
            return NEXT, None
        if result != aString:
            return OK, False
#            return NEXT, None
        return OK, True
taTable.cellHandlerTable["Asis"] = AsisCellHandler
taTable.cellHandlerTable["AsisCellHandler"] = AsisCellHandler
taTable.cellHandlerClassToName[AsisCellHandler] = "Asis"

class NumericRangeCellHandler(CellHandlerBase):
    canParse = False
    includeList = ["IntegerAdapter", "FloatAdapter"]

    def parse(self, unused, dummy):
        return NEXT, None

    checkRE = re.compile(r"^(.*?)\.\.(.*?)$")
    def check(self, cell, obj, callback):
        __pychecker__ = "no-returnvalues"
        result = self.checkRE.match(self.getEditedText(cell))
        if result is None:
            return NEXT, None
        left, right = result.group(1, 2)
        left = self._edit(left, callback)
        right = self._edit(right, callback)
        if left == "invalid" or right == "invalid":
            return NEXT, None
        if left == "missing" and right == "missing":
            return NEXT, None
        if left == "missing":
            return OK, obj <= right
        if right == "missing":
            return OK, left <= obj
        return OK, left <= obj <= right

    def _edit(self, num, callback):
        num = num.strip()
        if not num:
            return "missing"
        try:
            return callback.protocol.parse(num)
        except:
            return "invalid"
taTable.cellHandlerTable["NumericRange"] = NumericRangeCellHandler
taTable.cellHandlerTable["NumericRangeCellHandler"] = NumericRangeCellHandler
taTable.cellHandlerClassToName[NumericRangeCellHandler] = "NumericRange"

class SubstringCellHandler(CellHandlerBase):
    canParse = False
    def parse(self, unused, dummy):
        return NEXT, None
    checkRE = re.compile(r"^(startswith|endswith|contains)\[(.*?)\]$", re.I)

    def check(self, cell, obj, unused):
        match = self.checkRE.match(self.getEditedText(cell))
        if match is None:
            return NEXT, None
        oper, value = match.group(1, 2)
        lc = oper.lower()
        if lc == "startswith":
            return OK, obj.startswith(value)
        if lc == "endswith":
            return OK, obj.endswith(value)
        if lc == "contains":
            return OK, obj.find(value) > -1
        return NEXT, None #pragma: no cover
taTable.cellHandlerTable["Substring"] = SubstringCellHandler
taTable.cellHandlerTable["SubstringCellHandler"] = SubstringCellHandler
taTable.cellHandlerClassToName[SubstringCellHandler] = "Substring"

class SymbolCellHandler(CellHandlerBase):
    checkRE = re.compile("^<<(.*?)$")

    def _editedMatch(self, reObj, cell):
        text = self.getEditedText(cell)
        match = reObj.match(text)
        if match is None:
            return None
        return match.group(1)
    
    def check(self, cell, obj, callback):
        if not isinstance(cell, Parse):
            return NEXT, None
        result = self._editedMatch(self.checkRE, cell)
        if result is None:
            return (NEXT, None)
        callback.fixture.setSymbol(result, obj)
        cell.addToBody(callback.fixture.gray(
            " = %s" % callback.protocol.toString(obj)))
        return OK, True

    parseRE = re.compile("^(.*?)<<$")
    def parse(self, cell, callback):
        if not isinstance(cell, Parse):
            return NEXT, None
        result = self._editedMatch(self.parseRE, cell)
        if result is None:
            return NEXT, None
        obj = callback.fixture.getSymbol(result)
        cell.addToBody(callback.fixture.gray(
            " = %s" % callback.protocol.toString(obj)))
        return OK, obj
taTable.cellHandlerTable["Symbol"] = SymbolCellHandler
taTable.cellHandlerTable["SymbolCellHandler"] = SymbolCellHandler
taTable.cellHandlerClassToName[SymbolCellHandler] = "Symbol"
