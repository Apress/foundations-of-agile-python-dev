# Cell Handler Tests
#legalStuff jr05
# Copyright 2005 John H. Roth Jr.
# Released under the terms of the General Public License (GPL), Release 2.1 or later
# See license.txt for terms and disclaimer of all warrenties and liability.
# Last updated for Release 0.8a1
#endLegalStuff

from unittest import makeSuite, TestCase, main
from fit.CellHandlers import *
from fit.CellHandlerInspector import CellHandlerInspector
from fit.FitException import FitException
from fit.Fixture import Fixture
from fit.InitEnvironment import FG, setupFitGlobalForTests
from fit.Parse import Parse
from fit import taTable
from fit.TypeAdapter import ExceptionCellHandlerParameters
from fit import TypeAdapter
import fit.taProtocol as taPro
from tests.TestCommon import FitTestCommon

try:
    False
except:
    True = 1
    False = 0

def makeCellHandlerTest():
    suite = makeSuite(TestCellHandlers, 'test')
    suite.addTests([SpecifyExceptionCellHandlerParameterObject(x) for x in [
        "exceptionTypeOnly",
        "exceptionMessageOnly",
        "oldFormatTypeAndMessage",
        "newFormatTypeAndMessage",
        "typeAndValue",
        "messageAndValue",
        ]])
    suite.addTests([makeSuite(TestCellHandlerInspector, "should"),
                    makeSuite(SpecifyCellHandlerWrapper, "should"),
                    makeSuite(SpecifyListOfCellHandlersContainer, "should"),
                    ])
    return suite

OK = "ok"
NEXT = "next"
ERROR = "error"

