# TypeAdapter for FIT
#LegalStuff cc02 sm02 jr03-05
# Original Java version Copyright 2002 Cunningham and Cunningham, Inc.
# Released under the terms of the General Public License (GPL), Release 2.1 or later
# See license.txt for terms and disclaimer of all warrenties and liability.
# Original translation to Python Copyright 2002 Simon Michael
# changes Copyright 2003-2005 John H. Roth Jr.
# Last updated for Release 0.8a1
#endLegalStuff

import compiler
import copy
import inspect
#import math
#import operator
import re
#import struct
import sys
#import time
import token, tokenize
import traceback
import types
from types import *

import fit # XXX pychecker complains about this
#from fit import CellHandlers
from fit.Utilities import em, firstNonNone
from fit.CellHandlers import CellHandler, CellHandlers, NEXT
from fit.FitException import FitException, raiseIf, raiseIfNone
from fit.FitNesseExceptions import FitFailureException
from fit.InitEnvironment import FG as FitGlobal
from fit.Parse import Parse

from fit.taBase import TypeAdapter
from fit.taProtocol import getProtocolFor
from fit.taTable import typeAdapterTable, _isApplicationProtocol, \
     typeToAdapter, _isAdapterProtocol, cellHandlerTable as CHT

try:
    False
except: #pragma: no cover
    True = 1
    False = 0

## Factory ##################################

# the next four factories are obsolete - they are retained
# until the rest of the package is restructured to conform.
# !!! The unit tests have been commented out - they are still
#     available if anyone wants them.

# !!! These routines are used by FrameworkTest - it needs to
#     be redone to avoid them.

# !!! This could be useful if it actually did what it says it does.
#     However, the Default adapter mechanism has taken over the
#     general area.

def adapterOnType(instance, name, metaData = None):
    if metaData is None:
        return on(instance, "Dummy", {"Dummy": name})
    else:
        return on(instance, name, metaData = metaData)

#     These two are basically aliases for on()
def adapterOnField(instance, fieldName):
    return on(instance, fieldName)

def adapterOnMethod(instance, methodName):
    return on(instance, methodName)

#     This is what the on() factory function does anyway.
def adapterForStringTypeName(typeName):
    typeName = typeName.title()
    return on(None, "Dummy", {"Dummy": typeName})

# This is the basic factory to return a stack of an Accessor, protocol
# object and TypeAdapter. Notice that _getTypeAdapter is also used to
# just get a type adapter.

def on(instance, name, metaData = None, owner = None,
       targetClass = None, accClass = None):
    __pychecker__ = "no-noeffect" # or below; doesn't seem to work.
    if instance is None and targetClass is None and metaData is None:
        raise FitException, ('BadParm001',)
    if instance is not None and targetClass is None:
        targetClass = instance.__class__
    if metaData is None:
        if name in ("?", ""):
            metaData = {"": "String", "?": "String"}
        else:
            metaData = targetClass._typeDict

    name = firstNonNone(metaData.get("%s.RenameTo" % name),
                        metaData.get("%s.renameTo" % name), name)
    # notice that this path doesn't support the "name.types" variant.
    typeName = metaData.get(name)
    if typeName is None:
        if FitGlobal.appConfigInterface("canDefaultMissingMetadata") is True:
            typeName = "Default"
        else:
            raise FitException, ("NoTypeInfo", name,
                                 targetClass and targetClass.__name__)

    # ----------------- end metadata extraction ------------------------

    return _taFactory(instance, name, owner, typeName,
                      metaData, targetClass, accClass)

