# test module for Fixture
#legalStuff jr04-06
# Copyright 2004-2006 John H. Roth Jr.
# Released under the terms of the General Public License (GPL), Release 2.1 or later
# See license.txt for terms and disclaimer of all warrenties and liability.
# Last updated for Release 0.8a1
#endLegalStuff

# A lot of the unit tests for Fixture are in FrameworkTest. That hasn't
# been updated since the initial conversion.

import types
from unittest import makeSuite, TestCase, main
from fit.InitEnvironment import FG, setupFitGlobalForTests
from fit.FitNesseExceptions import FitFailureException
from fit.Fixture import Fixture, RunTime, NullFixtureListener
from fit.Options import Options
from fit.Parse import Parse
from fit.SiteOptions import BatchBase
from fit.Utilities import em
from fit import Variations
from tests.TestCommon import FitTestCommon

try:
    False
except:
    True = 1
    False = 0

def makeFixtureTest():
    theSuite = makeSuite(TestFixtureInStandardsMode, 'test')
    theSuite.addTests([makeSuite(TestRunTime, 'test'),
                       makeSuite(SpecifyWhichCamelToUse, "should"),
                       makeSuite(DrillDownToDoCell, "should"),
                       makeSuite(ErrorOnFirstTable, "should"),
                       makeSuite(TestSymbols, "should"),
                       makeSuite(TestFitNesseTest, "should"),
                       makeSuite(SpecifySetupAndTeardownExits, "should"),
                       ])
    return theSuite

class TestRunTime(TestCase):
    def setUp(self):
        print '%s %s' % (self.id(), self.shortDescription())
        self.savedTimeProperty = RunTime.currentTime
        RunTime.currentTime = property(RunTime.getMockTime)
        RunTime.mockTime = 1.0
        self.runTime = RunTime()

    def tearDown(self):
        RunTime.currentTime = self.savedTimeProperty

    def testCurrentTime(self):
        assert str(self.runTime) == "0:00.00"
        assert self.runTime.toString() == "0:00.00"

    def testTenMinutes(self):
        RunTime.mockTime = 601.0
        assert str(self.runTime) == "10:00.00"
        assert self.runTime.toString() == "10:00.00"

    def testOneHourAndTenMinutes(self):
        RunTime.mockTime = 1 * 3600.0 + 10 * 60.0 + 1.0
        assert str(self.runTime) == "1:10:00"
        assert self.runTime.toString() == "1:10:00"

class MockFixtureLoader(object):
    def __init__(self):
        self._fixtureTable = {}
    
    def loadFixture(self, pathToClass, unused='shouldBeAFixture = True'):
        result = self._fixtureTable.get(pathToClass)
        return result
    # !!! There are five other entry points which this mock does
    #     not support (yet).

class MockFixture1(Fixture):
    collector = {}
    def __init__(self):
        self.collector["inDoRow"] = False

    def doRow(self, cell):
        self.collector["inDoRow"] = True
        super(MockFixture1, self).doRow(cell)
    
    def doCell(self, cell, unused="columnNumber"):
        self.right(cell)

class MockDoFixture(MockFixture1):
    def interpretTables(self, firstTable):
        aTable = firstTable
        while aTable is not None:
            self.wrong(aTable.parts.parts, "test message")
            aTable = aTable.more

class MockDoExceptionFixture(MockFixture1):
    def interpretTables(self, firstTable):
        raise Exception, "test exception"

class MockDoExceptionFixture2(MockDoFixture):
    def interpretTables(self, firstTable):
        aTable = firstTable
        while aTable is not None:
            self.doTable(aTable)
            aTable = aTable.more
            
    def doTable(self, aTable):
        raise Exception, "test exception"

class MockDoTableExceptionFixture(Fixture):
    def doTable(self, aTable):
        raise Exception, "test exception"

