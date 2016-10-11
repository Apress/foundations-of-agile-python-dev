# test module for miscellaneous classes
#LegalStuff jr05
# Copyright 2005 John H. Roth Jr.
# Released under the terms of the General Public License (GPL), Release 2.1 or later
# See license.txt for terms and disclaimer of all warrenties and liability.
# Last updated for Release 0.8a1
#endLegalStuff

from unittest import makeSuite, TestCase, main
from fit.Counts import Counts, Count
from fit.Fixture import Fixture
from fit.FixtureLoader import FixtureLoader
from fit import FitGlobal
from fit import InitEnvironment
from fit.Import import Import
from fit.Parse import Parse
from fit.ScientificDouble import ScientificDouble
from fit.ScientificFloat import ScientificFloat
from fit.Summary import Summary
from fit import TypeAdapter
from fit.Utilities import em

try:
    False
except: #pragma: no cover
    True = 1
    False = 0

def makeMiscTest():
    suite = makeSuite(TestCounts, 'should')
    suite.addTests(
        [makeSuite(TestScientificFloat, "should"),
         makeSuite(TestApplicationConfigurationInterface, "should"),
         makeSuite(TestSummary, "should"),
         makeSuite(TestImport, "should"),
         ])
    return suite

class TestCounts(TestCase):
##    def setUp(self):
##        print '%s %s' % (self.id(), self.shortDescription())
##
##    def tearDown(self):
##        pass

    def shouldTakeStringConstructor(self):
        count = Counts("1 right, 0 wrong, 15 ignored, 8 exceptions")
        assert str(count) == "1 right, 0 wrong, 15 ignored, 8 exceptions"
        assert str(count) == count.toString() # depreciated!
        assert count.totalCounts() == 24
        assert count.isError()
        assert count.numErrors() == 8
        assert not count.isSummaryCount()

    def shouldThrowExceptionIfBadStringConstructor(self):
        try:
            Counts("fubar")
        except:
            return
        self.fail("Expected exception not thrown")

    def shouldAccumulateTwoCounts(self):
        count1 = Counts("1 right, 0 wrong, 15 ignored, 8 exceptions")
        count2 = Counts(right=4, wrong=6, ignored=2, exceptions=5)
        count1 += count2
        assert str(count1) == "5 right, 6 wrong, 17 ignored, 13 exceptions"

    def shouldRaiseErrorOnWrongTypeToTabulateCount(self):
        count1 = Counts("1 right, 0 wrong, 15 ignored, 8 exceptions")
#        count2 = Counts(right=4, wrong=6, ignored=2, exceptions=5)
        try:
            count1.tabulateCount(3.14)
        except:
            return
        self.fail("Expected exception not received")

    def shouldAccumulateCountEnumerations(self):        
        count = Counts("1 right, 0 wrong, 15 ignored, 8 exceptions")
        count += Count("right")
        count += Count("wrong")
        count += Count("ignored")
        count += Count("exception")
        assert str(count) == "2 right, 1 wrong, 16 ignored, 9 exceptions"

    def shouldCompareToAnotherCounts(self):
        count1 = Counts("1 right, 0 wrong, 15 ignored, 8 exceptions")
        count2 = Counts(right=4, wrong=6, ignored=2, exceptions=5)
        assert count1 != count2
        assert not (count1 == count2)
        assert not count1.equals(count2) # depreciated!!!
        assert count1 == "1 right, 0 wrong, 15 ignored, 8 exceptions"
        assert not (count1 == 45)
        assert not (count1 != 45)

    def shouldTallyPageCounts(self):
        accum = Counts()
        assert not accum.isSummaryCount()
        ex1 = Counts("1 right, 0 wrong, 15 ignored, 8 exceptions")
        accum.tallyPageCounts(ex1)
        assert accum.isSummaryCount()
        assert str(accum) == "0 right, 0 wrong, 0 ignored, 1 exceptions"
        ex2 = Counts("1 right, 0 wrong, 15 ignored, 0 exceptions")
        accum.tallyPageCounts(ex2)
        assert str(accum) == "1 right, 0 wrong, 0 ignored, 1 exceptions"
        ex3 = Counts("0 right, 0 wrong, 15 ignored, 0 exceptions")
        accum.tallyPageCounts(ex3)
        assert str(accum) == "1 right, 0 wrong, 1 ignored, 1 exceptions"
        ex4 = Counts("5 right, 1 wrong, 15 ignored, 0 exceptions")
        accum.tallyPageCounts(ex4)
        assert str(accum) == "1 right, 1 wrong, 1 ignored, 1 exceptions"