def _taFactory(instance, identifier, owner, typeName, metaData,
               targetClass, accClass = None):
    if accClass is None:
        accessorObj = _getAccessor(instance, identifier, owner, targetClass)
    else:
        accessorObj = accClass(instance, identifier, owner, targetClass)
    
    typeAdapterObj = _acquireTypeAdapter(instance, identifier,
                                         typeName, metaData)

    # !!! Hack, hack
    if typeName == "Default":
        accessorClass = accessorObj.__class__
        if accessorClass == FieldAccessor:
            try:
                obj = accessorObj.get()
            except:
                raise FitException("defaultTANoAttribute", identifier)
            # !!! hack - temp until descriptor accessor added.
            # 0.9 descriptors should have both kinds of access.
            instClass = instance.__class__
            identInClass = getattr(instClass, identifier, None)
            if identInClass is None or not hasattr(identInClass, "__get__"):
                result = _acquireAdapterForType(instance,
                                        identifier, obj, metaData)
                if result is not None:
                    typeAdapterObj = result
                else:
                    raise FitException("defaultTAinvalidAdapter", typeName)
            else:
                raise FitException("descriptorInvalidForDefaultTA")
        elif accessorClass == GetMethodAccessor:
            accessorObj = GetMethodDefaultAccessor(instance, identifier,
                                                   owner, targetClass)
        elif accessorClass == SetMethodAccessor:
            typeAdapterObj = _acquireTypeAdapter(instance, identifier,
                            "String", {identifier: "String"})

    protocol = getProtocolFor(typeAdapterObj)
    accessorObj.protocol = protocol
    accessorObj.adapter = typeAdapterObj
    accessorObj.metaData = metaData

    # ------------ tailor cell handler list in the accessor object
    accessorObj.cellHandlerList.tailorCellHandlerList(accessorObj,
                                    identifier, typeName, metaData)
    return accessorObj

# ------------------------
#
# externalize the routine above
#
# ------------------------
fit.taTable.on = on

# This is a streamlined factory for type adapters when the caller knows
# what he wants, and doesn't need a protocol or an accessor to go with
# it.

def _getTypeAdapter(instance, varName, metaData = {}):
    theClass = instance.__class__
    if varName == "":
        a = typeAdapterTable["String"](instance, varName,
                                       "String", metaData = metaData)
        return a
    typeName = metaData.get(varName)
    if typeName is None:
        metaData = instance._typeDict
        typeName = metaData.get(varName)
    if typeName is None:
        raise FitException, ("NoTypeInfo", varName, theClass.__name__)
    return _acquireTypeAdapter(instance, varName, typeName, metaData)

# ------------------------
#
# externalize the routine above
#
# ------------------------
fit.taTable._getTypeAdapter = _getTypeAdapter

# and this is the common process between on and _getTypeAdapter. 
def _acquireTypeAdapter(instance, identifier, typeName, metaData):
    taClass = FitGlobal.appConfigInterface("mapTypeAdapter", typeName)
    raiseIf(taClass is False, "taRejected", typeName)
    trueOrNone = taClass in (True, None)
    if isinstance(typeName, StringTypes):
        if typeName[0] == "@":
            raiseIf(trueOrNone, "UnknownType, typeName")
        else:
            raiseIf(not trueOrNone, "taRejected", typeName)
            taClass = typeAdapterTable.get(typeName)
        raiseIfNone(taClass, 'UnknownType', typeName)
    else:
        raiseIf(not trueOrNone, "taRejected", typeName)
        if inspect.isclass(typeName):
            taClass = typeName
            typeName = taClass.__name__
        else:
            taClass = typeName
            typeName = taClass.__class__.__name__
            strType = repr(taClass.__class__)
            raiseIf(strType[1:5] == "type", "UnknownType", typeName)

    if inspect.isclass(taClass):
        if issubclass(taClass, TypeAdapter):
            typeAdapterObj = taClass(instance, identifier, typeName,
                                     metaData = metaData)
            return typeAdapterObj
        elif (_isApplicationProtocol(taClass)):
            typeAdapterObj = taClass # Application object usable directly
            return typeAdapterObj
        else:
            typeAdapterObj = taClass() # Application Specific Type Adapter
    else:
        typeAdapterObj = taClass
    typeAdapterObj.metaData = copy.copy(metaData)
    typeAdapterObj.name = identifier
    typeAdapterObj.typeName = typeName
    return typeAdapterObj

def _acquireAdapterForType(instance, identifier, obj, metaData):
    result = FitGlobal.appConfigInterface("getAdapterForObject", obj)
    if result is False:
        return None # object cannot be adapted or used.
    if result is None:
        taClass = obj.__class__
        taName = taClass.__name__
        aClass = typeToAdapter.get(taClass)
        if aClass is not None:
            adapter = aClass(instance, identifier, taName,
                                     metaData = metaData)
            return adapter

        if _isApplicationProtocol(taClass):
            return taClass # Application object usable directly
        if _isAdapterProtocol(taClass):
            result = taClass
        else:
            return None

    taClass = result
    taName = taClass.__name__
    adapter = taClass() # Application Specific Type Adapter
    adapter.metaData = copy.copy(metaData)
    adapter.name = identifier
    adapter.typeName = taName
    return adapter

