# test module for RowFixture
#legalStuff jr04-05
# Copyright 2004-2005 John H. Roth Jr.
# Released under the terms of the General Public License (GPL), Release 2.1 or later
# See license.txt for terms and disclaimer of all warrenties and liability.
# Last updated for Release 0.8a1
#endLegalStuff

from unittest import makeSuite, TestCase, main
from fit.Counts import Counts
from fit.FitException import FitException
from fit import FitGlobal
from fit import InitEnvironment
from fit.Options import Options
from fit.Parse import Parse, ParseException
from fit.RowFixture import RowFixture
from fit.SiteOptions import BatchBase
from fit.Utilities import em
from fit import Variations

try:
    False
except: #pragma: no cover
    True = 1
    False = 0

def makeRowFixtureTest():
    theSuite = makeSuite(Test_RowFixture, 'test')
    theSuite.addTests([makeSuite(TestRowFixtureBind, 'test'),
                       makeSuite(SpecifyMarkupOff, "should"),
                       makeSuite(SpecifyExtendedLabelProcess, "should"),
                       makeSuite(SpecifyCollectionFromSymbol, "should"),
                       makeSuite(TestRowFixtureProcess, 'should'),
                       ])
    return theSuite

class AnObject(object):
    _typeDict = {"output": "Int"}
    def __init__(self, aString):
        self.anInt = int(aString)

    def __eq__(self, other):
        return id(self) == id(other)

    def __str__(self):
        return str(self.anInt)

    def input(self):        
        return self

    def process(self):
        return "wxyz"

    def output(self):
        return self.anInt

    def dither(self):
        return None

AnObject._typeDict["input"] = AnObject(1) # an instance

theCollection = []

class RowFixture1(RowFixture):
    _typeDict = {"input": AnObject(1),
                 "process": "String",
                 "output": "Int"}

    def query(self):
        return self.getSymbol("theCollection")

class Test_RowFixture(TestCase):
    def setUp(self):
        print '%s %s' % (self.id(), self.shortDescription())

    def _doTable(self, obj, table):
        self.exceptionWasPropagated = False
        headCell = table.parts.parts
        try:
            obj.doTable(table)
        except FitException, e:
            self.exceptionWasPropagated = True
            obj.exception(headCell, e)

    def testExtractListParm(self):
        fuList = ["fubar"]
        obj = RowFixture(fuList, {})
        obj.setActualCollection()
        assert obj.paramCollection == fuList
        assert obj.actuals == fuList
        assert id(obj.actuals) != id(fuList)
        assert obj.paramTypeDict == {}
        
    def testExtractListParmOfLengthThree(self):
        fuList = ["snafu", "spam", "fubar"]
        obj = RowFixture(fuList, {})
        obj.setActualCollection()
        assert obj.paramCollection == fuList
        assert obj.actuals == fuList
        assert id(obj.actuals) != id(fuList)
        assert obj.paramTypeDict == {}

    def testExtractDictParm(self):
        fuDict = {1: "snafu", 3: "fubar"}
        fuList = ["snafu", "fubar"]
        obj = RowFixture(fuDict, {})
        obj.setActualCollection()
        assert obj.paramCollection == fuDict
        assert obj.actuals == fuList
        assert obj.paramTypeDict == {}

    def testErrorIfNotDictOrSequenceOrIterator(self):
        obj = RowFixture(3.14, {})
        self.assertRaises(FitException, obj.setActualCollection)

    def testExtractUnsupportedParm(self):
        fuString = "Snafu"
        obj = RowFixture(fuString, {})
        self.assertRaises(FitException, obj.setActualCollection)

    def testMissingLabelRow(self):
        obj = RowFixture(["fuString"], {})
        table = Parse("<table><tr><td>fit.RowFixture</td></tr></table>")
        self._doTable(obj, table)
        headCell = table.parts.parts
        assert headCell.tagIsError()
        assert headCell.body.find("Row containing column") > -1
        assert self.exceptionWasPropagated

    def testTableExitedIfErrorInLabelRow(self):
        table = Parse("<table><tr><td>fit.RowFixture1</td></tr>"
                      "<tr><td>fubar</td></tr></table>")
        obj = RowFixture1()
        obj.setSymbol("theCollection", (AnObject(1),))
        self._doTable(obj, table)
        label = table.parts.more.parts
        assert label.tagIsError()
        assert label.body.find("is not in any") > -1

