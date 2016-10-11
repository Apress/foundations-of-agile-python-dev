# Python translation of fit..
#legalStuff cc02 sm02 jr03-05
# Original Java version Copyright 2002 Cunningham and Cunningham, Inc.
# Released under the terms of the General Public License (GPL), Release 2.1 or later
# See license.txt for terms and disclaimer of all warrenties and liability.
# Original translation to Python Copyright 2002 Simon Michael
# changes Copyright 2003-2005 John H. Roth Jr.
# Last updated for Release 0.8a1
#endLegalStuff

from fit.Parse import Parse
from fit import FitGlobal
from fit.Fixture import Fixture
from fit.FitException import FitException, exceptionIfNone
from fit import TypeAdapter
from fit.Utilities import em, firstNonNone

try:
    False
except: #pragma: no cover
    True = 1
    False = 0

# cannot begin or end name with an underscore
# !!! Depreciated - use FitException instead.
class InvalidAttributeName(Exception):
    pass

class ColumnFixture(Fixture):
    columnBindings = []
    columnExecutors = []
    hasExecuted = False

    ## Traversal ################################

    def doRows(self, rows):
        exceptionIfNone(rows, "ColumnHeadsMissing")
        self._shouldTakeExits = self._extractMetaData(".takeRowExits")
        if self._shouldTakeExits is None:
            self._shouldTakeExits = FitGlobal.appConfigInterface(
                "columnFixtureExits", rows)
        self.bind(rows.parts)
        super(ColumnFixture, self).doRows(rows.more)

    def doRow(self, row):
        self.hasExecuted = False
        try:
            cell = row.parts
            self.reset()
            if self._shouldTakeExits is not False:
                self.beginningOfRow(row)
            super(ColumnFixture, self).doRow(row)
            cell = row.leaf()
            if self.hasExecuted is False:
                self.execute()
            if self._shouldTakeExits is not False:
                self.endOfRow()
        except Exception, e:
            self.exception(cell, e)

    def beginningOfRow(self, row):
        return None

    def endOfRow(self):
        return None

    def doCell(self, cell, column):
        if column >= len(self.columnExecutors):
            raise FitException("RowTooLong")
        a = self.columnBindings[column]
        try:
            self.columnExecutors[column](cell, a)
        except Exception, e:
            self.exception(cell, e)

    def executeIfFirstResult(self, cell):            
        if self.hasExecuted is False:
            try:
                self.execute()
            except Exception, e:
                self.exception(cell, e)
            self.hasExecuted = True

##    def check(self, cell, a):
##        self.executeIfFirstResult(cell)
##        super(ColumnFixture, self).check(cell, a)