class TestCellHandlers(TestCase):
    def setUp(self):
        print '%s %s' % (self.id(), self.shortDescription())
        setupFitGlobalForTests("Batch")
        CellHandler._testInit()

    def tearDown(self):
        setupFitGlobalForTests("Batch")
        CellHandler._testInit()

    def testThatTypeAdapterIsAcceptableToCellHandler(self):
        class ACellHandler(CellHandlerBase):
            includeList = ["Larry", "Moe", "Curly"]
            excludeList = ["Laurel", "Hardy"]
        obj = CellHandler(ACellHandler)
        handler = obj.handlerClass()
        assert handler.isTypeAdapterApplicable("Laurel") is False
        assert handler.isTypeAdapterApplicable("Larry") is True
        assert handler.isTypeAdapterApplicable("Cleese") is None

    def testThatTypeAdapterIsAcceptableIfNothingSpecified(self):
        class ACellHandler(CellHandlerBase):
            pass
        obj = CellHandler(ACellHandler)
        handler = obj.handlerClass()
        assert handler.isTypeAdapterApplicable("Laurel") is None
        assert handler.isTypeAdapterApplicable("Larry") is None
        assert handler.isTypeAdapterApplicable("Cleese") is None



    def testBlankHandlerParse(self):
        h = BlankCellHandler()
        assert h.parse("blank", None) == (OK, "")
        assert h.parse("fubar", None) == (NEXT, None)

    def testBlankCellHandlerParseWithCell(self):        
        h = BlankCellHandler()
        cell = Parse(tag="td", body="blank")
        assert h.parse(cell, None) == (OK, "")
        cell.body = "fubar"
        assert h.parse(cell, None) == (NEXT, None)

    def testExceptionIfInvalidInputType(self):
        h = BlankCellHandler()
        self.assertRaises(FitException, h.parse, 3.14, None)

    def testBlankHandlerCheck(self):
        h = BlankCellHandler()
        assert h.check("blank", "", None) == (OK, True)

    def testAsisCellHandlerParse(self):
        h = AsisCellHandler()
        assert h.parse("asis[ hello ]", None) == (OK, " hello ")

    def testAsisWithParseCell(self):
        h = AsisCellHandler()
        cell = Parse(tag="td", body="asis[ hello ]")
        assert h.parse(cell, None) == (OK, " hello ")

    def testAsisParseNoMatch(self):
        h = AsisCellHandler()
        assert h.parse("fee fie fo fum", None) == (NEXT, None)

    def testAsisExceptionIfInvalidInputType(self):
        h = AsisCellHandler()
        self.assertRaises(FitException, h.parse, 3.14, None)

    def testAsisCellHandlerCheck(self):
        h = AsisCellHandler()
        assert h.check("asis[ goodbye ]", " goodbye ", None) == (OK, True)

    def testAsisCheckNoMatch(self):
        h = AsisCellHandler()
        assert h.check("fee fie fo fum", " fubar ", None) == (NEXT, None)

    def testAsisCheckNoMatch2(self):
        h = AsisCellHandler()
        assert h.check("asis[ goodbye ]", " fubar ", None) == (OK, False)

    def testNumericRangeParse(self):
        h = NumericRangeCellHandler()
        assert h.parse("40..60", None) == (NEXT, None)

    def testNumericRangeCheck(self):
        h = NumericRangeCellHandler()
        assert h.check("40 .. 60", 50,
                       AccMock(IntMock())) == (OK, True)
        assert h.check("40 .. 60", 70,
                       AccMock(IntMock())) == (OK, False)
        
    def testNumericRangeCheck2(self):
        # bug reported 2005/04/25 by jenisys815.
        h = NumericRangeCellHandler()
        assert h.check("..60", 50,
                       AccMock(IntMock())) == (OK, True)
        assert h.check("40 .. ", 50,
                       AccMock(IntMock())) == (OK, True)
        assert h.check(" .. 60", 70,
                       AccMock(IntMock())) == (OK, False)
        assert h.check("40 .. ", 30,
                       AccMock(IntMock())) == (OK, False)
        assert h.check(" .. ", 45, 
                       AccMock(IntMock())) == (NEXT, None)

    def testNumericRangeCheck3(self):
        # more special cases...
        h = NumericRangeCellHandler()
        assert h.check("fe ..60", 50,
                       AccMock(IntMock())) == (NEXT, None)
        assert h.check("40 ..fi ", 50,
                       AccMock(IntMock())) == (NEXT, None)
        assert h.check("fo .. fum ", 45, 
                       AccMock(IntMock())) == (NEXT, None)

    def testSubstringParse(self):
        h = SubstringCellHandler()
        assert h.parse("startswith[spam]", None) == (NEXT, None)

    def testSubstringCheck(self):
        h = SubstringCellHandler()
        assert (h.check("fubar", "snafu", None) == (NEXT, None))
        assert (h.check("startswith[spam]", "spamandeggs", None) ==
                (OK, True))
        assert (h.check("startswith[spam]", "spandex", None) == (OK, False))
        assert (h.check("endswith[eggs]", "spamandeggs", None) ==
                (OK, True))
        assert (h.check("endswith[eggs]", "spandex", None) == (OK, False))
        assert (h.check("contains[and]", "spamandeggs", None) == (OK, True))
        assert (h.check("contains[and]", "spicknspan", None) == (OK, False))

    def testSymbolHandler(self):
        h = SymbolCellHandler()
        checkCell = Parse(tag="td", body="&lt;&lt;sym")
        parseCell = Parse(tag="td", body="sym&lt;&lt;")
        callbacks = AccMock(IntMock())
        result = h.check(checkCell, "spam", callbacks)
        assert result == (OK, True)
        assert callbacks.fixture.getSymbol("sym") == "spam"
        assert checkCell.text().endswith(" = spam")
        result = h.parse(parseCell, callbacks)
        assert result == (OK, "spam")
        assert parseCell.text().endswith(" = spam")

    def testSymbolHandlerWithNoSymbol(self):
        h = SymbolCellHandler()
        checkCell = Parse(tag="td", body="sym")
        parseCell = Parse(tag="td", body="sym")
        callbacks = AccMock(IntMock())
        result = h.check(checkCell, "spam", callbacks)
        assert result == (NEXT, None)
        self.failUnlessRaises(KeyError, callbacks.fixture.getSymbol, "sym")
        result = h.parse(parseCell, callbacks)
        assert result == (NEXT, None)

class IntMock(object):
    def parse(self, str):
        return int(str)

    def toString(self, obj):
        return str(obj)

class FixMock(object):
    _symbols = {}
    def __init__(self):
        self._symbols = {}

    def getSymbol(self, symbol):
        return self._symbols[symbol]

    def setSymbol(self, symbol, value):
        self._symbols[symbol] = value
        return

    def gray(self, aString):
        return "<span>%s</span>" % aString

class AccMock(object):
    adapter = None
    fixture = None
    def __init__(self, adapter):
        self.fixture = FixMock() # Fixture
        self.adapter = adapter
        self.protocol = taPro.BasicProtocol(adapter)