# XXX depreciated!
def addTypeAdapterToDictionary(name, adapterClass):
    currentAdapter = typeAdapterTable.get(name)
    if currentAdapter:
        intAdapter = typeAdapterTable.get("Integer")
        if currentAdapter.__module__ == intAdapter.__module__:
            return False
    typeAdapterTable[name] = adapterClass
    return currentAdapter

def _getAccessor(instance, name, owner, targetClass):
    if targetClass is None:
        theAccessor = AccessorBaseClass(instance, name,
                                        owner, targetClass)
    elif name in ("", "?"):
        theAccessor = AccessorBaseClass(instance, name,
                                    owner, targetClass)
    else:
        theObj = getattr(targetClass, name, None)
        if type(theObj) == MethodType:
            numArgs = theObj.func_code.co_argcount
            if numArgs == 1: # must be getter
                theAccessor = GetMethodAccessor(instance, name,
                                              owner, targetClass)
            elif numArgs == 2:
                theAccessor = SetMethodAccessor(instance, name,
                                              owner, targetClass)
            else:
                raise FitException, ("WrongNumberOfParameters", name, targetClass.__name__)
        else:
            theAccessor = FieldAccessor(instance, name,
                                      owner, targetClass)

    return theAccessor

def _addCellHandlersToAccessor(accessor, handlerList):
    targetList = accessor.cellHandlerList
    targetList.addHandlers(handlerList)

def _removeCellHandlersFromAccessor(accessor, handlerList):
    targetList = accessor.cellHandlerList
    targetList.removeHandlers(handlerList)

##def _getName(instanceOrString):
##    if isinstance(instanceOrString, StringTypes):
##        return instanceOrString
##    return instanceOrString.__class__.__name__

#-------- routines used by the Cell Handler Fixtures ----------

def getCurrentCellHandlerList():
    return AccessorBaseClass.cellHandlerList

def clearCellHandlerList():
    AccessorBaseClass.cellHandlerList = CellHandlers()

def restoreDefaultCellHandlerList():
    AccessorBaseClass.cellHandlerList = CellHandlers(
        AccessorBaseClass.defaultCellHandlerList)

def addOptionalHandlerToList(name):
    numHandlers = len(AccessorBaseClass.cellHandlerList)
    _addCellHandlersToAccessor(AccessorBaseClass, [name])
    return numHandlers + 1== len(AccessorBaseClass.cellHandlerList)

def removeHandlerFromList(name):
    numEntries = len(AccessorBaseClass.cellHandlerList)
    _removeCellHandlersFromAccessor(AccessorBaseClass, [name])
    if numEntries == len(AccessorBaseClass.cellHandlerList):
        return False
    return True

# ------------- end of Cell Handler support routines ----------

# ------------- Result Objects for check routine ---------------

class CheckResult(object):
    parseResult = None
    resultType = "None"
    value = None
    
    def annotateCell(self, cell):
        pass

    def tabulateResult(self, counts):
        pass

    def isRight(self):
        return self.resultType == "right"

    def __str__(self):
        return "CheckResult: No data to report"

    def __nonzero__(self):
        return self.resultType == "right"

class CheckResult_DoNothing(CheckResult):
    resultType = "None"
    value = None
    def __str__(self):
        return "CheckResult: Do Nothing object"

class CheckResult_ParseOK(CheckResult):
    resultType = "ParseOK"
    def __str__(self):
        return ("CheckResult: Parse and Set successful. Parse result: %s" %
                (self.value,))

    def isRight(self):
        return True

    def __nonzero__(self):
        return True

class CheckResult_Right(CheckResult):
    resultType = "right"

    def __init__(self, actual=None):
        self.actual = actual
        self.value = actual

    def annotateCell(self, cell):
        cell.right(self.actual)

    def tabulateResult(self, counts):
        counts.right += 1

    def __str__(self):
        return "CheckResult_Right. actual data: '%s'" % self.actual

