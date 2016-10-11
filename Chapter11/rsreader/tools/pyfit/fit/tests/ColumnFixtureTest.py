# test module for ColumnFixture
#legalStuff jr05
# Copyright 2005 John H. Roth Jr.
# Released under the terms of the General Public License (GPL), Release 2.1 or later
# See license.txt for terms and disclaimer of all warrenties and liability.
# Last updated for Release 0.8a1
#endLegalNotices

import types
from unittest import makeSuite, TestCase, main

from fit.ColumnFixture import ColumnFixture
from fit import FitGlobal
from fit.Options import Options
from fit.Parse import Parse
from fit.SiteOptions import BatchBase
from fit import TypeAdapter as ta
from fit import taBase as tab
from fit.Utilities import em
from fit import Variations

try:
    False
except:
    True = 1
    False = 0

def makeColumnFixtureTest():
    suite = makeSuite(OldBindExamples, 'should')
    suite.addTest(makeSuite(ExtendedLabelExitExamples, "should"))
    suite.addTest(makeSuite(ExtendedLabelNoExitExamples, "should"))
    suite.addTest(makeSuite(NoMarkupExamples, "should"))
    suite.addTest(makeSuite(TestResetAndExecute, "should"))
    suite.addTest(makeSuite(TestExceptionInReset, "should"))
    suite.addTest(makeSuite(TestExceptionInExecute, "should"))
    return suite

class Context(TestCase):
    obj = None # must be set in subclass
    def mustBeEqual(self, actual, expected, message = ""):
        if actual == expected:
            return
        if message:
            self.fail(message)
        else:
            self.fail("actual: '%s' expected: '%s'" % (actual, expected))

    def mustBeTA(self, adapter, unused, kind):
        if not isinstance(adapter, ta.AccessorBaseClass):
            self.fail("expected accessor class, found: %s" % adapter)
        if kind == "Int":
            if not isinstance(adapter.adapter, tab.IntAdapter):
                self.fail("expected Integer Type Adapter. Found: %s" %
                          adapter.adapter)
        elif kind == "String":
            if not isinstance(adapter.adapter, tab.StringAdapter):
                self.fail("expected String Type Adapter. Found: %s" %
                          adapter.adapter)
        else:
            self.fail("unknown type adapter class: %s" % kind)
        return True

    def makeTable(self, pattern):
        table = Parse(tag = "table")
        lastRow = table.parts = Parse(tag = "tr")
        lastNode = firstNode = Parse(tag = "td")
        for item in pattern.split("|")[1:-1]:
            if not item.startswith("\n"):
                lastNode.more = Parse(tag="td", body=item)
                lastNode = lastNode.more
            else:
                lastRow.parts = firstNode.more
                lastRow.more = Parse(tag="tr")
                lastRow = lastRow.more
                lastNode = firstNode = Parse(tag="td")
        lastRow.parts = firstNode.more
        return table

    def runTable(self, pattern):
        table = self.makeTable(pattern)
        rows = table.parts.more
        self.obj.doRows(rows)
        return rows

    def setUp(self):
        print '%s %s' % (self.id(), self.shortDescription())
        self.options = Options(["FileRunner", "+v", "+e", "foo", "bar"],
                               BatchBase.parmDict)
        self.saveFitGlobal = (FitGlobal.RunOptions, FitGlobal.Options,
                              FitGlobal.Environment)
        FitGlobal.RunOptions = self.options
        FitGlobal.Options = self.options
        FitGlobal.Environment = "Batch"
        Variations.returnVariation()
        self._createFixture()

    def _createFixture(self):
        raise Exception("Error in subclass. _createFixture must be overridden")

    def tearDown(self):
        FitGlobal.RunOptions, FitGlobal.Options, FitGlobal.Environment = \
                              self.saveFitGlobal

class MockColumnFixture(ColumnFixture):
    _typeDict = {"aColumn": "Int",
                 "bColumn.columnType": "result",
                 "bColumn": "Int"}

    aColumn = 0
    bColumn = 0