class MockObject(Fixture):
    _typeDict = {"sFloat1": ScientificFloat,
                 "sFloat2": ScientificFloat,
                 }

    sFloat1 = ScientificFloat("3.14")
    
    def sFloat2(self):
        return self.sFloat1

class TestScientificFloat(TestCase):
##    def setUp(self):
##        print '%s %s' % (self.id(), self.shortDescription())
##
##    def tearDown(self):
##        pass

    def shouldDoComparesWell(self):
        pi = 3.141592865
        assert ScientificFloat("3.14") == pi
        assert ScientificFloat("3.142") == pi # original 3.141 wrong!
        assert ScientificFloat("3.1416") == pi # original 3.1415 wrong!
        assert ScientificFloat("3.14159") == pi
        assert ScientificFloat("3.141592865") == pi
        assert (ScientificFloat("3.140") == pi) is False
        assert (ScientificFloat("3.144") == pi) is False
        assert (ScientificFloat("3.1414") == pi) is False
        assert (ScientificFloat("3.141592863") == pi) is False
        assert ScientificFloat("3.141592863") != pi
        assert ScientificFloat("2.5") < pi
        av = 6.02e23
        assert ScientificFloat("6.0e23") == av
        assert ScientificFloat("12") == 12.0
        assert ScientificFloat("11") == 11
        assert ScientificFloat("-12.05") == -12.051

    def shouldDoLimitedSubtracts(self):
        v1 = ScientificFloat("3.14")
        v2 = ScientificFloat("3.141")
        self.assertAlmostEqual(v1, v2, 2)
        r1 = v1 - 3.13
        self.assertAlmostEqual(r1, .01, 2)
        r2 = 3.15 - v1
        self.assertAlmostEqual(r2, .01, 2)

    def shouldHandleJavaConventionsInScientificDouble(self):
        v1 = ScientificDouble.parse("3.14")
        assert v1.toString() == "3.14"
        assert v1.doubleValue() == 3.14
        assert v1.floatValue() == 3.14
        assert v1.longValue() == 3
        assert v1.intValue() == 3
        assert v1.equals(3.141)

    def shouldUseWithTypeAdapter(self):
        obj = MockObject()
        givenTA = TypeAdapter.on(obj, "sFloat1")
        givenCell = Parse(tag="td", body="6.45")
        obj.parseAndSet(givenCell, givenTA)
        assert obj.sFloat1 == 6.45
        assert isinstance(obj.sFloat1, ScientificFloat)
        assert givenCell.tagIsNotAnnotated()
        resultTA = TypeAdapter.on(obj, "sFloat2")
        resultCell = Parse(tag="td", body="6.45")
        obj.check(resultCell, resultTA)
        assert resultCell.tagIsRight()

class ExceptionTestAppConfig(object):
    def mapErrorMessage(self, args, unused='isExc', dummy='doTrace'):
        if args[0] == "Test003":
            return "It's magic!"
        elif args[0] == "Test002":
            return "Insert lightbulb joke here", False # was TraceWantd("ignore")
        elif args[0] == "Test001":
            return None, False # was TraceWanted("Ignore")
        return None