class TestRowFixtureBind(TestCase):
    def setUp(self):
        print '%s %s' % (self.id(), self.shortDescription())

    def _createLabelRow(self, labels):
        first = Parse(tag="td")
        last = first
        for label in labels:
            last.more = Parse(tag = "td", body = label)
            last = last.more
        return first.more

    def testBindOneColumn(self):
        labels = self._createLabelRow(("input",))
        obj = RowFixture1()
        obj.setSymbol("theCollection", (AnObject(1),))
        obj.setActualCollection()
        bindings = obj.bind(labels)
        assert bindings[0][1] == "input"
        assert bindings[0][2] is False
        assert len(bindings) == 1

    def testBindThreeColumns(self):
        labels = self._createLabelRow(("input", "process", "output"))
        obj = RowFixture1()
        obj.setSymbol("theCollection", (AnObject(1),))
        obj.setActualCollection()
        bindings = obj.bind(labels)
        assert bindings[2][1] == "output"
        assert bindings[2][2] is False
        assert len(bindings) == 3

    def testDictionaryInObjectList(self):
        labels = self._createLabelRow(("input", "process", "output"))
        obj = RowFixture1()
        obj.setSymbol("theCollection",
                      ({"input": AnObject(1), "output": 1},
                       AnObject(1),
                       ))
        obj.setActualCollection()
        bindings = obj.bind(labels)
        assert bindings[2][1] == "output"
        assert bindings[2][2] is False
        assert len(bindings) == 3

    def testSymbolRef(self):
        labels = self._createLabelRow(("input=", "process", "output"))
        obj = RowFixture1()
        obj.setSymbol("theCollection", (AnObject(1),))
        obj.setActualCollection()
        bindings = obj.bind(labels)
        assert bindings[2][1] == "output"
        assert bindings[0][2]
        assert len(bindings) == 3

    def testErrorMarkingIfLabelIsNotInAnyObject(self):
        labels = self._createLabelRow(("fubar",))
        obj = RowFixture1()
        obj.setSymbol("theCollection", (AnObject(1),))
        obj.setActualCollection()
        try:
            unused = obj.bind(labels)
        except FitException, e:
            if e.args[0] != "IgnoreException":
                raise
        assert labels.tagIsError()
        assert labels.body.find("is not in any") > -1

    def testNoErrorIfNoObjectsInCollection(self):        
        labels = self._createLabelRow(("input",))
        obj = RowFixture1()
        obj.setSymbol("theCollection", [])
        obj.setActualCollection()
        try:
            unused = obj.bind(labels)
        except FitException, e:
            if e.args[0] != "IgnoreException":
                raise
        assert labels.tagIsNotAnnotated()
#        assert labels.body.find("is not in any") > -1

    def testMarkLabelWrongIfNoMetadata(self):
        labels = self._createLabelRow(("dither",))
        obj = RowFixture1()
        obj.setSymbol("theCollection", (AnObject(1),))
        obj.setActualCollection()
        unused = obj.bind(labels)
        assert labels.tagIsError()

class RowFixtureForMarkupOff(RowFixture):
    _typeDict = {".markup": "off",
                 "input": AnObject(1),
                 "input.columnType": "checkSymbol",
                 "process": "String",
                 "output": "Int"}

    def query(self):
        return self.getSymbol("theCollection")

class SpecifyMarkupOff(TestCase):
    def setUp(self):
        print '%s %s' % (self.id(), self.shortDescription())
        self.options = Options(["FileRunner", "+v", "foo", "bar"],
                               BatchBase.parmDict)
        self.saveFitGlobal = (FitGlobal.RunOptions, FitGlobal.Options,
                              FitGlobal.Environment)
        FitGlobal.RunOptions = self.options
        FitGlobal.Options = self.options
        FitGlobal.Environment = "Batch"
        Variations.returnVariation()

    def _createLabelRow(self, labels):
        first = Parse(tag="td")
        last = first
        for label in labels:
            last.more = Parse(tag = "td", body = label)
            last = last.more
        return first.more

    def shouldSymbolRefWithMarkupOff(self):
        labels = self._createLabelRow(("input", "process", "output"))
        obj = RowFixtureForMarkupOff()
        obj.setSymbol("theCollection", (AnObject(1),))
        obj.setActualCollection()
        bindings = obj.bind(labels)
        assert bindings[2][1] == "output"
        assert bindings[0][2]
        assert len(bindings) == 3

    def tearDown(self):
        FitGlobal.RunOptions, FitGlobal.Options, FitGlobal.Environment = \
                              self.saveFitGlobal