class TestFixtureInStandardsMode(TestCase):
    def setUp(self):
        print '%s %s' % (self.id(), self.shortDescription())
        setupFitGlobalForTests("Batch", ["+e"])
        self.options = Options(["FileRunner", "+v", "+e", "foo", "bar"],
                               BatchBase.parmDict)
        self.fixture = Fixture()
        self.fixture.fixtureLoader = MockFixtureLoader()
        
    def tearDown(self):
        setupFitGlobalForTests("Batch")

    def setMockFixture(self, fixtureName, fixture):
        self.fixture.fixtureLoader._fixtureTable[fixtureName] = fixture

    def createParseTree(self, aString):
        lBracket = aString[0]
        rBracket = aString[1]
        cellSep = aString[2]
        restOfString = aString[3:]
        result = self._createTables(lBracket, rBracket, cellSep, restOfString)
        return result

    def _createTables(self, lBracket, rBracket, cellSep, aString):
        theRows, restOfString = self._createRows(lBracket, rBracket,
                                                 cellSep, aString[1:])
        nextTableBracket = restOfString.find(lBracket)
        if nextTableBracket == -1:
            nextTable = None
        else:
            nextTable = self._createTables(lBracket, rBracket, cellSep,
                                           restOfString[nextTableBracket:])
        return Parse(tag="table", parts=theRows, more=nextTable)
                                   
    def _createRows(self, lBracket, rBracket, cellSep, aString):
        firstRow, restOfString = self._createRow(lBracket, rBracket,
                                                 cellSep, aString[1:])
        lastRow = firstRow
        while True:
            nextRowIndex = restOfString.find(lBracket)
            endOfTableIndex = restOfString.find(rBracket)
            if nextRowIndex == -1 or nextRowIndex > endOfTableIndex:
                break
            nextRow, restOfString = self._createRow(lBracket, rBracket,
                                                 cellSep, restOfString[1:])
            lastRow.more = nextRow
            lastRow = nextRow
        return firstRow, restOfString[1:]

    def _createRow(self, unused, rBracket, cellSep, aString): # lBracket
        endOfRowIndex = aString.find(rBracket)
        beginningOfCellIndex = 0
        placeHolder = Parse(tag="td")
        lastCell = placeHolder
        while True:
            endOfCellIndex = aString.find(cellSep, beginningOfCellIndex)
            if endOfCellIndex == -1 or endOfCellIndex > endOfRowIndex:
                break
            nextCell = Parse(tag="td",
                    body=aString[beginningOfCellIndex:endOfCellIndex])
            beginningOfCellIndex = endOfCellIndex + 1
            lastCell.more = nextCell
            lastCell = nextCell
        nextCell = Parse(tag="td",
                         body=aString[beginningOfCellIndex:endOfRowIndex])
        lastCell.more = nextCell
        theRow = Parse(tag="tr", parts=placeHolder.more)
        return theRow, aString[endOfRowIndex+1:]

    def testDoRowNotInvokedForSingleRowTable(self):
        htmlTree = self.createParseTree("[]|[[test.fixture1]]")
        self.setMockFixture("test.fixture1", MockFixture1)
        self.fixture.doTables(htmlTree)
        assert MockFixture1.collector["inDoRow"] is False

    def testDoCellsInvokedForTwoRowTable(self):
        htmlTree = self.createParseTree("[]|[[test.fixture1][Hi There!]]")
        self.setMockFixture("test.fixture1", MockFixture1)
        self.fixture.doTables(htmlTree)
        resultHTML = str(htmlTree)
        assert resultHTML.find(Fixture.greenColor) > -1

    def testInterpretTablesOverridesStandardLoop(self):        
        htmlTree = self.createParseTree(
            "[]|[[test.interpretTablesFixture]]"
               "[[Hi There!]]"
               "[[Nice Day, isn't it?]]")
        self.setMockFixture("test.interpretTablesFixture", MockDoFixture)
        self.fixture.doTables(htmlTree)
        assert htmlTree.at(0, 0, 0).tag.find(Fixture.redColor) > -1
        assert htmlTree.at(1, 0, 0).tag.find(Fixture.redColor) > -1
        assert htmlTree.at(2, 0, 0).tag.find(Fixture.redColor) > -1

    tree1 = ("[]|[[test.interpretTablesFixture]]"
                "[[GreenFixture]]"
                "[[GreenFixture]]")

    def testExceptionInInterpretTablesOverride(self):        
        htmlTree = self.createParseTree(self.tree1)
        self.setMockFixture("interpretTablesFixture", MockDoExceptionFixture)
        self.setMockFixture("GreenFixture", MockFixture1)
        self.fixture.doTables(htmlTree)
        assert htmlTree.at(0, 0, 0).tag.find(Fixture.yellowColor) > -1
        assert htmlTree.at(1, 0, 0).tag.find("bgcolor") == -1
        assert htmlTree.at(2, 0, 0).tag.find("bgcolor") == -1

    def testExceptionInInterpretTablesDoTableOverride(self):        
        htmlTree = self.createParseTree(self.tree1)
        self.setMockFixture("interpretTablesFixture", MockDoExceptionFixture2)
        self.setMockFixture("GreenFixture", MockFixture1)
        self.fixture.doTables(htmlTree)
        assert htmlTree.at(0, 0, 0).tag.find(Fixture.yellowColor) > -1
        assert htmlTree.at(1, 0, 0).tag.find("bgcolor") == -1
        assert htmlTree.at(2, 0, 0).tag.find("bgcolor") == -1
        
    def testExceptionInInterpretTablesNoOverrideDoTable(self):        
        htmlTree = self.createParseTree(self.tree1)
        self.setMockFixture("interpretTablesFixture", MockDoTableExceptionFixture)
        self.setMockFixture("GreenFixture", MockFixture1)
        self.fixture.doTables(htmlTree)
        assert htmlTree.at(0, 0, 0).tag.find(Fixture.yellowColor) > -1
        assert htmlTree.at(1, 0, 0).tag.find("bgcolor") == -1
        assert htmlTree.at(2, 0, 0).tag.find("bgcolor") == -1