class TestApplicationConfigurationInterface(TestCase):
    def setUp(self):
        print '%s %s' % (self.id(), self.shortDescription())
        self.saveAppConfig = (FitGlobal.RunAppConfigModule,
                              FitGlobal.RunAppConfig,
                              FitGlobal.appConfigModule,
                              FitGlobal.appConfig)
        self._setAppConfig((ExceptionTestAppConfig, ExceptionTestAppConfig(),
                           ExceptionTestAppConfig, ExceptionTestAppConfig()))

    def _setAppConfig(self, parms):
        FitGlobal.RunAppConfigModule, FitGlobal.RunAppConfig, \
            FitGlobal.appConfigModule, FitGlobal.appConfig = parms

    def tearDown(self):
        self._setAppConfig(self.saveAppConfig)

    def shouldReturnResultFromRealExit(self):
        exitResult = FitGlobal.appConfigInterface("mapErrorMessage",
                                    ("Test003",), None, None)
        assert exitResult == "It's magic!"

    def shouldReturnNoneFromUnimplementedExit(self):
        exitResult = FitGlobal.appConfigInterface("unimplementedTestExit")
        assert exitResult is None

    def shouldReturnNoneIfNoExitIsInstalled(self):
        self._setAppConfig((None, None, None, None))
        exitResult = FitGlobal.appConfigInterface("mapErrorMessage",
                                    ("Test003",), None, None)
        assert exitResult is None

class TestSummary(TestCase):
    def setUp(self):
        print '%s %s' % (self.id(), self.shortDescription())
        self.sum = Summary()

##    def tearDown(self):
##        pass

    def doIt(self):
        self.table = Parse("<table><tr><td>fit.Summary</td></tr></table>")
        self.sum.doTable(self.table)
        return self.table.parts.more

    def shouldOnlyHaveCountsLineForEmptySummary(self):
        sumObj = self.sum
        row = self.doIt()
        assert row.more is None
        assert row.parts.body.find("counts") > 0
        assert row.parts.more.tagIsRight()
        assert sumObj.counts.totalCounts() == 0

    def shouldPutOutTheSummaryDictionaryInOrder(self):
        sumObj = self.sum
        sumObj.summary["alpha"] = "last"
        sumObj.summary["omega"] = "first"
        row = self.doIt()
        assert row.more.parts.body.find("counts") > 0
        assert row.more.parts.more.tagIsRight()
        assert row.more.more.more is None

    def shouldAnnotateCountAsWrongIfErrors(self):
        sumObj = self.sum
        sumObj.counts.exceptions += 1
        row = self.doIt()
        assert row.more is None
        assert row.parts.body.find("counts") > 0
        assert row.parts.more.tagIsWrong()
        assert sumObj.counts.totalCounts() == 1

class TestImport(TestCase):
    def setUp(self):
        print '%s %s' % (self.id(), self.shortDescription())
        self.imp = imp = Import()
        imp.clearFixtureRenameTable()
        imp.clearRememberedPackageTable()
        
    def tearDown(self):
        imp = self.imp
        imp.clearFixtureRenameTable()
        imp.clearRememberedPackageTable()

    def shouldAddPackageToPackageList(self):
        imp = self.imp
        table = Parse("<table><tr><td>fit.Import</td></tr>"
                    "<tr><td>tests</td></tr></table>")
        imp.doRows(table.parts.more)
        assert imp.fixtureLoader._rememberedPackages[1] == "tests"
        assert len(imp.fixtureLoader._rememberedPackages) == 2

    def shouldAdd2PackagesToPackageList(self):
        imp = self.imp
        table = Parse("<table><tr><td>fit.Import</td></tr>"
                    "<tr><td>tests</td><td></td></tr>"
                    "<tr><td>fitLib</td></tr></table>")
        imp.doRows(table.parts.more)
        assert imp.fixtureLoader._rememberedPackages[1] == "tests"
        assert imp.fixtureLoader._rememberedPackages[2] == "fitLib"
        assert len(imp.fixtureLoader._rememberedPackages) == 3

    def shouldAddRenameToRenameTable(self):
        imp = self.imp
        key = "fitnesse.fixtures"
        value = "fitnesse"
        assert FixtureLoader._fixtureRenameTable.get(key) is None
        table = Parse("<table><tr><td>fit.Import</td></tr>"
                    "<tr><td>fitnesse.fixtures</td><td>fitnesse</td></tr>"
                    "</table>")
        imp.doRows(table.parts.more)
        assert FixtureLoader._fixtureRenameTable.get(key) == value

if __name__ == '__main__':
    main(defaultTest='makeMiscTest')