class RowFixtureForExtendedLabelProcess(RowFixture):
    _typeDict = {".extendedLabelProcess": "on",
                 "input": AnObject(1),
                 "input.columnType": "checkSymbol",
                 "process": "String",
                 "output": "Int"}

    def processLabel(self, label, unused='columnNumber'):
        if label == "larry":
            return "result", "input"
        elif (label == "moe"):
            return "checkSymbol", "process"
        elif (label == "curley"):
            return "result", "output"
        return "result", label

    def query(self):
        return self.getSymbol("theCollection")

class SpecifyExtendedLabelProcess(TestCase):
    def setUp(self):
        print '%s %s' % (self.id(), self.shortDescription())
        self.options = Options(["FileRunner", "+v", "foo", "bar"],
                               BatchBase.parmDict)
        self.saveFitGlobal = (FitGlobal.RunOptions, FitGlobal.Options,
                              FitGlobal.Environment)
        FitGlobal.RunOptions = self.options
        FitGlobal.Options = self.options
        FitGlobal.Environment = "Batch"
        Variations.returnVariation()

    def _createLabelRow(self, labels):
        first = Parse(tag="td")
        last = first
        for label in labels:
            last.more = Parse(tag = "td", body = label)
            last = last.more
        return first.more

    def shouldChangeLabels(self):
        labels = self._createLabelRow(("larry", "moe", "curley"))
        obj = RowFixtureForExtendedLabelProcess()
        obj.setSymbol("theCollection", (AnObject(1),))
        obj.setActualCollection()
        bindings = obj.bind(labels)
        assert len(bindings) == 3
        assert bindings[0][1] == "input"
        assert bindings[0][2]
        assert bindings[1][1] == "process"
        assert bindings[1][2]
        assert bindings[2][1] == "output"
        assert bindings[2][2] is False

    def tearDown(self):
        FitGlobal.RunOptions, FitGlobal.Options, FitGlobal.Environment = \
                              self.saveFitGlobal

class CollSymbol(object):
    def __init__(self, coll, metaData):
        self.collection = coll
        self.metaData = metaData

class SpecifyCollectionFromSymbol(TestCase):
    def setUp(self):
        print '%s %s' % (self.id(), self.shortDescription())

    def shouldHandleCollectionFromSymbol(self):
        fix = RowFixture()
        coll = CollSymbol([AnObject(1), AnObject(2), AnObject(3)],
                          AnObject._typeDict)
        fix.setSymbol("aCollection", coll)
        table = Parse(
            "<table><tr><td>fit.RowFixture</td><td>aCollection</td></tr>"
            "<tr><td>output</td></tr>"
            "<tr><td>1</td></tr>"
            "<tr><td>2</td></tr>"
            "<tr><td>3</td></tr></table>")
        fix.doTables(table)
        row1 = table.parts.more.more.parts
        row2 = table.parts.more.more.more.parts
        row3 = table.parts.more.more.more.more.parts
        assert row1.tagIsRight()
        assert row2.tagIsRight()
        assert row3.tagIsRight()
        assert table.parts.more.more.more.more.more is None

    def shouldPostExceptionInParameterCellIfSymbolMissing(self):
        fix = RowFixture()
        unused = CollSymbol([AnObject(1), AnObject(2), AnObject(3)],
                          AnObject._typeDict)
        FitGlobal.testLevelSymbols = {}
        table = Parse(
            "<table><tr><td>fit.RowFixture</td><td>aCollection</td></tr>"
            "<tr><td>output</td></tr>"
            "<tr><td>1</td></tr>"
            "<tr><td>2</td></tr>"
            "<tr><td>3</td></tr></table>")
        fix.doTables(table)
        parmCell = table.parts.parts.more
        assert parmCell.tagIsError()
        assert table.parts.more.more.more.more.more is None