class OldBindExamples(Context):
    def _createFixture(self):
        self.obj = MockColumnFixture()

    def checkMarkup(self, label, adapter, accessor, type, identifier):
        heads = Parse(tag="td", body=label)
        self.obj.bind(heads)
        self.mustBeEqual(self.obj.columnExecutors[0], adapter)
        self.mustBeTA(self.obj.columnBindings[0], accessor, type)
        newId, colType = self.obj._extractColumnTypeFromOldMarkup(label, {})
        assert newId == identifier

    def checkMarkupNone(self, label, adapter, unused, dummy):
        heads = Parse(tag="td", body=label)
        self.obj.bind(heads)
        self.mustBeEqual(self.obj.columnExecutors[0], adapter)
        assert self.obj.columnBindings[0] is None

    def shouldTreatNoLabelMarkupAsAGiven(self):
        self.checkMarkup("aColumn", self.obj.setExecutor, "field", "Int",
                         "aColumn")

    def shouldTreatParenMarkupAsAResult(self):
        self.checkMarkup("aColumn()", self.obj.getExecutor, "field", "Int",
                         "aColumn")

    def shouldTreatQuestionMarkupAsAResult(self):
        self.checkMarkup("aColumn?", self.obj.getExecutor, "field", "Int",
                         "aColumn")

    def shouldTreatExclamationPointMarkupAsAResult(self):
        self.checkMarkup("aColumn!", self.obj.getExecutor, "field", "Int",
                         "aColumn")

    def shouldTreatBlankAsComment(self):
        self.checkMarkupNone("", self.obj.commentExecutor, "field", "String")

    def shouldTreatUnimplemented(self):
        self.checkMarkupNone("?fubar",
                         self.obj.unimplementedExecutor, "field", "String")

    def shouldMakeLeadingEqualSignSaveCalculatedResultAsSymbol(self):
        self.checkMarkup("=aColumn", self.obj.getSymbolExecutor,
                         "field", "Int", "aColumn")
        
    def shouldMakeLeadingEqualSignSaveCalculatedResultAsSymbol2(self):
        self.checkMarkup("=aColumn()", self.obj.getSymbolExecutor,
                         "field", "Int", "aColumn")

    def shouldMakeLeadingEqualSignSaveCalculatedResultAsSymbol3(self):
        self.checkMarkup("=aColumn?", self.obj.getSymbolExecutor,
                         "field", "Int", "aColumn")

    def shouldMakeTrailingEqualSignRetrieveSymbolAndStoreAsGiven(self):
        self.checkMarkup("aColumn=", self.obj.setSymbolExecutor,
                         "field", "Int", "aColumn")

    def shouldExecuteGiven(self):
        rows = self.runTable("|fit.ColumnFixture|\n|aColumn|\n|6|")
        cell = rows.more.parts
        assert cell.tagIsNotAnnotated()

    def shouldExecuteGivenWithBlankCell(self):
        obj = self.obj
        table = self.makeTable("|fit.ColumnFixture|\n|aColumn|\n||")
        rows = table.parts.more
        obj.aColumn = 6
        obj.doRows(rows)
        cell = rows.more.parts
        assert cell.tagIsNotAnnotated()
        assert cell.infoIsIgnored()

    def shouldExecuteResult(self):
        obj = self.obj
        table = self.makeTable("|fit.ColumnFixture|\n|aColumn()|\n|6|")
        rows = table.parts.more
        obj.aColumn = 6
        obj.doRows(rows)
        cell = rows.more.parts
        assert cell.tagIsRight()

    def shouldExecuteComment(self):
        obj = self.obj
        table = self.makeTable("|fit.ColumnFixture|\n||\n|6|")
        rows = table.parts.more
        obj.doRows(rows)
        cell = rows.more.parts
        assert cell.tagIsNotAnnotated()

    def shouldGetAndStoreIntoSymbol(self):
        obj = self.obj
        obj.setSymbol("foo", None)
        obj.aColumn = 6
        rows = self.runTable("|fit.ColumnFixture|\n|=aColumn|\n|foo|")
        cell = rows.more.parts
        assert obj.getSymbol("foo") == 6
        assert cell.tagIsNotAnnotated()
        assert cell.infoIsIgnored()

    def shouldGetAndStoreIntoSymbolParens(self):
        obj = self.obj
        table = self.makeTable("|fit.ColumnFixture|\n|=aColumn()|\n|foo|")
        obj.setSymbol("foo", None)
        obj.aColumn = 6
        rows = table.parts.more
        obj.doRows(rows)
        cell = rows.more.parts
        assert obj.getSymbol("foo") == 6
        assert cell.tagIsNotAnnotated()
        assert cell.infoIsIgnored()

    def shouldFetchFromSymbolAndStore(self):        
        obj = self.obj
        table = self.makeTable("|fit.ColumnFixture|\n|aColumn=|\n|foo|")
        obj.setSymbol("foo", 7)
        rows = table.parts.more
        obj.doRows(rows)
        cell = rows.more.parts
        assert obj.aColumn == 7
        assert cell.tagIsNotAnnotated()
        assert cell.infoIsIgnored()

    def shouldIgnoreIfUnimplemented(self):
        obj = self.obj
        table = self.makeTable("|fit.ColumnFixture|\n|?aColumn|\n|foo|")
        rows = table.parts.more
        obj.doRows(rows)
        cell = rows.more.parts
        assert cell.tagIsIgnored()

    def shouldRaiseErrorIfRowTooLong(self):
        obj = self.obj
        table = self.makeTable("|fit.ColumnFixture|\n"
                               "|?aColumn|\n|foo|bar|")
        rows = table.parts.more
        obj.doRows(rows)
        cell = rows.more.parts.more
        assert cell.tagIsError()
        assert cell.body.find("Row is too long") > -1

    def shouldCheckSaved(self):
        obj = self.obj
        table = self.makeTable("|fit.ColumnFixture|\n"
                               "|bColumn|\n|foo|")
        obj.setSymbol("foo", 8)
        obj.bColumn = 8
        obj._typeDict["bColumn.columnType"] = "checkSaved"
        rows = table.parts.more
        obj.doRows(rows)
        cell = rows.more.parts
        assert cell.tagIsRight()
        assert cell.infoIsIgnored()

    def shouldCheckSavedWrong(self):
        obj = self.obj
        table = self.makeTable("|fit.ColumnFixture|\n"
                               "|bColumn|\n|foo|")
        obj.setSymbol("foo", 8)
        obj.bColumn = 9
        obj._typeDict["bColumn.columnType"] = "checkSaved"
        rows = table.parts.more
        obj.doRows(rows)
        cell = rows.more.parts
        assert cell.tagIsWrong()
        assert cell.infoIsIgnored()
        assert cell.infoIsWrong()

    def shouldDisplayResult(self):
        obj = self.obj
        table = self.makeTable("|fit.ColumnFixture|\n"
                               "|bColumn|\n||")
        obj.bColumn = 9
        obj._typeDict["bColumn.columnType"] = "display"
        rows = table.parts.more
        obj.doRows(rows)
        cell = rows.more.parts
        assert cell.tagIsNotAnnotated()
        assert cell.body.find("9")
        assert cell.infoIsIgnored()

    def shouldDisplaySavedResult(self):
        obj = self.obj
        obj.bColumn = 10
        obj.setSymbol("foo", 10)
        obj._typeDict["bColumn.columnType"] = "displaySaved"
        rows = self.runTable("|fit.ColumnFixture|\n"
                               "|bColumn|\n|foo|")
        cell = rows.more.parts
        assert cell.tagIsNotAnnotated()
        assert cell.body.find("10")
        assert cell.infoIsIgnored()

    def shouldRaiseExceptionOnBadColumnType(self):        
        obj = self.obj
        obj._typeDict["bColumn.columnType"] = "fubar"
        rows = self.runTable("|fit.ColumnFixture|\n"
                               "|bColumn|\n|foo|")
        labelCell = rows.parts
        cell = rows.more.parts
        assert labelCell.tagIsError()
        assert labelCell.body.find("Unknown column type:") > -1
        assert cell.tagIsIgnored()

    def shouldRaiseExceptionOnBadMethodName(self):        