class SpecifyExceptionCellHandlerParameterObject(TestCase):
    def setUp(self):
        print '%s %s' % (self.id(), self.shortDescription())

    def tearDown(self):
        pass

    def doIt(self, input, xType, xMsg, value):
        obj = ExceptionCellHandlerParameters(input)
        assert obj.exceptionType == xType, (
            "expected exception type: '%s' actual: '%s'" %
            (xType, obj.exceptionType))
        assert obj.exceptionMsg == xMsg, (
            "expected exception message: '%s' actual: '%s'" %
            (xType, obj.exceptionMsg))
        assert obj.value == value, ("expected value: '%s' actual: '%s'" %
            (xType, obj.value))

    def exceptionTypeOnly(self):
        self.doIt("Fubar", "Fubar", None, None)

    def exceptionMessageOnly(self):
        self.doIt("'oops'", None, "oops", None)

    def oldFormatTypeAndMessage(self):
        self.doIt("Fubar: 'oops'", "Fubar", "oops", None)

    def newFormatTypeAndMessage(self):
        self.doIt("Fubar, 'oops'", "Fubar", "oops", None)

    def typeAndValue(self):
        self.doIt("Fubar, ,'oops'", "Fubar", None, "oops")

    def messageAndValue(self):
        self.doIt("'snafu', 'oops'", None, "snafu", "oops")

class TestCellHandlerInspector(TestCase):
    def shouldCreateListOfCellHandlers(self):
        table = Parse("<table><tr><td>fit.CellHandlerInspector"
                      "</td></tr></table>")
        obj = CellHandlerInspector()
        obj.doTable(table)
        assert table.parts.size() == 5

class SpecifyCellHandlerWrapper(FitTestCommon):
    def setUp(self):
        print '%s %s' % (self.id(), self.shortDescription())
        setupFitGlobalForTests("Batch")
        CellHandler._testInit()

    def tearDown(self):
        setupFitGlobalForTests("Batch")
        CellHandler._testInit()

    def shouldAcceptBuiltinName(self):
        obj = CellHandler("Blank")
        assert obj.name == "Blank"
        assert obj.handlerClass == taTable.cellHandlerTable["Blank"]

    def shouldAcceptBuiltinClass(self):
        obj = CellHandler(taTable.cellHandlerTable["Blank"])
        assert obj.name == "Blank"
        assert obj.handlerClass == taTable.cellHandlerTable["Blank"]

    def shouldRejectApplicationNameIfNoExit(self):
        obj = CellHandler("@fubar")
        assert obj.name == "@fubar"
        assert obj.handlerClass is None

    def shouldReturnInvalidHandlerObjectIfIncorrectBuiltin(self):
        obj = CellHandler("Foo")
        assert not obj.isValid()

    def shouldReturnSameHandlerIfParameterIsAHandlerObject(self):
        obj1 = CellHandler("Asis")
        obj2 = CellHandler(obj1)
        assert obj1 is obj2

    def shouldRejectNameOfBuiltin(self):
        class RejectCellHandler(object):
            def mapCellHandler(self, chName):
                return False
        self._installApplicationExit(RejectCellHandler)
        obj = CellHandler("String")
        assert obj.name == "String"
        assert obj.handlerClass is False
        assert not obj.isValid()

    def shouldBeAbleToRejectClass(self):
        class FooCellHandler(object):
            pass
        class RejectCellHandler(object):
            def mapCellHandler(self, chName):
                return False
        self._installApplicationExit(RejectCellHandler)
        obj = CellHandler(FooCellHandler)
        assert obj.name is False
        assert obj.handlerClass is FooCellHandler
        assert not obj.isValid()

    def shouldAcceptApplicationNameIfClassReturned(self):
        class FooCellHandler(object):
            pass
        class AcceptCellHandler(object):
            def mapCellHandler(self, chName):
                return FooCellHandler
        self._installApplicationExit(AcceptCellHandler)
        obj = CellHandler("@foo")
        assert obj.name == "@foo"
        assert obj.handlerClass == FooCellHandler

    def shouldUseClassNameIfNonstandardClassSupplied(self):        
        class FooCellHandler(object):
            pass
        obj = CellHandler(FooCellHandler)
        assert obj.name == "FooCellHandler"
        assert obj.handlerClass == FooCellHandler

    def shouldRememberNameFromPreviousCall(self):        
        class FooCellHandler(object):
            pass
        class BarCellHandler(object):
            pass
        obj = CellHandler(FooCellHandler)
        assert obj.name == "FooCellHandler"
        assert obj.handlerClass == FooCellHandler
        obj = CellHandler(BarCellHandler)
        assert obj.name == "BarCellHandler"
        assert obj.handlerClass == BarCellHandler
        obj = CellHandler(FooCellHandler)
        assert obj.name == "FooCellHandler"
        assert obj.handlerClass == FooCellHandler

    def shouldRememberNameForObjectFromExit(self):        
        class FooCellHandler(object):
            pass
        class BarCellHandler(object):
            pass
        class AcceptCellHandler(object):
            def mapCellHandler(self, chName):
                return FooCellHandler
        self._installApplicationExit(AcceptCellHandler)
        fooObj = CellHandler("@Foo")
        assert fooObj.name == "@Foo"
        assert fooObj.handlerClass == FooCellHandler
        obj = CellHandler(BarCellHandler)
        assert obj.name == "BarCellHandler"
        assert obj.handlerClass == BarCellHandler
        obj = CellHandler(fooObj.handlerClass)
        assert obj.name == "@Foo"
        assert obj.handlerClass == FooCellHandler

    def shouldAcceptValueEqualityAsEqual(self):
        obj1 = CellHandler("Blank")
        obj2 = CellHandler("Blank")
        assert obj1 is not obj2
        assert obj1 == obj2

    def shouldNotAcceptInvalidWrapperAsEqual(self):
        obj1 = CellHandler("fubar")
        obj2 = CellHandler("fubar")
        assert obj1 is not obj2
        assert not (obj1 == obj2)
        assert not (obj2 == obj1)

