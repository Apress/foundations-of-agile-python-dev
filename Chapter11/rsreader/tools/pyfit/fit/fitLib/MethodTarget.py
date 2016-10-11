# MethodTarget from FitLibrary
#legalStuff rm03-05 jr05
# Original version Contains code developed by Rick Mugridge.
# University of Auckland, NZ. Copyright 2003-2005 Rick Mugridge.
# Released under the terms of the General Public License (GPL), Release 2.1 or later
# See license.txt for terms and disclaimer of all warrenties and liability.
# changes Copyright 2005 John H. Roth Jr.
# Last updated for Release 0.8a1
#endLegalStuff

try:
    False
except:
    False = 0
    True = 1

#import copy
import inspect
import types
import traceback
import sys
from fit.Fixture import Fixture
from fit.Parse import Parse
from fit import TypeAdapter
from fit import taProtocol as taPro
from fit.FitException import FitException
from fit.Utilities import em
from fitLib.FitLibraryExceptions import FitFailureException, IgnoredException

##import fit.graphic.ObjectDotGraphic;

class MethodTarget(object):
    # Obsolete static constructor, maintained for compatability
    # Everything is now done in the standard constructor.
    def findSpecificMethod(name, numArgs, subject, fixture):
        return MethodTarget(subject, numArgs, fixture, name)
    findSpecificMethod = staticmethod(findSpecificMethod)

    def __init__(self, subject, numArgs, fixture, name):
        self.subject = subject # instance with the method
        self.fixture = fixture # fixture instance, may be same as subject
        self.name = name       # method name, needed for metadata lookup
        self.repeatString = None
        self.exceptionString = None
        self.resultFromInvoke = None
        self.resultTypeAdapter = None
        self.everySecond = False
        self.method, self.field, self.metaData = self._getNamedMethod(
            name, numArgs, fixture, subject)
        if self.metaData is None:
            raise Exception, "Unable to find metaData for '%s'" % name
        self.args = [None] * numArgs # filled in by _collectCell
        self.parameterAdapters = [None] * (numArgs + 1)
        self.types = [None] * (numArgs + 1)
        self.resultTypeAdapter = self._getResultTypeAdapter(
            subject, name, self.metaData[0])
        self.parameterAdapters[0] = self.resultTypeAdapter
        i = 1
        while i < len(self.parameterAdapters):
            self.parameterAdapters[i] = self._getTypeAdapter(
                subject, name, self.metaData[i])
            i += 1

        i = 0
        while i < len(self.types):
            parm = self.metaData[i]
            if isinstance(parm, types.StringTypes):
                result = parm
            elif isinstance(parm, types.DictType):
                result = parm.get(name)
            elif parm is None:
                result = None
            else:
                result = "?"
            self.types[i] = result
            i += 1
        self.returnType = self.types[0]

    # returns [method, field, metadata]
    def _getNamedMethod(self, name, numArgs, fixture, subject):
        # look in the subject first.
        if fixture != subject:
            result = self._searchForNamedMethod(name, numArgs, subject)
            if result is not None:
                return result
        # now look in the fixture
        result = self._searchForNamedMethod(name, numArgs, fixture)
        if result is None:
            return [None, None, None]
        return result

    def _searchForNamedMethod(self, name, numArgs, subject):
        __pychecker__ = 'no-returnvalues' # XXX fix None return
        mro = getattr(subject.__class__, "__mro__", None)
        mro = mro or [subject.__class__]
        for aClass in mro:
            typeDict = aClass.__dict__.get("_typeDict")
            if typeDict is None:
                continue
            name = self._renameTo(typeDict, name, numArgs)
            oldType = typeDict.get(name)
            newType = typeDict.get(name + ".types")
            if not(oldType or newType):
                continue
            method = getattr(subject, name, None)
            if method is None and oldType is not None and newType is None:
                return [None, True, [oldType]] # must be a field
            methodType = self._examineMethodType(method)
            if methodType in ("instancemethod", "staticmethod"):
                actualNumArgs = method.func_code.co_argcount
                if methodType == "staticmethod":
                    actualNumArgs += 1 # account for return parameter
                if newType and len(newType) == actualNumArgs:
                    return [method, False, newType]
                if not newType and oldType and actualNumArgs < 2:
                    return [method, False, oldType]
                raise Exception, "Method and Metadata mismatch"
            if methodType == "property":
                if newType:
                    return (method, True, newType)
                else:
                    return (method, True, [oldType, oldType])
            if methodType == "field":
                return (method, True, [oldType])
        return None

    def _renameTo(self, typeDict, name, numArgs):
        newName = typeDict.get(name + ".RenameTo")
        if type(newName) == types.DictType:
            newName = newName.get(numArgs)
        if newName is not None:
            return newName
        return name

    def _examineMethodType(self, method):
        if method is None:
            return "None"
        if inspect.ismethod(method):
            return "instancemethod"
        if inspect.isfunction(method):
            return "staticmethod"
        getter = getattr(method, "__get__", None)
        setter = getattr(method, "__set__", None)
        if getter and setter:
            return "property"
        return "field"

    # two special cases for results only.
    # ??? should we provide a special type adapter for void?
    def _getResultTypeAdapter(self, subject, name, metaData):
        if metaData is None:
            result = None
        elif isinstance(metaData, types.StringTypes) and metaData[0] == "$":
            result = None
        else:
            result = self._getTypeAdapter(subject, name, metaData)
        return result

    def _getTypeAdapter(self, subject, name, metaData):
        if type(metaData) != type({}):
            metaData = {name: metaData}
        result = self._getTypeAdapterFromDict(subject, name, metaData)
        return result

    def _getTypeAdapterFromDict(self, subject, name, metaDataDict):
        # ??? what was typeThing all about? should we change the on. call?