## Executors

    def getExecutor(self, cell, accessor): # foo()
        self.executeIfFirstResult(cell)
        self.check(cell, accessor)
        return None

    def setExecutor(self, cell, accessor):
        text = cell.text()
        if text:
            self.parseAndSet(cell, accessor)
        # added escape because of problem in StandardAnnotationFixture
        else:
            try:
                result = accessor.toString(accessor.get())
                cell.addToBody(self.gray(self.escape(result)))
            except: #pragma: no cover
                pass
        return None

    def getSymbolExecutor(self, cell, accessor): # =foo()
        self.executeIfFirstResult(cell)
        symbolName = cell.text()
        symbolObj = accessor.get()
        symbolString = accessor.toString(symbolObj)
        self.setSymbol(symbolName, symbolObj)
        cell.addToBody(self.gray(" = " + symbolString))
        return None

    def checkSavedExecutor(self, cell, accessor):
        # XXX the symbol versions don't play well with the cell handlers.
        self.executeIfFirstResult(cell)
        symbolName = cell.text()
        symbolObj = self.getSymbol(symbolName)
        symbolString = str(symbolObj)
        cell.addToBody(self.gray(" = " + symbolString))
        savedBody = cell.body
        cell.body = symbolString
        self.check(cell, accessor)
        if cell.body == symbolString:
            cell.body = savedBody
            return None
        cell.body = "%s<hr>%s" % (savedBody, cell.body)
        return None

    def displayExecutor(self, cell, accessor):
        # XXX should throw exception or something if there was something
        #     already in the cell.
        self.executeIfFirstResult(cell)
        obj = accessor.get()
        theString = accessor.toString(obj)
        cell.body = self.gray(theString)
        return None

    def displaySavedExecutor(self, cell, unused):
        symbolName = cell.text()
        symbolObj = self.getSymbol(symbolName)
        symbolString = str(symbolObj)
        cell.addToBody(self.gray(" = " + symbolString))
        return None

    def setSymbolExecutor(self, cell, accessor):
        symbolName = cell.text()
        symbolObj = self.getSymbol(symbolName)
        symbolString = accessor.toString(symbolObj)
        accessor.set(symbolObj)
        cell.addToBody(self.gray(" = " + symbolString))

    def unimplementedExecutor(self, cell, unused):
        text = cell.text()
        if text == "": return None
        self.ignore(cell)
        return None

    def commentExecutor(self, unused="cell", dummy="accessor"):
        return None

    # !!! This can't be reached until the test suite puts the entry
    #     in the columnTypes table.
    def testingErrorExecutor(self, unused="cell", dummy="accessor"):
        raise FitException("anException",
                           "This is a test. This is only a test")
    
    ## Utility ##################################
    ## These three methods are to be overridden if the function is needed
    
    # about to process first cell of row
    def reset(self):
        pass

    # about to process first result of row (or end of row)
    def execute(self):
        pass

    def processLabel(self, label, pos):
        raise Exception("Error in User Fixture: processLabel not implemented"
                        " label: %s pos: %s" % (label,  pos))

    ## End of "virtual" methods    

    def bind (self, heads):
        self.columnBindings = [None] * heads.size()
        self.columnExecutors = [None] * len(self.columnBindings)
        i = 0
        classTypeDict = getattr(self.__class__, "_typeDict", {})
        extendedProcess = classTypeDict.get(".extendedLabelProcess")
        typeDict = self.getTargetClass()._typeDict
        dotMarkup = typeDict.get(".markup")
        dotDisplay = FitGlobal.getDiagnosticOption("displayLabelMapping")
        if dotDisplay is None:
            dotDisplay = (typeDict.get(".display") == "on")
        while heads:
            if extendedProcess == "on":
                try:
                    kind, name = self.processLabel(heads.text(), i)
                except Exception, e:
                    self.exception(heads, e)
                    heads = heads.more
                    i += 1
                    continue
                if kind == "continue":
                    name, kind = self._extractColumnTypeFromOldMarkup(name, typeDict)
                elif kind == "lookup":
                    kind = self._extractColumnTypeUsingMetadata(name, typeDict)
            elif dotMarkup == "off":
                name = self.camel(heads.text())
                kind = self._extractColumnTypeUsingMetadata(name, typeDict)
            else:
                name = heads.text()
                name, kind = self._extractColumnTypeFromOldMarkup(name, typeDict)
            executorName, shouldGetTypeAdapter = self.columnTypes.get(kind,
                                                        (None, False))
            try:
                self._bindColumnExecutor(executorName, kind, i, name)
            except FitException, e:
                self.exception(heads, e)
                self._bindColumnExecutor("unimplementedExecutor",
                                         "ignore", i, name)
                self.columnBindings[i] = None
                shouldGetTypeAdapter = False
            if shouldGetTypeAdapter:
                self._bindAdapter(name, heads, i)
            else:
                self.columnBindings[i] = None
            if dotDisplay:
                diagDisplay = "<hr>Type: %s<br>Name: %s" % (kind, name)
                heads.addToBody(self.gray(diagDisplay))
            heads = heads.more
            i += 1

    columnTypes  = {None: ("setExecutor", True),
                    "checkSaved": ("checkSavedExecutor", True),
                    "comment": ("commentExecutor", False),
                    "display": ("displayExecutor", True),
                    "displaySaved": ("displaySavedExecutor", False),
                    "getSymbol": ("getSymbolExecutor", True), # old
                    "given": ("setExecutor", True),
                    "ignore": ("unimplementedExecutor", False),
                    "result": ("getExecutor", True),
                    "saveResult": ("getSymbolExecutor", True),
                    "setSymbol": ("setSymbolExecutor", True), # old
                    "storeSaved": ("setSymbolExecutor", True),
                    }

    def _extractColumnTypeFromOldMarkup(self, label, typeDict):
        __pychecker__ = "no-noeffect" # or below; doesn't seem to work.
        if len(label) == 0:
            name = ""
            colType = "comment"
        elif (label.startswith("?")):
            name = ""
            colType = "ignore"
        elif (label.startswith("=")):
            name = self._trimEndingMarkup(label[1:])
            colType = "saveResult"
        elif (label.endswith("()")):
            name = label[:-2]
            colType = "result"
        elif (label[-1] in ("?", "!")):
            name = label[:-1]
            colType = "result"
        elif (label.endswith("=")):
            name = label[:-1]
            colType = "storeSaved"
        else:
            name = label
            colType = "given"
        identifier = self.camel(name)
        if colType == "given":
            newKind = self._extractColumnTypeUsingMetadata(identifier, typeDict)
            colType = firstNonNone(newKind, colType)
        return identifier, colType

    def _trimEndingMarkup(self, label):
        if label.endswith("()"):
            name = label[:-2]
        elif label[-1] in ("?", "!"):
            name = label[:-1]
        else:
            name = label
        return name

    def _bindAdapter(self, name, heads, i):
        try:
            adapter = TypeAdapter.on(self, name, None, self, self.getTargetClass())
            self.columnBindings[i] = adapter
        except Exception, e:
            self.exception(heads, e)
            self._bindColumnExecutor("unimplementedExecutor",
                                     "ignore", i, name)

    def _extractColumnTypeUsingMetadata(self, name, typeDict):
        kind = typeDict.get(name + ".columnType")
        return kind

    def _bindColumnExecutor(self, executorName, kind, i, identifier):
        if executorName is None:
            raise FitException("UnknownColumnType", kind, identifier)
        self.columnExecutors[i] = getattr(self, executorName)

    def getTargetClass(self):
        return self.__class__