class CheckResult_Wrong(CheckResult):
    resultType = "wrong"    

    def __init__(self, actual=None, escape=True):
        self.actual = actual
        self.value = actual
        self.escape = escape

    def annotateCell(self, cell):
        cell.wrong(self.actual, self.escape)

    def tabulateResult(self, counts):
        counts.wrong += 1

    def __str__(self):
        return "CheckResult_Wrong. actual data: '%s'" % self.actual

class CheckResult_Info(CheckResult):
    resultType = "None"
    
    def __init__(self, actual=None):
        self.actual = actual
        self.value = actual

    def annotateCell(self, cell):
        cell.info(self.actual)

    def __str__(self):
        return "CheckResult_Info. actual data: '%s'" % self.actual

class CheckResult_Ignore(CheckResult):
    value = None
    resultType = "ignore"    

    def annotateCell(self, cell):
        cell.ignore()

    def tabulateResult(self, counts):
        counts.ignores += 1

    def __str__(self):
        return "CheckResult_Ignore"

class CheckResult_Exception(CheckResult):
    value = None
    resultType = "exception"    

    def __init__(self, exc):
        self.exc = exc
        self.exType, self.val, tb = sys.exc_info()
        self.tb = "".join(traceback.format_exception(self.exType, self.val, tb))
        tb = None # attempt to prevent a reference loop.
        self.doTrace = 1
        if isinstance(exc, FitException):
            isExc, self.doTrace, self.actual = exc.getMeaningfulMessage()
            if self.doTrace == 2:
                self.__class__ = CheckResult_DoNothing
                return
            elif isExc == 0:
                self.__class__ = CheckResult_ExceptionWrong
                return
        # depreciated - from FitNesseExceptions
        elif (isinstance(exc, FitFailureException)): #pragma: no cover
            self.actual = str(exc)
            self.doTrace = 0
        else:
            self.actual = str(exc)

    def annotateCell(self, cell):
        if self.doTrace == 0:
            cell.exception(self.actual, False, self._excBackground())
        else:
            cell.exception(self.tb, True, self._excBackground())

    def _excBackground(self):
        return "exception"

    def tabulateResult(self, counts):
        counts.exceptions += 1

    def __str__(self):        
        if self.doTrace == 0:
            result = self.actual
        else:
            result = self.tb
        return "%s\n%s" % (self.__class__.__name__, result)

class CheckResult_ExceptionRight(CheckResult_Exception):
    value = None
    resultType = "right"

    def _excBackground(self):
        return "right"

    def tabulateResult(self, counts):
        counts.right += 1

class CheckResult_ExceptionWrong(CheckResult_ExceptionRight):
    value = None
    resultType = "wrong"    

    def _excBackground(self):
        return "wrong"

    def tabulateResult(self, counts):
        counts.wrong += 1

# Exception Cell Handler Parameters support classes

class TokenizeReader(object):
    def __init__(self, aString):
        self.aString = aString + "\n"

    def __call__(self):
        outLine = self.aString
        self.aString = ""
        return outLine

class ExceptionCellHandlerParameters(object):
    def __init__(self, parmString):
        tokens = self._tokenize(parmString)
        signature, values = self._getSignature(tokens)
        if signature == "S":
            self.exceptionType = None
            self.exceptionMsg = values[0]
            self.value = None
        elif signature == "N:S":
            self.exceptionType = values[0]
            self.exceptionMsg = values[2]
            self.value = None
        elif signature == "S,S":
            self.exceptionType = None
            self.exceptionMsg = values[0]
            self.value = values[2]
        elif signature in ("N", "N,S", "N,S,S", "N,,S",
                           ",S", ",S,S", ",,S"):
            i = 0
            i, self.exceptionType = self._nextParm(i, values)
            i, self.exceptionMsg = self._nextParm(i, values)
            i, self.value = self._nextParm(i, values)
        else:
            raise FitException("exceptionCHinvalidSignature", signature)

    def _tokenize(self, parmString):
        reader = TokenizeReader(parmString)
        tokens = [x for x in tokenize.generate_tokens(reader)]
        return tokens

    def _getTokenName(self, tokNum):
        return token.tok_name[tokNum]

    def _getSignature(self, tokens):
        signature = []
        values = []
        for aToken in tokens:
            tokName = self._getTokenName(aToken[0])
            value = aToken[1]
            if tokName == "NAME":
                signature.append("N")
                values.append(value)
            elif tokName == "STRING":
                signature.append("S")
                values.append(value[1:-1])
            elif tokName == "OP":
                signature.append(value)
                values.append(value)
            elif tokName == "ERRORTOKEN":
                raise FitException("exceptionCHParseError", aToken[2][1])
            elif tokName in ("NEWLINE", "ENDMARKER"):
                pass
            else:
                raise FitException("exceptionCHUnknownToken", tokName)
        return "".join(signature), values

    def _nextParm(self, i, values):
        if i >= len(values):
            return i, None
        if values[i] == ",":
            i += 1
            return i, None
        next = i + 2
        return next, values[i]

