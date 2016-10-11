# Fixture, part of Core Fit
#legalStuff cc02 sm02 om04 rm05 jr03-06
# Original Java version Copyright 2002 Cunningham and Cunningham, Inc.
# Released under the terms of the General Public License (GPL), Release 2.1 or later
# See license.txt for terms and disclaimer of all warrenties and liability.
# Original translation to Python Copyright 2002 Simon Michael
# Contains changes copyright 2004 by Object Mentor, Inc.
# Contains code developed by Rick Mugridge.
# University of Auckland, NZ. Copyright 2005 Rick Mugridge.
# changes Copyright 2003-2006 John H. Roth Jr.
# Last updated for Release 0.8a1
#endLegalStuff

import sys
import time
import traceback
import types

from fit.Counts import Counts
from FitException import FitException
from fit import FitGlobal
from fit.FitNesseExceptions import FitFailureException
from fit.FixtureLoader import FixtureLoader
from fit import Variations
from fit.Parse import Parse
from fit.Utilities import em

try:
    False
except: #pragma: no cover
    True = 1
    False = 0

class RunTime(object):
    def getSystemTime(self):
        return time.time()
    currentTime = property(getSystemTime)

    # method for unit tests - see test harness for usage
    def getMockTime(self):
        return self.mockTime

    mockTime = 0.0 # set by unit tests, pychecker complains about absense    
        
    def __init__(self):
        self.start = self.currentTime
        self.elapsed = 0.0

    def __str__(self):
        # in integers representing hundredths of a second
        self.elapsed = int((self.currentTime - self.start) * 100)
        hours = self.d(360000)
        minutes = self.d(6000)
        seconds = self.d(100)
        hundredths = self.elapsed
        if hours > 0:
            return "%s:%02d:%02d" % (hours, minutes, seconds)
        else:
            return "%s:%02d.%02d" % (minutes, seconds, hundredths)

    # depreciated as part of removal of javisms where convenient.
    def toString(self):
        return str(self)

    def d(self, scale):
        report, self.elapsed = divmod(self.elapsed, scale)
        return report

# for the real implemetation of this, see FitServerImplementation
class NullFixtureListener:
    def tablesStarted(self, tables):
        return None

    def tableFinished(self, tables):
        return None

    def tablesFinished(self, counts):
        return None

    def getPageName(self): #pragma: no cover
        return ""

class Fixture(object):
    # These labels are in the process of being moved to Variations.
    # They are still here until several fixtures that use them for
    # checking are fixed to call FitGlobal.annotationStyleVariation
    # to do the checking
    greenColor = "cfffcf"
    redColor = "ffcfcf"
    grayColor = "efefef"
    yellowColor = "ffffcf"
    labelColor = "c08080"
    grayLabelColor = "808080"
    greenLabelColor = "80c080"

    def __init__(self):
        # most of these are updated by dependency injection either
        # in one of the runners or in the recursive invocation in doTables.
        self.counts = Counts()
        self.summary = {}
        self.args = []
        self.argCells = []
#        self._symbols = {}
        self.listener = NullFixtureListener()
        self.fixtureLoader = FixtureLoader()

    ## Fixture Loader ##################################

    def loadFixture(self, pathToClass, shouldBeAFixture = True):
        "load requested fixture - return the class object"
        result = self.fixtureLoader.loadFixture(pathToClass,
                                                shouldBeAFixture)
        return result

    # !!! The following are proxy methods which are intended for
    #     use by the runners, the Import fixture and the unit test
    #     suite. They are not general use methods. Either the proxies
    #     or the base methods may be removed at any time.

    # this is called from the runners and the unit test suite    
    def clearFixtureRenameTable(self):
        self.fixtureLoader.clearFixtureRenameTable()

##    # this is called from the runners to load a table from a file.
##    def loadFixtureRenamesFromFile(self, fileName):
##        self.fixtureLoader.loadFixtureRenamesFromFile(fileName)