class ProcObj(object):
    def __init__(self, c1, c2, c3):
        self.c1 = c1
        self.c2 = c2
        self.c3 = c3

class TestRowFixtureProcess(TestCase):
    def setUp(self):
        print '%s %s' % (self.id(), self.shortDescription())
        FitGlobal.testLevelSymbols = {}

    def tearDown(self):
        FitGlobal.testLevelSymbols = {}

    def shouldMatchThree(self):
        table = Parse("<table><tr><td>fit.RowFixture</td></tr>"
                      "<tr><td>c1</td><td>c2</td><td>c3</td></tr>"
                      "<tr><td>Three</td><td>Blind</td><td>Mice</td></tr>"
                      "<tr><td>Lord</td><td>Lova</td><td>Duck</td></tr>"
                      "<tr><td>Larry</td><td>Moe</td><td>Curly</td></tr>"
                      "</table>")
        coll = [ProcObj("Three", "Blind", "Mice"),
                ProcObj("Lord", "Lova", "Duck"),
                {"c1": "Larry", "c2": "Moe", "c3": "Curly"}]
        metaData = {"c1": "String", "c2": "String", "c3": "String"}
        fix = RowFixture(coll, metaData)
        fix.doTable(table)
        assert fix.counts.right == 9

    def shouldSurplusRow(self):
        table = Parse("<table><tr><td>fit.RowFixture</td></tr>"
                      "<tr><td>c1</td><td>c2</td><td>c3</td></tr>"
                      "<tr><td>Three</td><td>Blind</td><td>Mice</td></tr>"
                      "<tr><td>Larry</td><td>Moe</td><td>Curly</td></tr>"
                      "</table>")
        coll = [ProcObj("Three", "Blind", "Mice"),
                ProcObj("Lord", "Lova", "Duck"),
                {"c1": "Larry", "c2": "Moe", "c3": "Curly"}]
        metaData = {"c1": "String", "c2": "String", "c3": "String"}
        fix = RowFixture(coll, metaData)
        fix.doTable(table)
        assert fix.counts.right == 6
                      
    def shouldUnmatchedRow(self):
        table = Parse("<table><tr><td>fit.RowFixture</td></tr>"
                      "<tr><td>c1</td><td>c2</td><td>c3</td></tr>"
                      "<tr><td>Three</td><td>Blind</td><td>Mice</td></tr>"
                      "<tr><td>Lord</td><td>Lova</td><td>Duck</td></tr>"
                      "<tr><td>Larry</td><td>Moe</td><td>Curly</td></tr>"
                      "</table>")
        coll = [ProcObj("Three", "Blind", "Mice"),
                {"c1": "Larry", "c2": "Moe", "c3": "Curly"}]
        metaData = {"c1": "String", "c2": "String", "c3": "String"}
        fix = RowFixture(coll, metaData)
        fix.doTable(table)
        assert fix.counts.right == 6

    def shouldHandleDuplicateRow(self):
        table = Parse("<table><tr><td>fit.RowFixture</td></tr>"
                      "<tr><td>c1</td><td>c2</td><td>c3</td></tr>"
                      "<tr><td>Three</td><td>Blind</td><td>Mice</td></tr>"
                      "<tr><td>Lord</td><td>Lova</td><td>Duck</td></tr>"
                      "<tr><td>Lord</td><td>Lova</td><td>Duck</td></tr>"
                      "<tr><td>Larry</td><td>Moe</td><td>Curly</td></tr>"
                      "</table>")
        coll = [ProcObj("Three", "Blind", "Mice"),
                ProcObj("Lord", "Lova", "Duck"),
                {"c1": "Larry", "c2": "Moe", "c3": "Curly"}]
        metaData = {"c1": "String", "c2": "String", "c3": "String"}
        fix = RowFixture(coll, metaData)
        fix.doTable(table)
        assert fix.counts.right == 9

    def shouldHandleUndefinedColumn(self):
        table = Parse("<table><tr><td>fit.RowFixture</td></tr>"
                      "<tr><td>c1</td><td>Huh</td><td>c3</td></tr>"
                      "<tr><td>Three</td><td>Blind</td><td>Mice</td></tr>"
                      "<tr><td>Lord</td><td>Lova</td><td>Duck</td></tr>"
                      "<tr><td>Lord</td><td>Lova</td><td>Duck</td></tr>"
                      "<tr><td>Larry</td><td>Moe</td><td>Curly</td></tr>"
                      "</table>")
        coll = [ProcObj("Three", "Blind", "Mice"),
                ProcObj("Lord", "Lova", "Duck"),
                ProcObj("Lord", "Lova", "Duck"),
                {"c1": "Larry", "Huh": "Moe", "c3": "Curly"}]
        metaData = {"c1": "String", "c2": "String", "c3": "String"}
        fix = RowFixture(coll, metaData)
        fix.doTable(table)
