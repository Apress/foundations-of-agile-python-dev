# FlowFixture and DoFixture from FitLibrary
#legalStuff rm03-05 jr05-06
# Original version Contains code developed by Rick Mugridge.
# University of Auckland, NZ. Copyright 2003-2005 Rick Mugridge.
# Released under the terms of the General Public License (GPL), Release 2.1 or later
# See license.txt for terms and disclaimer of all warrenties and liability.
# changes Copyright 2005-2006 John H. Roth Jr.
# Last updated for Release 0.8a1
#endLegalStuff

# These two Java classes have been included in the same
# module to avoid clutter. Notice that Python does not have
# abstract classes; FlowFixture is a real class.

try:
    False
except:
    False = 0
    True = 1

import inspect
# import new
import types
import traceback
import sys

from fit.Fixture import Fixture, NullFixtureListener # test!
from fit.Parse import Parse
from fit.Summary import Summary
from fit import TypeAdapter
from fit.FitException import FitException
from fit.Utilities import em
from fitLib import ExtendedCamelCase
from fitLib.FitLibraryExceptions import IgnoredException
from fitLib.FitLibraryFixture import FitLibraryFixture
from fitLib.MethodTarget import MethodTarget

##import fit.graphic.ObjectDotGraphic;

# ----------------------- FlowFixture ---------------------------
# An abstract superclass of DoFixture which defines the top-level
# interpretation of tables.

class FlowFixture(FitLibraryFixture):
    _typeDict = {"stopOnError": "Boolean"}
    stopOnError = False

    # Method overrides Fixture
    def interpretTables(self, tables):
        # this section handles the first table. Fixture has already
        # loaded the fixture named in the first line; rather obviously
        # or we wouldn't be here.
        # Now we need to handle the rest of the table, if there is a
        # rest of the table.
        if tables.parts.more is not None:
            # Interpret any actions in the rest of the table:
            restOfTable = Parse(tag="table", body="", parts=tables.parts)
            self.doTable(restOfTable)
            self.listener.tableFinished(tables)

        # This handles all remaining tables.
        tables = tables.more
        while tables is not None and not (
                self.stopOnError and self.problem(self.counts)):
            self.interpretTable(tables)
            self.listener.tableFinished(tables)
            tables = tables.more
        self.listener.tablesFinished(self.counts)

    # Done for each table            
    def interpretTable(self, table):
        try:
            if self.wasFixtureByName(table): # subfixture invoked?
                return
            row = table.parts
            if self.doRow(row):
                pass
            else:
                self.doTable(table)
        except Exception, e:
            self.exception(table.at(0, 0, 0), e)

    # This is intended to be overridded by DoFixture
    # XXX FixMe - this is a virtual method, it won't work as written.
    def doRow(self, row):
        __pychecker__ = "no-classattr"
        cells = row.parts
        result = self.interpretCells(cells)
        if isinstance(result, Fixture):
            self.interpretTableWithFixture(row.next, result)
            return True
        return False

    def interpretTableWithFixture(self, table, fixture):
        self.injectDependenciesIntoFixture(fixture, table)
        fixture.doTable(table)

    def wasFixtureByName(self, table):
        try:
            fixture = self.getLinkedFixtureWithArgs(table)
        except Exception:
            return False
        fixture.doTable(table)
        return True

    _typeDict["showSummary.types"] = [None]
    def showSummary(self):
        return Summary()

    # if (stopOnError) then we don't continue intepreting a table
    # if there's been a problem
    def isStopOnError(self):
        return self.stopOnError
    def setStopOnError(self, stopOnError):
        self.stopOnError = stopOnError

    def problem(self, official):
        return official.wrong + official.exceptions > 0

# ------------ End of FlowFixture ------------------ #

# ----------------- DoFixture ---------------------- #

# A fixture that takes control and interprets all of the
# tables in a test as a single entity, thus avoiding
# inter-fixture communication problems and also sometimes avoiding
# having to declare a fixture at the start of each table.

#/** An alternative to fit.ActionFixture
#	@author rick mugridge, july 2003
#	Updated April 2004 to include not/reject actions.
#	Updated August 2004 to handle properties and
#	  to automap Object to DoFixture, List, etc to ArrayFixture, etc.
#  * 
#  * See the FixtureFixture specifications for examples

class DoFixture(FlowFixture):
    _typeDict = {}
    systemUnderTest = None
    map = {}
    passedOntoOtherFixture = False

    def __init__(self, sut=None):
        Fixture.__init__(self) # first superclass with an init method.
        self.setSystemUnderTest(sut)
        self.map = {}
        
# Set the systemUnderTest. 
# If an action can't be satisfied by the DoFixture, the systemUnderTest
# is tried instead. Thus the DoFixture is an adapter with methods just
# when they're needed.

    def setSystemUnderTest(self, sut):
        self.systemUnderTest = sut

# ---------------- Special Actions ----------------------
# 0.8a2 - to be a special action, the method object must be marked
#         with the fitLibSpecialAction = True attribute.