#        typeThing = metaDataDict.get(name)
        return TypeAdapter.on(subject, name, metaDataDict,
                              accClass=TypeAdapter.AccessorBaseClass)
##        result = TypeAdapter._acquireTypeAdapter(subject, name, typeThing,
##                                             metaDataDict)
##        # get accessor - we want one that scans the cell handler list.
##        protocol = taPro.getProtocolFor(result)
##        accessor = TypeAdapter.AccessorBaseClass(protocol, subject,
##                                name, None, subject.__class__)
##        return accessor

# --------- end of init subroutines. Whew! -------------------

    def isValid(self):
        return self.method is not None

    def getReturnType(self):
        return self.types[0]

    def getParameterTypes(self):
        return self.types[1:]

    # parameter is either a parse cell, or an array of parameters
    # to be passed to the method. This is because the Java version
    # used an overloaded method.
    def invoke(self, cellsOrArgs):
        if isinstance(cellsOrArgs, Parse):
            return self.invokeWithCells(cellsOrArgs)
        return self.invokeWithArgs(cellsOrArgs)

    def invokeWithCells(self, cells):
        try:
            if  self.everySecond:
                self.collectEverySecondCell(cells)
            else:
                self.collectAllCells(cells)
        except Exception, e:
            self.fixture.exception(cells, e)
            raise IgnoredException
        return self.invokeWithArgs(self.args)
    
    def invokeWithArgs(self, args):
        if args is None:
            args = []
        if self.field:
            self.resultFromInvoke = getattr(self.subject, self.name)
        else:
            self.resultFromInvoke = self.method(*args)
        return self.resultFromInvoke

    def collectAllCells(self, cells):
        argNo = 0
        while (argNo) < len(self.args):
            self._collectCell(cells, argNo)
            cells = cells.more
            argNo += 1

    def collectEverySecondCell(self, cells):
        argNo = 0
        while (argNo) < len(self.args):
            self._collectCell(cells, argNo)
            cells = cells.more
            if cells != None:
                cells = cells.more
            argNo += 1
            
    def _collectCell(self, cell, argNo):
        text = cell.text()
        try:
            if text != self.repeatString:
                self.args[argNo] = (
                    self.parameterAdapters[argNo + 1].parse(cell)) # was text
        except Exception, e:
            self.fixture.exception(cell, e)
            raise e

    def invokeAndCheck(self, cells, expectedCell):
        result = None
        exceptionExpected = (self.exceptionString is not None and
                             self.exceptionString == expectedCell.text())
        try:
            result = self.invokeWithCells(cells)
            if exceptionExpected:
                self.fixture.wrong(expectedCell)
                return
        except IgnoredException:
            return
        except FitFailureException, e:
            # Temporary to see what's happening