##        em("\n%s" % table.toNodeList())
##        cell = table.parts.more.parts.more
##        em("tag: %s body: %s" % (cell.tag, cell.body))
        assert fix.counts == Counts(9, 0, 3, 1)

    def shouldHandleUndefinedColumnWithStringMismatch(self):
        table = Parse("<table><tr><td>fit.RowFixture</td></tr>"
                      "<tr><td>c1</td><td>Huh</td><td>c3</td></tr>"
                      "<tr><td>Three</td><td>Blind</td><td>Mice</td></tr>"
                      "<tr><td>Lord</td><td>Lova</td><td>Duck</td></tr>"
                      "<tr><td>Larry</td><td>Moe</td><td>Curly</td></tr>"
                      "</table>")
        coll = [ProcObj("Three", "Blind", "Mice"),
                ProcObj("Lord", "Lova", "Duck"),
                {"c1": "Larry", "Huh": "Moe", "c3": "Curly"}]
        coll[0].Huh = "Blind"
        coll[1].Huh = "says to"
        metaData = {"c1": "String", "c2": "String", "c3": "String"}
        fix = RowFixture(coll, metaData)
        fix.doTable(table)
##        em("\n%s" % table.toNodeList())
##        cell = table.parts.more.parts.more
##        em("tag: %s body: %s" % (cell.tag, cell.body))
        assert fix.counts == Counts(8, 1, 0, 1)

    def shouldPutMessageInCellForUndefinedAttributeInSurplusRow(self):
        table = Parse("<table><tr><td>fit.RowFixture</td></tr>"
                      "<tr><td>c1</td><td>Huh</td><td>c3</td></tr>"
                      "<tr><td>Three</td><td>Blind</td><td>Mice</td></tr>"
                      "<tr><td>Lord</td><td>Lova</td><td>Duck</td></tr>"
                      "<tr><td>Larry</td><td>Moe</td><td>Curly</td></tr>"
                      "</table>")
        coll = [ProcObj("Three", "Blind", "Mice"),
                ProcObj("Lord", "Lova", "Duck"),
                {"c1": "Larry", "Huh": "Moe", "c3": "Curly"},
                {"c1": "Larry", "c3": "Curly"}]
        coll[0].Huh = "Blind"
        coll[1].Huh = "says to"
        metaData = {"c1": "String", "c2": "String", "c3": "String"}
        fix = RowFixture(coll, metaData)
        fix.doTable(table)
##        em("\n%s" % table.toNodeList())
        cell = table.parts.more.more.more.more.more.parts.more
##        em("tag: %s body: %s" % (cell.tag, cell.body))
        assert cell.body.find("[missing attribute]") > -1
        assert fix.counts == Counts(8, 2, 0, 1)

    def shouldPutMessageInCellForUnprintableAttributeInSurplusRow(self):
        table = Parse("<table><tr><td>fit.RowFixture</td></tr>"
                      "<tr><td>c1</td><td>Huh</td><td>c3</td></tr>"
                      "<tr><td>Three</td><td>Blind</td><td>Mice</td></tr>"
                      "<tr><td>Lord</td><td>Lova</td><td>Duck</td></tr>"
                      "<tr><td>Larry</td><td>Moe</td><td>Curly</td></tr>"
                      "</table>")
        coll = [ProcObj("Three", "Blind", "Mice"),
                ProcObj("Lord", "Lova", "Duck"),
                {"c1": "Larry", "Huh": "Moe", "c3": "Curly"},
                {"c1": "Larry", "Huh": u"\u00a1", "c3": "Curly"}]
        coll[0].Huh = "Blind"
        coll[1].Huh = "says to"
        metaData = {"c1": "String", "c2": "String", "c3": "String"}
        fix = RowFixture(coll, metaData)
        fix.doTable(table)
