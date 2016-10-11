# Test Harness for FixtureFixture, depreciated part of FitLibrary
# Copyright 2004, Rick Migridge, University of Auckland, NZ
# Released under the terms of the GNU General Public License version 2 or later.
# Translation to Python copyright 2005, John H. Roth Jr.

import unittest
from fit.Parse import Parse
from fitLib import ParseUtility
from fit.Fixture import Fixture
from fitLib.FixtureFixture import FixtureFixture

try:
    False
except:
    True = 1
    False = 0

def makeFixtureFixtureTest():
    theSuite = unittest.makeSuite(FixtureFixtureTest, 'test')
#    theSuite.addTest(unittest.makeSuite(Test_FooBar, 'Test'))
    return theSuite

class FixtureFixtureTest(unittest.TestCase):
    def test1(self):
        table = Parse("<table><tr><td>fit.ff.FixtureUnderTest</td>"
                "<td>r</td>"
                "</tr></table>\n")
        Fixture().doTables(table)
        ParseUtility.printParse(table, "test")

if __name__ == '__main__':
    unittest.main(defaultTest='makeFixtureFixtureTest')