class MockCamelFixture(Fixture):
    _typeDict = {}

class MockCamelFixtureIndirect(Fixture):
    _typeDict = {}
    def getTargetClass(self):
        return MockCamelTargetClass

class MockCamelTargetClass(object):
    _typeDict = {}

class SpecifyWhichCamelToUse(TestCase):
    def setUp(self):
        print '%s %s' % (self.id(), self.shortDescription())
        setupFitGlobalForTests("Batch")
        self.options = Options(["FileRunner", "+v", "foo", "bar"],
                               BatchBase.parmDict)

    def tearDown(self):
        setupFitGlobalForTests("Batch")
        if MockCamelFixture._typeDict.get(".useToMapLabel"):
            del MockCamelFixture._typeDict[".useToMapLabel"]
        if MockCamelFixtureIndirect._typeDict.get(".useToMapLabel"):
            del MockCamelFixtureIndirect._typeDict[".useToMapLabel"]
        if MockCamelTargetClass._typeDict.get(".useToMapLabel"):
            del MockCamelTargetClass._typeDict[".useToMapLabel"]

    def mustReturn(self, obj, expected):        
        label = "3teen <4teen"
        result = obj.camel(label)
        assert result == expected, (
            "label: '%s' expected: '%s' actual: '%s'" %
            (label, expected, result))

    def shouldAcceptKindParameter(self):
        obj = MockCamelFixture()
        assert obj.camel("3teen <4teen", "camel") == "threeteen4teen"

    def shouldAcceptMapLabelFromFixture(self):
        obj = MockCamelFixture()
        obj._typeDict[".useToMapLabel"] = "gracefulNames"
        self.mustReturn(obj, "threeTeen4Teen")

    def shouldAcceptMapLabelFromOtherObject(self):
        obj = MockCamelFixtureIndirect()
        MockCamelTargetClass._typeDict[".useToMapLabel"] = "extended"
        self.mustReturn(obj, "threeteenLessThan4teen")

