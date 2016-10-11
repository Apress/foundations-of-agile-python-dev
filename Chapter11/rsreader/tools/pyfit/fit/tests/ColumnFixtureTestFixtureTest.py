# test module for ColumnFixtureTestFixture
# copyright 2004, John H. Roth Jr. Licensed under the terms of the
# GNU Public License, Version 2. See license.txt for conditions and
# exclusion of all warrenties.

import unittest
from fitnesse.fixtures.ColumnFixtureTestFixture import ColumnFixtureTestFixture

try:
    False
except:
    True = 1
    False = 0

def makeColumnFixtureTestFixtureTest():
    theSuite = unittest.makeSuite(Test_ColumnFixtureTestFixture, 'Test')
#    theSuite.addTest(unittest.makeSuite(SpecifyFoo, 'Test'))
    return theSuite

class Test_ColumnFixtureTestFixture(unittest.TestCase):
    def setUp(self):
        print '%s %s' % (self.id(), self.shortDescription())

    def Test_it(self):
        obj = ColumnFixtureTestFixture()
        obj.input = 1
        assert obj.output() == 1

    def tearDown(self):
        pass

if __name__ == '__main__':
    unittest.main(defaultTest='makeColumnFixtureTestFixtureTest')
