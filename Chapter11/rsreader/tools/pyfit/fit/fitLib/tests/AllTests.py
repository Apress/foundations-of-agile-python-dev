# Invoke all FitLibrary unit tests.
#legalStuff jr04
# Copyright 2004 John H. Roth Jr.
# Released under the terms of the General Public License (GPL), Release 2.1 or later
# See license.txt for terms and disclaimer of all warrenties and liability.
# Last updated for Release 0.8a1
#endLegalStuff

# import sys

import unittest
from fitLib.tests import CalculateFixtureTest
from fitLib.tests import FlowFixtureFixtureTest
from fitLib.tests import TestListTree
from fitLib.tests import TestParseUtility

try:
    False
except:
    True = 1
    False = 0

def makeAllTests():
    suite = CalculateFixtureTest.makeCalculateFixtureSpecifications()
    suite.addTests((FlowFixtureFixtureTest.makeFlowFixtureFixtureTest(),))
    suite.addTests((TestListTree.makeListTreeTest(),))
    suite.addTests((TestParseUtility.makeParseUtilityTest(),))
    return suite

if __name__ == '__main__':
    unittest.main(defaultTest='makeAllTests')