##        em("\n%s" % table.toNodeList())
        cell = table.parts.more.more.more.more.more.parts.more
##        em("tag: %s body: %s" % (cell.tag, cell.body))
        assert cell.body.find("[error extracting value]") > -1
        assert fix.counts == Counts(8, 2, 0, 1)

    def shouldHandleSymbolicReferencesInLastColumn(self):
        table = Parse("<table><tr><td>fit.RowFixture</td></tr>"
                      "<tr><td>c1</td><td>c2</td><td>c3=</td></tr>"
                      "<tr><td>Three</td><td>Blind</td><td>a</td></tr>"
                      "<tr><td>Lord</td><td>Lova</td><td>b</td></tr>"
                      "<tr><td>Larry</td><td>Moe</td><td>c</td></tr>"
                      "</table>")
        coll = [ProcObj("Three", "Blind", "Mice"),
                ProcObj("Lord", "Lova", "Duck"),
                {"c1": "Larry", "c2": "Moe", "c3": "Curly"}]
        metaData = {"c1": "String", "c2": "String", "c3": "String"}
        fix = RowFixture(coll, metaData)
        fix.setSymbol("a", "Mice")
        fix.setSymbol("b", "Duck")
        fix.setSymbol("c", "Curly")
        fix.doTable(table)
#        label1 = table.parts.more.parts
        assert fix.counts == Counts(9)

    def shouldMarkIncorrectSymbolReferenceAsWrong(self):
        table = Parse("<table><tr><td>fit.RowFixture</td></tr>"
                      "<tr><td>c1</td><td>c2</td><td>c3=</td></tr>"
                      "<tr><td>Three</td><td>Blind</td><td>a</td></tr>"
                      "<tr><td>Lord</td><td>Lova</td><td>b</td></tr>"
                      "<tr><td>Larry</td><td>Moe</td><td>c</td></tr>"
                      "</table>")
        coll = [ProcObj("Three", "Blind", "Mice"),
                ProcObj("Lord", "Lova", "Duck"),
                {"c1": "Larry", "c2": "Moe", "c3": "Curly"}]
        metaData = {"c1": "String", "c2": "String", "c3": "String"}
        fix = RowFixture(coll, metaData)
        fix.setSymbol("a", "Mice")
        fix.setSymbol("b", "Duck")
        fix.setSymbol("c", "Laurel")
        fix.doTable(table)