#	/** Check that the result of the action in the rest of the row matches
#	 *  the expected value in the last cell of the row.

    def check(self, cells):
        # FIXME do something with a table to eliminate the check override
        cells = cells.more
        if cells is None:
            raise FitException, "MissingCellsFailureException"
        args = cells.size() - 2
        expectedCell = cells.at(args + 1)
        target = self.findMethodByActionName(cells, args)
        target.invokeAndCheck(cells.more, expectedCell)
    check.fitLibSpecialAction = True

#	/** Add a cell containing the result of the rest of the row.
#	 *  HTML is not altered, so it can be viewed directly.

    def show(self, cells):
        cells = cells.more
        if cells is None:
            raise FitException, "MissingCellsFailureException"
        args = cells.size() - 1
        target = self.findMethodByActionName(cells, args)
        adapter = target.resultTypeAdapter
        try:
            result = self.callGivenMethod(target, cells)
            lastCell = self.addCell(cells)
            if isinstance(result, types.StringTypes):
                lastCell.body = str(result)
            else:
                lastCell.body = adapter.toString(result, lastCell)
        except IgnoredException:
            pass
    show.fitLibSpecialAction = True


##	/** Add a cell containing the result of the rest of the row,
##	 *  shown as a Dot graphic.
##	 */
##	public void showDot(Parse cells) throws Exception {
##		cells = cells.more;
##		if (cells is None)
##			throw new MissingCellsFailureException();
##		int args = cells.size() - 1;
##		MethodTarget target = findMethodByActionName(cells, args);
##		Class resultType = target.getReturnType();
##		TypeAdapter adapter = LibraryTypeAdapter.onResult(this, ObjectDotGraphic.class);
##		try:
##			Object result = callGivenMethod(target, cells);
##			addCell(cells, adapter.toString(new ObjectDotGraphic(result)));
##		} catch (IgnoredException e) { // No result, so ignore
##		}
##	}

    def addCell(self, cells):
        newCell = Parse(tag="td")
        cells.last().more = newCell
        return newCell

#	/** Checks that the action in the rest of the row succeeds.
#	 *  o If a boolean is returned, it must be true.
#	 *  o For other result types, no exception should be thrown.

    def ensure(self, cells):
        ensureCell = cells
        cells = cells.more
        if cells is None:
            raise FitException, "MissingCellsFailureException"
        target = self.findMethodByActionName(cells, cells.size()-1)
        try:
            result = self.callGivenMethod(target, cells)
            print "in DoFixture.ensure result: '%s'" % result
            if result is True:
                self.right(ensureCell)
            else:
                self.wrong(ensureCell)
        except IgnoredException:
            pass
        except Exception, ex:
            self.exception(ensureCell, ex, color="wrong")
    ensure.fitLibSpecialAction = True


#	/** Checks that the action in the rest of the row fails.
#	 *  o If a boolean is returned, it must be false.
#	 *  o For other result types, an exception should be thrown.
#	 */
    def reject(self, cells):
        notCell = cells
        cells = cells.more
        if cells is None:
            raise FitException, "MissingCellsFailureException"
        target = self.findMethodByActionName(cells,cells.size()-1)
        try:
            result = self.callGivenMethod(target, cells)
            if result not in (True, False):
                self.exception(notCell,"Was not rejected")
            elif result is True:
                self.wrong(notCell)
            else:
                self.right(notCell)
        except IgnoredException:
            pass
        except Exception:
            self.right(notCell)
    not_ = reject
    reject.fitLibSpecialAction = True


#	/** The rest of the row is ignored. 

    def note(self, cells):
        pass
    note.fitLibSpecialAction = True


#	/** An experimental feature, which may be changed or removed. */
#   XXX need to do something about results which are not fixtures.
    def name(self, cells):
        # |name|method|args|
        cells = cells.more
        if cells is None or cells.more is None:
            raise FitException, "MissingCellsFailureException"
        name = cells.text()
        methodCells = cells.more
        args = methodCells.size() - 1
        target = self.findMethodByActionName(methodCells, args)
        result = target.invokeAndWrap(methodCells.more)
        if isinstance(result, Fixture):
            self.map[name] = result
            self.right(cells)
        else:
            raise FitException, ("FitFailureException", "Must return an object.")
    name.fitLibSpecialAction = True


#	/** An experimental feature, which may be changed or removed. */
# Note - test dof13, to allow name and use of domain objects, isn't
#        working in the distributed system.
    def use(self, cells):
        # |use|name|of|name|...
        cells = cells.more
        if cells is None:
            raise FitException, "MissingCellsFailureException"
        name = cells.text()
        anObject = self.getMapper(cells.more).map.get(name)
        if isinstance(anObject, Fixture):
            return anObject
        raise FitException, ("FitFailureException", "Unknown name: "+name)
    use.fitLibSpecialAction = True

    def getMapper(self, cells):
        if cells is None:
            return self
        if cells.text() != "of":
            raise FitException, ("FitFailureException", "Missing 'of'.")
        if cells.more is not None:
            cells = cells.more
            name = cells.text()
            anObject = self.getMapper(cells.more).map.get(name)
            if isinstance(anObject, Fixture):
                return anObject
            raise FitException, ("FitFailureException", "Unknown name: "+name)
        raise FitException, ("FitFailureException", "Missing name.")