# Accessor Classes ###############################

class AccessorBaseClass(object):
    name = None # name bound to
    protocol = None # Type Adapter protocol object
    adapter = None # Type Adapter object
    target = None # Instance containing the field, method or property
    metaData = {}
    fixture = None # Fixture this adapter belongs to

    defaultCellHandlerList = CellHandlers(
        [CHT[x] for x in ["Blank", "Null", "NumericRange", "Symbol"]])
    cellHandlerList = CellHandlers(defaultCellHandlerList)

    def __init__(self, instance, name, owner, targetClass):
        self.name = name
        self.target = instance # !!! dependency injection in RowFixture.
        self.fixture = owner or instance
        self.targetClass = targetClass
        self._parseExit = DefaultParseExit()

    value = None

    def get(self):
        return self.value

    def set(self, anObject):
        self.value = anObject
        return    

    def invoke(self):
        return self.value

    def parseAndSet(self, cell): # returns CheckResult_XXX
        if self._isExceptionHandlingRequested(cell.text(), errorKwd=False):
            return self._handleErrorInParseCell(cell)
        else:
            result = None
            try:
                result = self.parse(cell)
                self.set(result)
                exc = CheckResult_ParseOK()
            except Exception, e:
                exc = CheckResult_Exception(e)
            exc.parseResult = result
            exc.value = result
            return exc
    
    def parse(self, cell):
        result, value = self.runCellHandlerParseList(cell)
        res = result.lower()[0]
        if res == "o":
            return value
        self._raiseError(res, value)
        cell = firstNonNone(value, cell)

        ret, value = self._parseExit(self.getEditedText(cell))
        ret = ret[0].lower()
        if ret == "o":
            return value
        self._raiseError(ret, value)
        cell = firstNonNone(value, cell)

        return self.protocol.parse(cell)

    def getEditedText(self, cell):
        if isinstance(cell, Parse):
            return cell.text()
        return cell

    def _handleErrorInParseCell(self, cell):
        text = cell.text()
        numFailLevels, newText = self._unwrapFailRequests(text)
        excClass, excMsg, excValue = self._extractExceptionParms(newText)
        if excValue is None:
            raise FitException("parseExceptionCHNoValue")
        newCell = Parse(tag="td", body=excValue)
        result = None
        try:
            result = self.parse(newCell)
            self.set(result)
            exc = CheckResult_Wrong(str(result),
                               escape=True) # was shouldEscape, comes from nowhere.
        except Exception, e:
            exc = CheckResult_Exception(e)
            exc = self._checkTypeAndMsg(exc, excClass, excMsg)
        checkResult = self._applyFailLevels(numFailLevels, exc)
        checkResult.parseResult = result
        checkResult.value = result
        return checkResult

    def _raiseError(self, resultCode, message):
        if resultCode != "e":
            return
        raise FitException("aMessage", message)

    def runCellHandlerParseList(self, cell):
        for handler in self.cellHandlerList:
            ch = handler.handlerClass()
            if ch.canParse:
                result, value = ch.parse(cell, self)
                if not result.lower().startswith("n"):
                    return result, value
        return NEXT, None
    
    def equals(self, cell, obj):
        if not isinstance(cell, (Parse, types.StringTypes)):
            return self.protocol.equals(cell, obj)
        # !!! these two are only used by FitLibrary, so we bypass cell handlers
        #     next release we make cell handlers use Cell Access.
        if self.protocol.protocolName in ("RawString", "CellAccess"): #pragma: no cover
            return self.protocol.equals(cell, obj)
        result, value = self.runCellHandlerCheckList(cell, obj)
        lc = result.lower()[0]
        self._raiseError(lc, value)
        if lc == "o":
            return value
        return self.protocol.equals(cell, obj)
    stringEquals = equals

    def runCellHandlerCheckList(self, cell, obj):
        for handler in self.cellHandlerList:
            ch = handler.handlerClass()
            if ch.canCheck:
                result, value = ch.check(cell, obj, self)
                if not result.lower().startswith("n"):
                    return result, value
        return NEXT, None

    def toString(self, o, cell=None):
        return self.protocol.toString(o, cell)

    def setParseExit(self, executable):
        self._parseExit = executable

    def clearParseExit(self):        
        self._parseExit = DefaultParseExit()

    def hasCellHandler(self, handlerName):
        for handler in self.cellHandlerList:
            if handlerName == handler.name:
                return True
        return False

