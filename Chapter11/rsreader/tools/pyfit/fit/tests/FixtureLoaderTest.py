# test module for FixtureLoader
#legalStuff jr05
# Copyright 2005 John H. Roth Jr.
# Released under the terms of the General Public License (GPL), Release 2.1 or later
# See license.txt for terms and disclaimer of all warrenties and liability.
# Last updated for Release 0.8a1
#endLegalStuff

from unittest import makeSuite, TestCase, main

from fit import FitGlobal
from fit.FixtureLoader import FixtureLoader
from fit.FitException import FitException
import fit.Fixture
from fit.Options import Options
from fit.SiteOptions import BatchBase
from fit import Variations

try:
    False
except:
    True = 1
    False = 0

def makeFixtureLoaderTest():
    theSuite = makeSuite(Test_FixtureLoaderInitialization, 'test')
    theSuite.addTests([
        makeSuite(Test_FixtureLoader, "test"),
        makeSuite(TestFixtureLoaderWithAppExit, "should"),
        ])
    return theSuite

class Test_FixtureLoaderInitialization(TestCase):
    def setUp(self):
        print '%s %s' % (self.id(), self.shortDescription())

    def testInitialContentOfRememberedPackagesCache(self):
        obj = FixtureLoader()
        assert obj._rememberedPackages.index("fit") == 0
    
class Test_FixtureLoader(TestCase):
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
##        it = getattr(FixtureLoader, "__it__", None)
##        if it is not None:
##            del FixtureLoader.__it__ 
        self.obj = FixtureLoader()
        FixtureLoader.clearFixtureRenameTable()

    def testAddToRenameTable(self):
        obj = self.obj
        assert not hasattr(obj._fixtureRenameTable, "spam")
        obj.addRenameToRenameTable("spam", "eggs")
        assert obj._fixtureRenameTable["spam"] == "eggs"

    def testLoadOfFixtureRenameTable(self):
        loader = self.obj
        assert len(loader._fixtureRenameTable) == 0
        loader.loadFixtureRenameTable(["spam: eggs\n",
                                       "foo: bar"
                                       ])
        assert len(loader._fixtureRenameTable) == 2
        assert loader._fixtureRenameTable["spam"] == "eggs"
        assert loader._fixtureRenameTable["foo"] == "bar"

    def testLoadOfFixtureRenameTableWithComment(self):
        loader = self.obj
        assert len(loader._fixtureRenameTable) == 0
        loader.loadFixtureRenameTable(["spam: eggs\n",
                                       "#This is: a comment",
                                       "foo: bar"
                                       ])
        assert len(loader._fixtureRenameTable) == 2
        assert loader._fixtureRenameTable["spam"] == "eggs"
        assert loader._fixtureRenameTable["foo"] == "bar"

    def test_loadFixtureRenameTable(self):
        testList = ["fit.fat: exercise", "foo.bar: spam", "foo: ham",
                     "spam.eggs: vikingChow"]
        self.obj.loadFixtureRenameTable(testList)
        assert len(self.obj._fixtureRenameTable) == 4
        dList = ["%s: %s" % (key, value) for key, value in 
                    self.obj._fixtureRenameTable.items()]
        dList.sort()
        assert dList == testList

    def test_renameFixtureName(self):
        testList = ["fit.fat: exercise", "foo: ham", "foo.bar: spam",
                     "spam.eggs: vikingChow"]
        self.obj.loadFixtureRenameTable(testList)
        assert self.obj._renameFixture("foo.bar.fefifofum") == "spam.fefifofum"
        assert self.obj._renameFixture("foo.fiddle") == "ham.fiddle"

    def testExactRenameMatch(self):
        loader = self.obj
        testList = ["laurel.hardy: fit.ColumnFixture",]
        loader.loadFixtureRenameTable(testList)
        fixture = loader.loadFixture("laurel.hardy")
        assert fixture.__name__ == "ColumnFixture"

    def test_isGracefulName(self):
        assert self.obj.isGracefulName("foo bar")
        assert self.obj.isGracefulName("spam") is False
        assert self.obj.isGracefulName("spam.eggs") is False
        assert self.obj.isGracefulName("spam. eggs") is False
        assert self.obj.isGracefulName("spam. eggs.toast") is False

    def test_unGracefulName(self):
        assert self.obj.unGracefulName("foo'bar") == "Foobar"
        assert self.obj.unGracefulName("foo bar") == "FooBar"
        assert self.obj.unGracefulName("foo48bar") == "Foo48Bar"
        assert self.obj.unGracefulName("spam. eggs") == "Spam.Eggs"
        assert self.obj.unGracefulName("spam:eggs.toast") == "SpamEggs.Toast"

    def testOneLevelNameExists(self):
        loader = self.obj
        try:
            loader.loadFixture("FileRunner")
        except FitException, e:
            isExc, doTrace, result = e.getMeaningfulMessage()
            print result
            if result == ('"FileRunner" was found, but it\'s not a fixture.'):
                return
            raise
        assert False, "Accepted a non-Fixture object as a fixture"

    def testLoadViaGracefulNameAndRememberedPackage(self):
        loader = self.obj
        loader.loadFixture("column fixture")

    def testTwoLevelModuleNameNoClassName(self):
        loader = self.obj
        fixture = loader.loadFixture("fit.Fixture")
        print fixture
        assert fixture is fit.Fixture.Fixture

    def testThreeLevelModuleNameNoClassName(self):
        loader = self.obj
        fixture = loader.loadFixture("fitLib.specify.DoFixtureUnderTest")
        print fixture
        assert issubclass(fixture, fit.Fixture.Fixture)
        assert fixture.__name__ == "DoFixtureUnderTest"

    def testThreeLevelModuleNameWithClassName(self):
        loader = self.obj
        fixture = loader.loadFixture(
            "fitLib.specify.DoFixtureFlowUnderTest.MyColumnFixture")
        print fixture
        assert issubclass(fixture, fit.Fixture.Fixture)
        assert fixture.__name__ == "MyColumnFixture"

    def tearDown(self):
        FixtureLoader.clearFixtureRenameTable()
        FitGlobal.RunOptions, FitGlobal.Options, FitGlobal.Environment = \
                              self.saveFitGlobal