class MockNullFixture(Fixture):
    pass

class DrillDownToDoCell(TestCase):
    def shouldmarkCellsWithIgnored(self):
        __pychecker__ = "maxrefs=10"
        fix = MockNullFixture()
        table = Parse("<table><tr><td>fit.fitter</td></tr>"
                      "<tr><td>fe</td><td>fie</td><td>fo</td><td>fum</td></tr>"
                      "</table>")
        fix.doTable(table)
        row2 = table.parts.more
        assert row2.parts.tagIsIgnored()
        assert row2.parts.more.tagIsIgnored()
        assert row2.parts.more.more.tagIsIgnored()
        assert row2.parts.more.more.more.tagIsIgnored()
        assert table.parts.parts.tagIsNotAnnotated()

    def shouldAnnotateGreen(self):
        fix = MockNullFixture()
        cell = Parse(tag="td", body="Hi, There!")
        fix.addGreenLabel(cell, "Howdy")
        assert cell.body.find("Howdy") > -1
        assert cell.infoIsRight()

    def shouldAnnotateRed(self):
        fix = MockNullFixture()
        cell = Parse(tag="td", body="Oops.")
        fix.addRedLabel(cell, "Aw. Shucks.")
        assert cell.body.find("Aw. Shucks.") > -1
        assert cell.infoIsWrong()

    def shouldAnnotateOnErrorCall(self):
        fix = Fixture()
        cell = Parse(tag="td", body="Oops.")
        fix.error(cell, "Not good!")
        assert cell.body.find("Not good!") > -1
        assert cell.tagIsError()
        assert fix.counts.exceptions == 1

    def shouldHandleStringAsExceptionParameter(self):
        fix = Fixture()
        cell = Parse(tag="td", body="Oops.")
        fix.exception(cell, "What the heck?")
        assert cell.body.find("What the heck?") > -1
        assert cell.tagIsError()
        assert fix.counts.exceptions == 1

    def shouldBeAbleToColorExceptionAsWrong(self):
        fix = Fixture()
        cell = Parse(tag="td", body="Oops.")
        fix.exception(cell, "What the heck?", color="wrong")
        assert cell.body.find("What the heck?") > -1
        assert cell.tagIsWrong()
        assert fix.counts.wrong == 1

    def shouldCreateExpectedAndActualLabelInRed(self):
        fix = Fixture()
        cell = Parse(tag="td", body="Oops.")
        cell.addToBody(fix.label("It's dead, Jim."))
        assert cell.body.find("It's dead, Jim") > -1
        assert cell.infoIsWrong()

    def shouldCreateExpectedAndActualLabelInGreen(self):
        fix = Fixture()
        cell = Parse(tag="td", body="Oops.")
        cell.addToBody(fix.greenlabel("That's all right."))
        assert cell.body.find("That's all right") > -1
        assert cell.infoIsRight()

    def shouldAddTextOnInfo(self):        
        fix = Fixture()
        cell = Parse(tag="td", body="It's cold out there.")
        fix.info(cell, "Well, dress warmly.")
        assert cell.body.find("Well, dress warmly.") > -1
        assert cell.infoIsIgnored()

    def shouldGetTheInfoText(self):
        fix = Fixture()
        cell = Parse(tag="td", body="It's cold out there.")
        cell.addToBody(fix.info("Well, dress warmly."))
        assert cell.body.find("Well, dress warmly.") > -1
        assert cell.infoIsIgnored()

    def shouldRecognizeFitFailureException(self):        
        fix = Fixture()
        cell = Parse(tag="td", body="Oops.")
        fix.exception(cell, FitFailureException("What the heck?"))
        assert cell.body.find("What the heck?") > -1
        assert cell.tagIsError()
        assert fix.counts.exceptions == 1