#        obj = self.obj
        rows = self.runTable("|fit.ColumnFixture|\n"
                               "|leaning column|\n|foo|")
        labelCell = rows.parts
        cell = rows.more.parts
        assert labelCell.tagIsError()
        assert labelCell.body.find(
            "Metadata for 'leaningColumn' not found in class") > -1
        assert cell.tagIsIgnored()

class MockExtendedColumnFixture(ColumnFixture):
    _typeDict = {".extendedLabelProcess": "on",
                 "aColumn": "Int",
                 "given": "Int",
                 "label": "Int",
                 "theAnswer.columnType": "result",
                 "theAnswer": "Int",
                 }

    aColumn = 0
    given = 0
    label = -1
    theAnswer = 42

    def processLabel(self, label, unused):
        return label.split()

class ExtendedLabelExitExamples(Context):
    def _createFixture(self):
        self.obj = MockExtendedColumnFixture()

    def checkLabel(self, label, adapter, accessor, type):
        obj = self.obj
        heads = Parse(tag="td", body=label)
        kind, newLabel = label.split()
        obj.bind(heads)
        adapterName, shouldGetTypeAdapter = obj.columnTypes.get(adapter)
        boundAdapter = getattr(obj, adapterName)
        self.mustBeEqual(obj.columnExecutors[0], boundAdapter)
        self.mustBeTA(obj.columnBindings[0], accessor, type)

    def checkLabelNone(self, label, adapter, unused, dummy):
        obj = self.obj
        heads = Parse(tag="td", body=label)
        kind, newLabel = label.split()
        obj.bind(heads)
        adapterName, shouldGetTypeAdapter = obj.columnTypes.get(adapter)
        boundAdapter = getattr(obj, adapterName)
        self.mustBeEqual(obj.columnExecutors[0], boundAdapter)
        assert obj.columnBindings[0] is None

    def shouldReturnGiven(self):
        self.checkLabel("given label", "given", "field", "Int")

    def shouldReturnResult(self):
        self.checkLabel("result label", "result", "field", "Int")

    def shouldReturnGetSymbol(self):
        self.checkLabel("getSymbol label", "getSymbol", "field", "Int")

    def shouldReturnSetSymbol(self):
        self.checkLabel("setSymbol label", "setSymbol", "field", "Int")

    def shouldReturnCommentColumn(self):
        self.checkLabelNone("comment ?", "comment", "field", "String")

    def shouldReturnIgnoreAdapter(self):
        self.checkLabelNone("ignore ?", "ignore", "field", "String")

    def shouldUseOldAlgorithmResult(self):
        self.checkLabel("continue label?", "result", "field", "Int")

    def shouldUseOldAlgorithmIgnore(self):
        self.checkLabelNone("continue ?label", "ignore", "field", "String")

    def shouldLookupInMetaData(self):
        self.checkLabel("lookup theAnswer", "result", "field", "Int")