class MockAppConfigMapFixture(object):
    def mapFixture(self, text):
        if text == "doric column":
            return "ColumnFixture"
        if text == "ionic column":
            return "fit.ColumnFixture"
        return None

class TestFixtureLoaderWithAppExit(TestCase):
    def setUp(self):
        print '%s %s' % (self.id(), self.shortDescription())
        self.options = Options(["FileRunner", "+v", "+e", "foo", "bar"],
                               BatchBase.parmDict)
        self.saveFitGlobal = (FitGlobal.RunOptions, FitGlobal.Options,
                              FitGlobal.Environment)
        self.saveAppExit = (FitGlobal.appConfigModule, FitGlobal.appConfig)
        FitGlobal.RunOptions = self.options
        FitGlobal.Options = self.options
        FitGlobal.Environment = "Batch"
        FitGlobal.appConfigModule = MockAppConfigMapFixture
        FitGlobal.appConfig = MockAppConfigMapFixture()
        Variations.returnVariation()
        self.obj = FixtureLoader()
        FixtureLoader.clearFixtureRenameTable()

    def tearDown(self):
        FixtureLoader.clearFixtureRenameTable()
        FitGlobal.RunOptions, FitGlobal.Options, FitGlobal.Environment = \
                              self.saveFitGlobal
        FitGlobal.appConfigModule, FitGlobal.appConfig = self.saveAppExit

    def shouldRaiseExceptionWithSingleElementName(self):
        loader = self.obj
        self.assertRaises(FitException, loader.loadFixture, "doric column")
        
    def shouldTranslateName(self):
        loader = self.obj
        fixture = loader.loadFixture("ionic column")
        assert fixture.__name__ == "ColumnFixture"
        


if __name__ == '__main__':
    main(defaultTest='makeFixtureLoaderTest')