##        label1 = table.parts.more.parts
##        em("\n%s" % table.toNodeList())
##        cell = table.parts.more.more.more.more.parts.more.more
##        em("tag: %s body: %s" % (cell.tag, cell.body))
        assert fix.counts == Counts(8, 1)

    def shouldHandleSymbolicReferencesInFirstColumn(self):
        table = Parse("<table><tr><td>fit.RowFixture</td></tr>"
                      "<tr><td>c1=</td><td>c2</td><td>c3</td></tr>"
                      "<tr><td>a</td><td>Blind</td><td>Mice</td></tr>"
                      "<tr><td>b</td><td>Lova</td><td>Duck</td></tr>"
                      "<tr><td>c</td><td>Moe</td><td>Curly</td></tr>"
                      "</table>")
        coll = [ProcObj("Three", "Blind", "Mice"),
                ProcObj("Lord", "Lova", "Duck"),
                {"c1": "Larry", "c2": "Moe", "c3": "Curly"}]
        metaData = {"c1": "String", "c2": "String", "c3": "String"}
        fix = RowFixture(coll, metaData)
        fix.setSymbol("a", "Three")
        fix.setSymbol("b", "Lord")
        fix.setSymbol("c", "Larry")
        fix.doTable(table)
        assert fix.counts.right == 9

    def shouldHandleMissingSymbolInPartitionStep(self):
        table = Parse("<table><tr><td>fit.RowFixture</td></tr>"
                      "<tr><td>c1=</td><td>c2</td><td>c3</td></tr>"
                      "<tr><td>a</td><td>Blind</td><td>Mice</td></tr>"
                      "<tr><td>b</td><td>Lova</td><td>Duck</td></tr>"
                      "<tr><td>c</td><td>Moe</td><td>Curly</td></tr>"
                      "</table>")
        coll = [ProcObj("Three", "Blind", "Mice"),
                ProcObj("Lord", "Lova", "Duck"),
                {"c1": "Larry", "c2": "Moe", "c3": "Curly"}]
        metaData = {"c1": "String", "c2": "String", "c3": "String"}
        fix = RowFixture(coll, metaData)
        fix.setSymbol("b", "Lord")
        fix.setSymbol("c", "Larry")
        fix.doTable(table)
        assert fix.counts == Counts(6, 1, 2, 1)

    def shouldHandleUndefinedAttributeInCollectionElement(self):
        table = Parse("<table><tr><td>fit.RowFixture</td></tr>"
                      "<tr><td>c1</td><td>c2</td><td>c3</td></tr>"
                      "<tr><td>Three</td><td>Blind</td><td>Mice</td></tr>"
                      "<tr><td>Lord</td><td>Lova</td><td>Duck</td></tr>"
                      "<tr><td>Lord</td><td>Lova</td><td>Duck</td></tr>"
                      "<tr><td>Larry</td><td>Moe</td><td>Curly</td></tr>"
                      "</table>")
        coll = [ProcObj("Three", "Blind", "Mice"),
                ProcObj("Lord", "Lova", "Duck"),
                {"missing": "Larry", "c2": "Moe", "c3": "Curly"}]
        metaData = {"c1": "String", "c2": "String", "c3": "String"}
        fix = RowFixture(coll, metaData)
        fix.doTable(table)
        assert fix.counts == Counts(6, 3)

    def shouldMarkShortRowAsMissingWithException(self):
        table = Parse("<table><tr><td>fit.RowFixture</td></tr>"
                      "<tr><td>c1</td><td>c2</td><td>c3</td></tr>"
                      "<tr><td>Three</td><td>Blind</td><td>Mice</td></tr>"
                      "<tr><td>Lord</td><td>Lova</td></tr>"
                      "<tr><td>Larry</td><td>Moe</td><td>Curly</td></tr>"
                      "</table>")
        coll = [ProcObj("Three", "Blind", "Mice"),
                ProcObj("Lord", "Lova", "Duck"),
                {"c1": "Larry", "c2": "Moe", "c3": "Curly"}]
        metaData = {"c1": "String", "c2": "String", "c3": "String"}
        fix = RowFixture(coll, metaData)
        fix.doTable(table)
##        em("\n%s" % table.toNodeList())
##        label1 = table.parts.more.parts
##        em("tag: %s body: %s" % (label1.tag, label1.body))
##        cell = table.parts.more.more.more.parts
##        em("tag: %s body: %s" % (cell.tag, cell.body))
        assert fix.counts == Counts(6, 1, 0, 1)

    def shouldMarkRowWithoutCellsAsMissingWithException(self):
        # ??? should this be fixed. Throws ParseException without getting to RowFixture
##        table = Parse("<table><tr><td>fit.RowFixture</td></tr>"
        self.assertRaises(ParseException, Parse, "<table><tr><td>fit.RowFixture</td></tr>"
                      "<tr><td>c1</td><td>c2</td><td>c3</td></tr>"
                      "<tr><td>Three</td><td>Blind</td><td>Mice</td></tr>"
                      "<tr></tr>"
                      "<tr><td>Larry</td><td>Moe</td><td>Curly</td></tr>"
                      "</table>")
##        coll = [ProcObj("Three", "Blind", "Mice"),
##                ProcObj("Lord", "Lova", "Duck"),
##                {"c1": "Larry", "c2": "Moe", "c3": "Curly"}]
##        metaData = {"c1": "String", "c2": "String", "c3": "String"}
##        fix = RowFixture(coll, metaData)
##        fix.doTable(table)
##        assert fix.counts == Counts(6, 1, 0, 1)

if __name__ == '__main__':
    main(defaultTest='makeRowFixtureTest')