# check routine moved here from Fixture

    def check(self, cell):
        text = cell.text()
        if text == "":
            checkResult = self.handleBlankCell(cell)
        elif (self._isExceptionHandlingRequested(text)):
            checkResult = self._handleErrorInCell(cell)
        else:
            checkResult = self._compareCellToResult(cell)
        return checkResult

    exceptionRE = re.compile(r"^exception\[(.*?)\]$", re.I)
    def _isExceptionHandlingRequested(self, text, errorKwd=True):
        failLevels, newText = self._unwrapFailRequests(text)
        if newText == "error" and errorKwd is True:
            return True
        match = self.exceptionRE.match(newText)
        if match is None:
            return False
        return True

    failRE = re.compile(r"^Fail\[(.*?)\]$")
    def _unwrapFailRequests(self, text):
        failLevels = 0
        newText = text
        while True:
            isFail, newText = self._unwrapOneFailLevel(newText)
            if not isFail:
                break
            failLevels += 1
        return failLevels, newText

    def _unwrapOneFailLevel(self, text):
        match = self.failRE.match(text)
        if match is None:
            return False, text
        return True, match.group(1)

    def _compareCellToResult(self, cell):
        shouldEscape = (self.protocol.protocolName != "CellAccess")
        numFailLevels, newText = self._unwrapFailRequests(cell.text())
        result = None
        try:
            result = self.get()
            if numFailLevels != 0:
                newCell = Parse(tag="td", body=newText)
            else:
                newCell = cell
            equalsResult = self.equals(newCell, result)
            if equalsResult:
                checkResult = CheckResult_Right()
            else:
                checkResult = CheckResult_Wrong(self.toString(result),
                                   escape=shouldEscape)
        except Exception, e:
            checkResult = CheckResult_Exception(e)
        self._applyFailLevels(numFailLevels, checkResult)
        checkResult.value = result
        return checkResult

    def handleBlankCell(self, unused='cell'):
        # ??? should cell be here?
        result = None
        try:
            result = self.get()
            checkResult = CheckResult_Info(self.toString(result))
        except Exception:
            checkResult = CheckResult_Info("error")
        checkResult.value = result
        return checkResult

    def _handleErrorInCell(self, cell):
        numFailLevels, newText = self._unwrapFailRequests(cell.text())
        result = None
        if newText == "error":
            aBool, exc, result = self._doGet()
            if exc is not None:
                exc = CheckResult_Right()
        else:
            excClass, excMsg, excValue = self._extractExceptionParms(newText)
            if excValue is None:
                aBool, exc, result = self._doGet()
                if exc is not None:
                    exc = self._checkTypeAndMsg(exc, excClass, excMsg)
            else: 
                newCell = Parse(tag="td", body=excValue)
                try:
                    result = self.get()
                    self.equals(newCell, result)
                    exc = CheckResult_Wrong(self.toString(result),
                                       escape="shouldEscape")
                except Exception, e:
                    exc = CheckResult_Exception(e)
                    exc = self._checkTypeAndMsg(exc, excClass, excMsg)
        if exc is None:
            exc = CheckResult_Wrong(result)
        checkResult = self._applyFailLevels(numFailLevels, exc)
        checkResult.value = result
        return checkResult

    def _extractExceptionParms(self, cellText):
        parsed = ExceptionCellHandlerParameters(cellText[10:-1])
        return parsed.exceptionType, parsed.exceptionMsg, parsed.value