class MockExtendedColumnFixtureWithoutExit(ColumnFixture):
    _typeDict = {".extendedLabelProcess": "on",
                 "aColumn": "Int",
                 "given": "Int",
                 "label": "Int",
                 "theAnswer.columnType": "result",
                 "theAnswer": "Int",
                 }

    aColumn = 0
    given = 0
    label = -1
    theAnswer = 42

class ExtendedLabelNoExitExamples(Context):
    def _createFixture(self):
        self.obj = MockExtendedColumnFixtureWithoutExit()

    def shouldRaiseExceptionIfNoExit(self):
        obj = self.obj
        heads = Parse(tag="td", body='label')
        obj.bind(heads)
        assert heads.tagIsError()
        assert heads.body.find("processLabel not implemented") > 1

# TODO - specs for "lookup" - wait until lookup mechanism created.        

class MockNoMarkupColumnFixture(ColumnFixture):
    _typeDict = {".markup": "off",
                 ".display": "on",
                 "theAnswer": "Int",
                 "theAnswer.columnType": "result",
                 "anError": "String",
                 "anError.columnType": "raiseError",
                 }

    theAnswer = 0
    anError = "fubar"

    def getTargetClass(self):
        return self

class NoMarkupExamples(Context):
    def _createFixture(self):
        self.obj = MockNoMarkupColumnFixture()

    def checkLabel(self, label, adapter, accessor, type):
        obj = self.obj
        heads = Parse(tag="td", body=label)
