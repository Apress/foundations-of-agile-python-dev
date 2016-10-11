# test module for Python Translation of DoFixture
# copyright 2005, John H. Roth Jr. Licensed under the terms of the
# GNU Public License, Version 2. See license.txt for conditions and
# exclusion of all warrenties.

import unittest
from fitLib.DoFixture import FlowFixture, DoFixture
from fitLib.FitLibraryFixture import FitLibraryFixture

try:
    False
except:
    True = 1
    False = 0

def makeDoFixtureTest():
    theSuite = unittest.makeSuite(Test_DoFixture, 'test')
#    theSuite.addTest(unittest.makeSuite(Test_FooBar, 'Test'))
    return theSuite

class Test_DoFixture(unittest.TestCase):
    def setUp(self):
        print '%s %s' % (self.id(), self.shortDescription())

    def tearDown(self):
        pass

if __name__ == '__main__':
    unittest.main(defaultTest='makeDoFixtureTest')