##    def _handleErrorKeyword(self, cell):
##        result = None
##        try:
##            result = self.get()
##            result = self.parse(result)
##        except Exception, e:
##            exc = CheckResult_Exception(e)
##            exc.value = result
##            return True, exc, None
##        return False, None, result

    def _doGet(self):
        result = None
        try:
            result = self.get()
        except Exception, e:
            return True, CheckResult_Exception(e), None
        return False, None, result

##    def _doGetCheck(self, text):
##        cell = Parse(tag="td", body=text) # should probably encode it.
##        result = None
##        try:
##            result = self.get()
##            result = self.equals(cell, result)
##        except Exception, e:
##            exc = CheckResult_Exception(e)
##            exc.value = result
##            return True, exc, None
##        return False, None, result

    def _checkTypeAndMsg(self, exc, excClass, excMsg):
        result = exc
        if excClass is not None and exc.exc.__class__.__name__ != excClass:
            exc.__class__ = CheckResult_ExceptionWrong
        elif (excMsg is not None and exc.actual != excMsg):
            exc.__class__ = CheckResult_ExceptionWrong
        else:
            result = CheckResult_Right()
        return result

    _failChanges = {"CheckResult_Wrong": (CheckResult_Right, CheckResult_Wrong),
                    "CheckResult_Right": (CheckResult_Wrong, CheckResult_Right),
                    "CheckResult_Exception": (CheckResult_ExceptionRight,
                                              CheckResult_ExceptionWrong),
                    "CheckResult_ExceptionWrong": (CheckResult_ExceptionRight,
                                              CheckResult_ExceptionWrong),
                    "CheckResult_ExceptionRight": (CheckResult_ExceptionWrong,
                                              CheckResult_ExceptionRight),
                    }

    def _applyFailLevels(self, numLevels, exc):
        quo, rem = divmod(numLevels, 2)
        changes = self._failChanges[exc.__class__.__name__]
        if numLevels == 0:
            pass
        elif rem == 1:
            exc.__class__ = changes[0]
        else:
            exc.__class__ = changes[1]
        return exc


## -------- end of check routine -------------------
## -------- end of base class ----------------------

# This also supports properties!
class FieldAccessor(AccessorBaseClass):
    def get(self):
        return getattr(self.target, self.name)

    def set(self, value):
        setattr(self.target, self.name, value)

    def invoke(self):
        raise FitException, ("InvokeField",)

class GetMethodAccessor(AccessorBaseClass):
    def __init__(self, instance, name, owner, targetClass):
        super(GetMethodAccessor, self).__init__(instance, name, owner, targetClass)
        self.method = getattr(targetClass, name) # !!! unbound method!
        
    def get(self):
        return self.method(self.target)

    def set(self, unused='value'):
        raise FitException("CallSetOnGetter")

    def invoke(self):
        return self.method(self.target)

class GetMethodDefaultAccessor(GetMethodAccessor):
    def equals(self, cell, obj):
        adapter = _acquireAdapterForType(self.target, self.name,
                                         obj, self.metaData)
        if adapter is not None:
            protocol = getProtocolFor(adapter)
            self.protocol = protocol
            self.adapter = adapter
        self.__class__ = GetMethodAccessor
        return super(GetMethodAccessor, self).equals(cell, obj)
        

class SetMethodAccessor(AccessorBaseClass):
    def __init__(self, instance, name, owner, targetClass):
        super(SetMethodAccessor, self).__init__(instance, name, owner, targetClass)
        self.method = getattr(targetClass, name)
        
    def get(self):
        raise FitException("CallGetOnSetter")

    def set(self, value):
        return self.method(self.target, value)

    def invoke(self):
        raise FitException("InvokeASetter")

## Default Parse Exit

class DefaultParseExit(object):
    def __call__(self, unused='value'):
        return "continue", None
