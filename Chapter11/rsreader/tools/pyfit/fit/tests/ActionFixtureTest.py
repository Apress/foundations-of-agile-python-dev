# test module for ActionFixture
#LegalStuff jr05
# Copyright 2005 John H. Roth Jr.
# Released under the terms of the General Public License (GPL), Release 2.1 or later
# See license.txt for terms and disclaimer of all warrenties and liability.
# Last updated for Release 0.8a1
#endLegalStuff

# There don't appear to be any tests for ActionFixture in FrameworkTest
# since that starts out with a flat zero statement coverage.

import types
from unittest import makeSuite, TestCase, main
from fit.ActionFixture import ActionFixture
from fit import FitGlobal
from fit import InitEnvironment
from fit.Fixture import Fixture
from fit.Parse import Parse
from fit.Utilities import em

try:
    False
except: #pragma: no cover
    True = 1
    False = 0

def makeActionFixtureTest():
    theSuite = makeSuite(ActionFixtureTests, 'should')
#    theSuite.addTest(makeSuite(SpecifyFoo, "should"))
    return theSuite

class MockActor(Fixture):
    _typeDict = {"entryWidgit": "String",
                 "bigRedButton": "Int",
                 "littleGreenButton": "Int"}

    entryWidgit = ""
    bigRedButtonPressed = False

    def bigRedButton(self):
        self.bigRedButtonPressed = True

    def littleGreenButton(self):
        raise Exception("Expected Test Exception")
        
class NotAFixture(object):
    _typeDict = {"entryWidgit": "String",
                 "bigRedButton": "Int"}

    entryWidgit = ""
    bigRedButtonPressed = False

    def bigRedButton(self):
        self.bigRedButtonPressed = True

class ActionFixtureTests(TestCase):
    def setUp(self):
        print '%s %s' % (self.id(), self.shortDescription())
        FitGlobal.Environment = "Batch"
        ActionFixture.actor = None
        ActionFixture.cells = None
        self.af = ActionFixture()

    def tearDown(self):
        pass

    def makeCells(self, text):
        parts = text.split("|")
        firstCell = lastCell = Parse(tag="td")
        for body in parts:
            lastCell.more = Parse(tag="td", body=body)
            lastCell = lastCell.more
        return firstCell.more

    def _printCells(self, cells):
        em("\n cells for %s" % self.id())
        while cells is not None:
            em("-- tag: %s body: %s" % (cells.tag, cells.body))
            cells = cells.more

    def shouldSetUpActorOnEnter(self):
        af = self.af
        cells = self.makeCells("start|tests.ActionFixtureTest.MockActor|")
        af.doCells(cells)
        assert ActionFixture.actor is not None
        assert af.cells == cells

    def shouldRaiseErrorIfActorNameCellMissing(self):
        af = self.af
        cells = self.makeCells("start")
        af.doCells(cells)
        assert cells.tagIsError()
        assert cells.body.find("Cell containing actor name is missing") > -1

    def shouldRaiseErrorIfActorIsNotAFixture(self):
        af = self.af
        cells = self.makeCells("start|tests.ActionFixtureTest.NotAFixture|")
        af.doCells(cells)
##        em("tag: '%s' body: '%s'" % (cells.more.tag, cells.more.body))
        assert cells.more.tagIsError()
        assert cells.more.body.find("found, but it's not a fixture") > -1

    def shouldRaiseErrorIfActorNameMissing(self):
        af = self.af
        cells = self.makeCells("start|")
        af.doCells(cells)
        assert cells.tagIsError()
        assert cells.body.find("must specify a fixture to start") > -1

    def shouldEnterData(self):
        af = self.af
        cells = self.makeCells("enter|entry widgit|an entry")
        ActionFixture.actor = MockActor()
        af.doCells(cells)
        assert cells.more.more.tagIsNotAnnotated()
        assert ActionFixture.actor.entryWidgit == "an entry"

    def shouldRaiseExceptionIfEntryDataCellMissing(self):
        af = self.af
        cells = self.makeCells("enter|entry widgit")
        ActionFixture.actor = MockActor()
        af.doCells(cells)
        assert cells.tagIsError()
        assert cells.body.find("data to enter or check") > -1

    def shouldRaiseWrongOnInvalidCommand(self):
        af = self.af
        cells = self.makeCells("larry|moe|curly")
        ActionFixture.actor = MockActor()
        af.doCells(cells)
        assert cells.tagIsWrong()
        assert cells.body.find("Command 'larry' not recognized") > -1

    def shouldRaiseExceptionOnInvalidMethodName(self):
        af = self.af
        cells = self.makeCells("enter|Thunderbolt|in Preakness")
        ActionFixture.actor = MockActor()
        af.doCells(cells)
        assert cells.more.tagIsError()
        assert cells.more.body.find(
            "Metadata for 'Thunderbolt' not found in class 'MockActor'") > -1

    def shouldPressTheBigRedButton(self):
        af = self.af
        cells = self.makeCells("press|big red button|ignored")
        ActionFixture.actor = MockActor()
        af.doCells(cells)
#        assert cells.more.tagIsRight()
        assert cells.more.tagIsNotAnnotated()
        assert ActionFixture.actor.bigRedButtonPressed

    def shouldGetExceptionIfWePressTheLittleGreenButton(self):
        af = self.af
        cells = self.makeCells("press|little green button|ignored")
        ActionFixture.actor = MockActor()
        af.doCells(cells)
        assert cells.more.tagIsError()
        assert cells.more.body.find("Expected Test Exception") > -1

    def shouldCheckThatEntryWidgitContainsCorrectData(self):
        af = self.af
        cells = self.makeCells("check|entry Widgit|correct data")
        ActionFixture.actor = MockActor()
        ActionFixture.actor.entryWidgit = "correct data"
        af.doCells(cells)
        assert cells.more.more.tagIsRight()

    def shouldRaiseErrorIfDataCellToCheckIsMissing(self):
        af = self.af
        cells = self.makeCells("check|entry Widgit")
        ActionFixture.actor = MockActor()
        af.doCells(cells)
        assert cells.tagIsError()
        assert cells.body.find("data to enter or check") > -1

if __name__ == '__main__':
    main(defaultTest='makeActionFixtureTest')