class MockRaisesErrorOnDoTable(Fixture):
    def doTable(self, unused='table'):
        raise Exception("Testing Error!")

class ErrorOnFirstTable(TestCase):
    def shouldPostErrorOnFirstTable(self):
        fix = MockRaisesErrorOnDoTable()
        table = Parse("<table><tr><td>"
            "tests.FixtureTest.MockRaisesErrorOnDoTable</td></tr></table>")
        fix.doTables(table)
        cell = table.parts.parts
        assert cell.tagIsError()

class TestSymbols(TestCase):
    def setUp(self):
        setupFitGlobalForTests("Batch")

    def tearDown(self):
        setupFitGlobalForTests("Batch")

    def shouldAccessRunSymbols(self):
        FG.RunLevelSymbols["aSymbol"] = "Clang!"
        fix = Fixture()
        assert fix.getSymbol("aSymbol") == "Clang!"

    def shouldNotBeFitnesse(self):
        fix = Fixture()
        assert not fix.isFitNesse() 

class TestFitNesseTest(TestCase):
    def setUp(self):
        print '%s %s' % (self.id(), self.shortDescription())
        setupFitGlobalForTests("FitNesseOnline")

    def tearDown(self):
        setupFitGlobalForTests("Batch")

    def shouldBeFitnesse(self):
        fix = Fixture()
        assert fix.isFitNesse()

class SetupExitMock1(Fixture):
    def setUpFixture(self, firstRow):
        self.setUpEntered = True
        self.firstRow = firstRow

    def tearDownFixture(self):
        self.tearDownEntered = True

    setUpEntered = False
    tearDownEntered = False
    firstRow = None

    _typeDict={}    

class SpecifySetupAndTeardownExits(FitTestCommon):        
    def setUp(self):
        print '%s %s' % (self.id(), self.shortDescription())
        setupFitGlobalForTests("FitNesseOnline")
        SetupExitMock1._typeDict = {}

    def tearDown(self):
        setupFitGlobalForTests("Batch")

    def shouldTakeSetupExits(self):
        fix = SetupExitMock1()
        table = Parse("<table><tr><td>"
            "tests.FixtureTest.SetupExitMock1</td></tr></table>")
        fix.doTable(table)
        assert fix.setUpEntered
        assert fix.tearDownEntered
        assert fix.firstRow.parts.body == "tests.FixtureTest.SetupExitMock1"

    def shouldIgnoreSetupExitsIfAppExitReturnsFalse(self):        
        class setUpExit(object):
            def fixtureSetUpExit(self, label):
                return False
        self._installApplicationExit(setUpExit)
        fix = SetupExitMock1()
        table = Parse("<table><tr><td>"
            "tests.FixtureTest.SetupExitMock1</td></tr></table>")
        fix.doTable(table)
        assert fix.setUpEntered is False
        assert fix.tearDownEntered is False
        assert fix.firstRow is None

    def shouldTakeSetupExitsIfAppExitReturnsTrue(self):        
        class setUpExit(object):
            def fixtureSetUpExit(self, label):
                return True
        self._installApplicationExit(setUpExit)
        fix = SetupExitMock1()
        table = Parse("<table><tr><td>"
            "tests.FixtureTest.SetupExitMock1</td></tr></table>")
        fix.doTable(table)
        assert fix.setUpEntered
        assert fix.tearDownEntered
        assert fix.firstRow.parts.body == "tests.FixtureTest.SetupExitMock1"

    def shouldIgnoreSetupExitsIfMetaDataSaysFalse(self):        
        fix = SetupExitMock1()
        table = Parse("<table><tr><td>"
            "tests.FixtureTest.SetupExitMock1</td></tr></table>")
        SetupExitMock1._typeDict[".takeSetupExits"] = False
        fix.doTable(table)
        assert fix.setUpEntered is False
        assert fix.tearDownEntered is False
        assert fix.firstRow is None

if __name__ == '__main__':
    main(defaultTest='makeFixtureTest')