##    # this is called from the runners to load a table.
##    def loadFixtureRenameTable(self, aList):
##        self.fixtureLoader.loadFixtureRenameTable(aList)

    # this is called from the Import fixture
    def addRenameToRenameTable(self, alias, originalPath):
        self.fixtureLoader.addRenameToRenameTable(alias, originalPath)

    # this is called from the Import fixture
    def rememberPackage(self, packageName):
        self.fixtureLoader.rememberPackage(packageName)

    # this is called from the MiscTest unit tests for Import
    def clearRememberedPackageTable(self):
        self.fixtureLoader.clearRememberedPackageTable()

    # !!! end of internal use proxy methods.        

    ## Major Table Traversal ##########################

    # First table processing unrolled for doFixture from FitLibrary.
    # changes copyright 2004 Rick Mugridge, University of Auckland, NZ.
    # This is only invoked under the first instance of Fixture. It cannot
    # be overridden by a subclass unless the subclass is invoked at the
    # top level by runner.
    def doTables(self, tables):
        self.listener.tablesStarted(tables)
        self.summary["run date"] = time.ctime(time.time())
        self.summary["run elapsed time"] = RunTime()
        Variations.returnVariation()
        if tables.tag.lower() == "<wiki>":
            tables = tables.parts
        # Rick's unrolled process begins here...
        if tables is not None:
            heading = self.fixtureName(tables)
            if heading is not None:
                try:
                    fixture = self.getLinkedFixtureWithArgs(tables)
                    fixture.interpretTables(tables)
                except Exception, e:
                    self.exception(heading, e)
                    self.listener.tableFinished(tables)
                    self._interpretFollowingTables(tables)

    # extracted because it's used by the Fit 1.1 specification tests
    def fixtureName(self, table):                    
        return table.at(0,0,0)

    # This is only executed under the recursively invoked instance
    # of Fixture.
    def interpretTables(self, tables):
        try:
            self.getArgsForTable(tables) # get them again for the new fixture object
            self.doTable(tables)
            self.listener.tableFinished(tables)
        except Exception, ex:
            self.exception(tables.at(0, 0, 0), ex)
            return
        self._interpretFollowingTables(tables)

    # This is the rest of the table traversal loop that was
    # unrolled to expose the first table to subfixtures.
    def _interpretFollowingTables(self, tables):
        tables = tables.more;
        while tables:
            heading = self.fixtureName(tables)
#            heading = tables.at(0,0,0)
            if heading:
                try:
                    fixture = self.getLinkedFixtureWithArgs(tables)
                    fixture.doTable(tables)
                except Exception, e:
                    self.exception(heading, e)
            self.listener.tableFinished(tables)
            tables = tables.more
        self.listener.tablesFinished(self.counts)

    def getLinkedFixtureWithArgs(self, tables):
        header = self.fixtureName(tables).text()
        fixture = self.loadFixture(header)()
        self.injectDependenciesIntoFixture(fixture, tables)
        return fixture

    def injectDependenciesIntoFixture(self, fixture, tables):
        fixture.counts = self.counts
        fixture.summary = self.summary
        fixture.getArgsForTable(tables)
        fixture.listener = self.listener
        fixture.fixtureLoader = self.fixtureLoader
#        fixture._symbols = self._symbols
        return

    def getArgsForTable(self, table):
        args = []
        argCells = []
        cell = table.parts.parts
        while cell is not None:
            argCells.append(cell)
            args.append(cell.text())
            cell = cell.more
        if len(args) > 0:
            del args[0]
        self.args = args
        self.argCells = argCells
        return args

    ## Row and Cell Traversal ###########################

    def doTable(self, table):
        shouldTakeExits = self._extractMetaData(".takeSetupExits")
        if shouldTakeExits is None:
            shouldTakeExits = FitGlobal.appConfigInterface(
                "fixtureSetUpExit", table)
        if shouldTakeExits is not False:
            self.setUpFixture(table.parts)
        self.doRows(table.parts.more)
        if shouldTakeExits is not False:
            self.tearDownFixture()

    def doRows(self, rows):
        while rows:
            more = rows.more
            self.doRow(rows)
            rows = more

    def doRow(self, row):
        self.doCells(row.parts)

    def doCells(self, cells):
        i = 0
        while cells:
            try:
                self.doCell(cells, i)
            except Exception, e:
                self.exception(cells, e)
            i = i + 1
            cells=cells.more

    def doCell(self, cell, unused="columnNumber"):
        self.ignore(cell)

    def setUpFixture(self, unused='firstRow'):
        return None

    def tearDownFixture(self):
        return None

    ## Annotation ##############################

# The actual routines for modifying the parse nodes
# have been moved to Parse. These routines now invoke
# the routines in Parse. Some of them also have the
# tabulate function, the rest are simply proxies.

# Most of the actual annotation decisions are now made
# in the CheckResults hierarchy in the TypeAdapter module.

# The routines in this set all use the routines in
# Parse to do the actual annotation, and also do the
# tabulate function by adding into the current count
# object. They are only useful for fixtures that don't
# use the TypeAdapter check and parseAndSet calls.

    def right(self, cell, actual=None):
        cell.right(actual)
        self.counts.right += 1

    def wrong(self, cell, actual=None, escape=True):
        cell.wrong(actual, escape)
        self.counts.wrong += 1

    def ignore(self, cell):
        cell.ignore()
        self.counts.ignores += 1

    # New in 1.1
    def error(self, cell, msg):
        cell.error(msg)
        self.counts.exceptions += 1