class SpecifyListOfCellHandlersContainer(FitTestCommon):
    def setUp(self):
        print '%s %s' % (self.id(), self.shortDescription())
        setupFitGlobalForTests("Batch")
        CellHandler._testInit()

    def tearDown(self):
        setupFitGlobalForTests("Batch")
        CellHandler._testInit()

    def shouldAddCellHandlersToList(self):
        obj = CellHandlers()
        obj.addHandler(CellHandler("Blank"))
        obj.addHandler(CellHandler("Asis"))
        assert len(obj) == 2

    def shouldntAddDuplicatesToList(self):
        obj = CellHandlers()
        obj.addHandler(CellHandler("Blank"))
        obj.addHandler(CellHandler("Blank"))
        assert len(obj) == 1

    def shouldAddHandlerByName(self):
        obj = CellHandlers()
        obj.addHandler("Blank")
        assert len(obj) == 1

    def shouldRemoveHandlerFromList(self):
        obj = CellHandlers()
        obj.addHandler(CellHandler("Blank"))
        obj.addHandler(CellHandler("Asis"))
        assert len(obj) == 2
        obj.removeHandler(CellHandler("Blank"))
        assert len(obj) == 1

    def shouldRemoveHandlerByNameFromList(self):
        obj = CellHandlers()
        obj.addHandler(CellHandler("Blank"))
        obj.addHandler(CellHandler("Asis"))
        assert len(obj) == 2
        obj.removeHandler("Blank")
        assert len(obj) == 1

    def shouldAddListOfHandlersToList(self):
        obj = CellHandlers()
        obj.addHandlers(["Blank", "Asis"])
        assert len(obj) == 2

    def shouldRemoveHandlersInListFromList(self):
        obj = CellHandlers()
        obj.addHandlers(["Blank", "Asis", "Null"])
        assert len(obj) == 3
        obj.removeHandlers(["Null", "Asis"])
        assert len(obj) == 1

    def shouldNotAddAnInvalidHandler(self):
        obj = CellHandlers()
        obj.addHandlers(["Blank", "Foo", "Asis"])
        assert len(obj) == 2

    def shouldReturnItemByIndex(self):
        obj = CellHandlers()
        obj.addHandlers(["Blank", "Asis"])
        assert obj[0] == CellHandler("Blank")
        assert obj[1] == CellHandler("Asis")
        self.assertRaises(IndexError, obj.__getitem__, 2)

    def shouldRaiseTypeErrorIfIndexIsNotAnIngeger(self):        
        obj = CellHandlers()
        obj.addHandlers(["Blank", "Asis"])
        assert obj[0] == CellHandler("Blank")
        assert obj[1] == CellHandler("Asis")
        self.assertRaises(TypeError, obj.__getitem__, "0")

    def shouldInitializeFromAList(self):
        obj = CellHandlers(["Blank", "Asis"])
        assert len(obj) == 2
                           

if __name__ == '__main__':
    main(defaultTest='makeCellHandlerTest')