#            self.fixture.exception(expectedCell, e)
            return
        except Exception, e:
            if exceptionExpected:
                self.fixture.right(expectedCell)
            else:
                self.fixture.exception(expectedCell, e)
            return

        self.checkResult(expectedCell, result)

    # TODO exception[] cell handler (including Fail[] wrappers).
    # XXX this mess needs to be cleaned up - the string compare should
    #     be the fallback, not the first thing tried.
    def checkResult(self, expectedCell, result):
        try:
            if self.resultTypeAdapter is None:
                raise FitFailureException, "No value provided"
            toString = self.resultTypeAdapter.toString(result, expectedCell)
#            toString = self.resultTypeAdapter.toString(result, result)
            expectedWithoutTags = expectedCell.text()
            if toString == expectedWithoutTags:
                self.fixture.right(expectedCell)
            elif toString == expectedCell.body:
                self.fixture.right(expectedCell)
            elif self.resultTypeAdapter.equals(expectedCell, result):
                self.fixture.right(expectedCell)
            else:
                # ??? what was this about? Old type adapter attempt,
                #     doesn't work now.
                shouldEscape = getattr(self.resultTypeAdapter.adapter,
                                 "cellParse", False)
                self.fixture.wrong(expectedCell, toString,
                                   escape=shouldEscape)
        except Exception, e:
            self.fixture.exception(expectedCell, e)

    def color(self, cells, right):
        while cells is not None:
            if right:
                self.fixture.right(cells)
            else:
                self.fixture.wrong(cells)
            if not self.everySecond:
                break
            cells = cells.more
            if cells is not None:
                cells = cells.more

#    /** Defines the Strings that signifies that the value in the row above is
#     *  to be used again. Eg, it could be set to "" or to '"

    def setRepeatAndExceptionString(self, repeatString, exceptionString):
        self.repeatString = repeatString
        self.exceptionString = exceptionString

    def setEverySecond(self, everySecond):
        self.everySecond = everySecond

# This is the routine that decides whether the
# result is a fixture. It also wraps a fixture
# object around certain types of collections
# to automatically invoke RowFixture and friends.

# invokeAndWrap either returns a fixture or some
# other object. If it returns a fixture, the caller
# invokes it for the remainder of the current table.

    def invokeAndWrap(self, cells):
        result = self.invokeWithCells(cells)
#        theClass = self.subject.__class__
        if isinstance(result, Fixture):
            return result
        elif self.returnType == "$SUT":
            return result
        # 2005/04/02 - new hook to display module.
        # interface is a tuple of (collection, nameList, typeDict)
        elif self.returnType == "$Display":
            return self._getFixture("fitLib.DisplayUtility")(*result)
        elif self._ListAdaptersDict.get(self.returnType) is not None:
            # interface is a tuple of (collection, typeDict)
            fixtureName = self._ListAdaptersDict.get(self.returnType)
            return self._getFixture(fixtureName)(*result)
        elif hasattr(result, "_typeDict"):
            return self._getFixture("fitLib.DoFixture")(result)
        return result

    _ListAdaptersDict = {"$Array": "fitLib.ArrayFixture",
                         "$Row": "fitLib.ParamRowFixture",
                         "$Set": "fitLib.SetFixture",
                         "$Subset": "fitLib.SubsetFixture",
                         }

    # The indirection here is because otherwise we would have
    # a very nasty import loop between this module and doFixture
    def _getFixture(self, fixtureName):
        result = self._fixtureNameDict.get(fixtureName)
        if result is not None:
            return result
        result = self.fixture.loadFixture(fixtureName)
        self._fixtureNameDict[fixtureName] = result
        return result

    _fixtureNameDict = {}    