#        kind, newLabel = label.split()
        obj.bind(heads)
        adapterName, shouldGetTypeAdapter = obj.columnTypes.get(adapter)
        boundAdapter = getattr(obj, adapterName)
        self.mustBeEqual(obj.columnExecutors[0], boundAdapter)
        self.mustBeTA(obj.columnBindings[0], accessor, type)

    def shouldHandleResultColumn(self):
        self.checkLabel("the answer", "result", "field", "Int")

    def shouldRaiseErrorInDoCell(self):
#        obj = self.obj
        ColumnFixture.columnTypes["raiseError"] = (
            "testingErrorExecutor", False)
        rows = self.runTable("|fit.ColumnFixture|\n"
                               "|an error|\n|2|")
        labelCell = rows.parts
        cell = rows.more.parts
        assert labelCell.body.find("Type: raiseError") > -1
        assert cell.tagIsError()

class MockResetAndExecute(ColumnFixture):
    _typeDict = {"getMiddle": "Int",
                 "getEnd": "Int"}
    start = 0
    def reset(self):
        self.middle = self.start + 1

    def getMiddle(self):
        return self.middle

    def execute(self):
        self.end = self.middle + 1

    def getEnd(self):
        return self.end

class TestResetAndExecute(Context):
    def _createFixture(self):
        self.obj = MockResetAndExecute()

    def shouldExecuteResetAndExecute(self):
        obj = self.obj
        obj.start = 1
        rows = self.runTable("|fit.ColumnFixture|\n"
                               "|getMiddle()|getEnd?|\n|2|3|")
        cell1 = rows.more.parts
        cell2 = cell1.more
        assert cell1.tagIsRight()
        assert cell2.tagIsRight()

class MockExceptionInReset(MockResetAndExecute):
    def reset(self):
        raise Exception("Expected exception")

class TestExceptionInReset(Context):
    def _createFixture(self):
        self.obj = MockExceptionInReset()

    def shouldPutExceptionInFirstCell(self):
        obj = self.obj
        obj.start = 1
        rows = self.runTable("|fit.ColumnFixture|\n"
                               "|getMiddle()|getEnd?|\n|2|3|")
        cell1 = rows.more.parts
        cell2 = cell1.more
        assert cell1.tagIsError()
        assert cell2.tagIsNotAnnotated()

class MockExceptionInExecute(MockResetAndExecute):
    end = 0
    def getMiddle(self, anInt):
        __pychecker__ = 'no-override'
        self.middle = anInt

    def execute(self):
        raise Exception("Expected Exception")

class TestExceptionInExecute(Context):
    def _createFixture(self):
        self.obj = MockExceptionInExecute()

    def shouldPutExceptionInLastCell(self):
        obj = self.obj
        obj.start = 1
        rows = self.runTable("|fit.ColumnFixture|\n"
                               "|getMiddle|getEnd?|\n|2|3|")
        cell1 = rows.more.parts
        cell2 = cell1.more
        assert cell1.tagIsNotAnnotated()
        assert cell2.infoIsTrace()

if __name__ == '__main__':
    main(defaultTest='makeColumnFixtureTest')