# -------------- End of experimental feature --------------------

#	/** To allow for DoFixture to be used without writing any fixtures.

    def start(self, cells):
        cells = cells.more
        if cells is None:
            raise FitException, "MissingCellsFailureException"
        if cells.more != None:
            raise FitException, "ExtraCellsFailureException"
        className = cells.text()
        try:
            theClass = self.loadFixture(className, shouldBeAFixture = False)
        except Exception:
            raise FitException, ("FitFailureException", "Unknown class: "+className)
        
        try:
            self.setSystemUnderTest(theClass())
        except Exception:
            raise FitException, ("FitFailureException", "Class " + className + " failed to initialize")
    start.fitLibSpecialAction = True

#	/** To allow for a CalculateFixture to be used for the rest of the table.
#	 *  This is intended for use for teaching, where no fixtures need to be
#	 *  written.
    _typeDict["calculate.types"] = [None]
    def calculate(self):
        fixture = self.loadFixture("fitLib.CalculateFixture")
        return fixture(self.systemUnderTest)
    calculate.fitLibSpecialAction = True

# ---------------- End of Special Actions -----------------------    


# ------------ Navigation Code overrides FlowFixture ------------
    def doRows(self, rows):
        while rows != None and not self.passedOntoOtherFixture:
            more = rows.more
            self.doRow(rows)
            rows = more

#    /** Note that doCells() and doCell() are not called at all.

    def doRow(self, row):
        try:
            self.passedOntoOtherFixture = False
            firstCell = row.parts
            target, result = self._interpretCells(firstCell)
            if isinstance(result, Fixture):
                restOfTable = Parse(tag="table", body="", parts=row)
                self.interpretTableWithFixture(restOfTable, result)
                self.passedOntoOtherFixture = True
            elif isinstance(target, types.BooleanType):
                pass
            elif target.getReturnType() == "$SUT":
                if result is None:
                    self.wrong(firstCell)
                if isinstance(result, types.StringTypes):
                    self.wrong(firstCell, result)
                else:
                    self.setSystemUnderTest(result)
            return self.passedOntoOtherFixture
        except Exception, ex:
            self.exception(row, ex)
            return False

    # the split is because interpretCells is called from FlowFixture,
    # and I wanted to preserve the interface.
    def interpretCells(self, cells):
        target, result = self._interpretCells(cells)
        return result

    def _interpretCells(self, cells):        
        try:
            handled, result = self.calledParseMethod(cells)
            if handled:
                return True, result
            target = self.findMethodByActionName(cells, cells.size()-1)
            result = target.invokeAndWrap(cells.more)
            if isinstance(result, types.BooleanType):
                target.color(cells, result)
            return target, result
        except IgnoredException:
            pass
        except Exception, ex:
            self.exception(cells, ex)
        return False, None

#	------ END CODE FOR FLOW ---------------

    # this finds and invokes a method that's built into DoFixture if one exists,
    def calledParseMethod(self, cells):
        name = cells.text()
        if name == "":
            return False, None
        name = self.camel(name) # shouldn't be any need to camelCase it.
        parseMethod = self._extractParseMethod(name)
        if parseMethod is None:
            return False, None
        result = parseMethod(cells)
        return True, result

    # !!! implementer's note. The current implementation, using
    #     getattr, supports the "special method" tests where it
    #     lets DoFixture subclasses define command methods.

    def _extractParseMethod(self, name):
        if name == "not": # hack for use of Python keyword
            name = "not_"
        method = getattr(self, name, None)
        if method is None:
            return
        if not inspect.ismethod(method):
            return
        numArgs = method.im_func.func_code.co_argcount
        if numArgs != 2: # (self, cells)
            return
        if hasattr(method, "fitLibSpecialAction") is False:
            return
        if method.fitLibSpecialAction is not True:
            return
        return method

#	/** Is overridden in subclass SequenceFixture to process arguments differently
    def findMethodByActionName(self, cells, numArgs):
        parms = numArgs / 2 + 1
        args = (numArgs + 1) / 2
        name = cells.text()
        i = 1
        while (i < parms):
            name += " " + cells.at(i*2).text()
            i += 1
        target = self.findMethod(ExtendedCamelCase.camel(name), args)
        target.setEverySecond(True)
        return target

    def findMethod(self, name, args):
        print "in DoFixture.findMethod self.systemUnderTest: %s" % (
            self.systemUnderTest)
        __pychecker__ = 'no-returnvalues' # last statement throws exception.
        sut = self.systemUnderTest or self
        try:
            result = MethodTarget(sut, args, self, name)
        except:
            traceback.print_exc(None, sys.stdout)
            self._findMethodException(name, args)
        if result is not None:
            return result
        self._findMethodException(name, args)

    def _findMethodException(self, name, args):
        plural = "s"
        if args == 1:
            plural = ""
        raise FitException, ("FitFailureException", 'Unknown: "%s" with %s argument%s'
                                  % (name, args, plural))

    def callGivenMethod(self, target, rowCells):
        return target.invoke(rowCells.more)

    def tearDown(self):
        self.systemUnderTest = None