# exception is the major annotation routine that is
# used extensively throughout the code.

    def exception(self, cell, exception, color="ex"):
        doTrace = 1
        if isinstance(exception, types.StringTypes):
            isExc = 1
            doTrace = 0
            message = exception
        elif (isinstance(exception, FitException)):
            isExc, doTrace, message = exception.getMeaningfulMessage()
            if doTrace == 2:
                return
            if isExc == 0 or color == "wrong":
                self.wrong(cell, message)
                return
        elif (isinstance(exception, FitFailureException)):
            isExc = 1
            doTrace = 0
            message = exception.args

        if doTrace == 0:
            cell.addToBody("<hr>%s" % message)
        else:
            exType, val, tb = sys.exc_info()
            err = "".join(traceback.format_exception(exType, val, tb))
            cell.addToBody(FitGlobal.annotationStyleVariation.stackTrace(err))
        if color == "wrong":
            self.wrong(cell)
            return
        cell.addToTag(FitGlobal.annotationStyleVariation.exception())
        self.counts.exceptions += 1
    
    ## Utility ##################################

    # !!! duplication of function and field name!!!
    # !!! should use str(self.counts) instead of this.
##    def _counts(self) :
##        return self.counts.toString()

    # This set of routines are all supporting methods
    # which proxy the calls on the Parse cell, or which
    # bypass the parse cell entirely and access the raw
    # strategy objects that determine the text to add
    # to the cell. The later should be avoided at all
    # costs; they will most likely be removed in 0.9.

    def addGreenLabel(self, cell, actual):
        if actual is None: return
        cell.addGreenLabel(actual)

    def addRedLabel(self, cell, actual, escape=True):
        if actual is None: return
        cell.addRedLabel(actual, escape)

    # the variant of this routine that calls self.gray
    # will be removed in 0.9.
    def info(self, cell, msg = None):
        if isinstance(cell, Parse):
            cell.info(msg)
        else:
            return self.gray(self.escape(cell))

# Routines to be removed in 0.9!

    def label (self, aString):
        return FitGlobal.annotationStyleVariation.label(aString)

    def gray (self, aString):
        return FitGlobal.annotationStyleVariation.gray(aString)

    def greenlabel(self, aString):
        return FitGlobal.annotationStyleVariation.greenlabel(aString)

    # This duplicates code in Parse. 
    def escape(self, aString):
        aString = aString.replace("&", "&amp;");
        aString = aString.replace("<", "&lt;");
        aString = aString.replace("  ", " &nbsp;")
        aString = aString.replace("\r\n", "<br />")
#        aString = aString.replace("\n\r", "<br />")
        aString = aString.replace("\r", "<br />")
        aString = aString.replace("\n", "<br />")
        return aString

# end of routines to be removed in 0.9

    # camelCase routine. Thanks to Rick Mugridge whose ExtendedCamel
    # routine pointed out several problems with the original camelCase
    # (batch) and gracefulName (FitNesse) routines.

    def camel(self, name, kind=None):
        kind = self._extractMetaData(".useToMapLabel") or kind
        return FitGlobal.annotationStyleVariation.mapLabel(name, kind)

    gracefulName = camel
    mapLabel = camel

    def _extractMetaData(self, key):
        result = self._camelKindFromTargetClass(key)
        if result is None:
            result = self._camelKindFromFixture(key)
        return result

    def _camelKindFromFixture(self, key):
        try:
            kind = self._typeDict[key]
            return kind
        except:
            pass
        return None

    def _camelKindFromTargetClass(self, key):
        try:
            obj = self.getTargetClass()
            kind = obj._typeDict[key]
            return kind
        except:
            pass
        return None

    # The fixture's parse exit used to be here. The original intent
    # was to provide a mechanism where type adapter functionality
    # could be included directly in an application fixture. PyFit's
    # metadata facility eliminates the need for this functionality.

    # Moved the core of the check() routine to AdapterBase in TypeAdapter,
    # where it really belongs. The version in AdapterBase returns a
    # CheckResult object, which encapsulates the correct annotation
    # and tabulation routines for the specific result, and also makes
    # it difficult to support.
    
    def check(self, cell, adapter):
        checkResult = adapter.check(cell)
        checkResult.annotateCell(cell)
        checkResult.tabulateResult(self.counts)
        return checkResult

    # New in 0.8
    def parseAndSet(self, cell, adapter):
        checkResult = adapter.parseAndSet(cell)
        checkResult.annotateCell(cell)
        checkResult.tabulateResult(self.counts)
        return checkResult

# More utility methods.
           
    def getArgs(self):
        return self.args

    def getArgCells(self):
        return self.argCells

    def setSymbol(self, symbol, value):
#        self._symbols[symbol] = value
        FitGlobal.testLevelSymbols[symbol] = value
        return None

    def getSymbol(self, symbol):
        if FitGlobal.testLevelSymbols.has_key(symbol):
            return FitGlobal.testLevelSymbols.get(symbol)
        return FitGlobal.RunLevelSymbols[symbol]

    def isFitNesse(self):
        return FitGlobal.Environment == "FitNesse"

# The following two items are to satisfy pychecker.

    def getTargetClass(self):
        raise Exception

    _typeDict = {}
