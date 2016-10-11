# Test module for FlowFixtureFixture from FitLibrary
# Developed by Rick Mugridge
# Copyright 2004 Rick Mugridge, University of Auckland, NZ
# Released under the terms of the GNU General Public License version 2 or later.
# Translation to Python copyright 2005 John H. Roth Jr.

import sys

def em(msg):
    if msg[1] != "\n":
        msg += "\n"
    sys.stderr.write(msg)

import unittest
from fit.Parse import Parse
from fitLib.FlowFixtureFixture import FlowFixtureFixture

try:
    False
except:
    True = 1
    False = 0

def makeFlowFixtureFixtureTest():
    theSuite = unittest.makeSuite(Test_FlowFixtureFixture, 'test')
#    theSuite.addTest(unittest.makeSuite(Test_FooBar, 'Test'))
    return theSuite

class Test_FlowFixtureFixture(unittest.TestCase):
    def setUp(self):
        print '%s %s' % (self.id(), self.shortDescription())

    def testMakeEmbeddedTable(self):
        cells = self.td("", self.td("a", None))
        rows = self.tr(cells, None)
        table = Parse(tag="table", parts=rows)
        result = FlowFixtureFixture().makeEmbeddedRows(table.parts)
        self.assertEquals("a", result.parts.parts.text())
        assert result.more is None
        assert result.parts.more is None
        assert result.parts.parts.more is None

    def testMakeEmbeddedTable2(self):
        cells = self.td("", self.td("a", self.td("b", None)))
        rows = self.tr(cells, None)
        table = Parse(tag="table", parts=rows)
        result = FlowFixtureFixture().makeEmbeddedRows(table.parts)
        self.assertEquals("a", result.parts.parts.text())
        self.assertEquals("b", result.parts.parts.more.text())
        assert result.more is None
        assert result.parts.more is None
        assert result.parts.parts.more.more is None

    def testMakeEmbeddedTables(self):
        cells = self.td("", self.td("a", self.td("b", None)))
        rows = self.tr(cells, self.tr(cells, None))
        tables = Parse(tags="table", parts=rows)
        resultingTable = FlowFixtureFixture().makeEmbeddedTables(tables)
        self.assertEquals("a", resultingTable.parts.parts.text())
        self.assertEquals("b", resultingTable.parts.parts.more.text())
        assert resultingTable.more is None
        assert resultingTable.parts.more is None
        assert resultingTable.parts.parts.more.more is None
        
        self.assertEquals(tables.parts.parts.more, resultingTable.parts.parts)

    def tr(self, cells, more):
        return Parse(tag="tr", parts=cells, more=more)

    def td(self, s, more):
        return Parse(tag="td", body=s, more=more);

    def tearDown(self):
        pass

if __name__ == '__main__':
    unittest.main(defaultTest='makeFlowFixtureFixtureTest')
