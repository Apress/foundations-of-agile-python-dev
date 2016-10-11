# test module for Python Translation of CalculateFixture
# copyright 2005, John H. Roth Jr. Licensed under the terms of the
# GNU Public License, Version 2. See license.txt for conditions and
# exclusion of all warrenties.

import unittest
from fit.Parse import Parse
from fit import InitEnvironment
from fit.Utilities import em
from fitLib.CalculateFixture import CalculateFixture

try:
    False
except:
    True = 1
    False = 0

def makeCalculateFixtureSpecifications():
    suite = unittest.TestSuite()
    suite.addTests([SpecifyCalculateFixture(x) for x in [
        "twoGiven1Result1Comment",
        "twoGivenNoName1Result1Comment",
        "throwExceptionIfRowIsWrongWidth",
        ]])
    return suite

class CalculateFixtureExample(CalculateFixture):
    _typeDict = {"breakfastSpamEggs.types": ["Boolean", "Boolean", "Boolean"]}
    def breakfastSpamEggs(self, spam, eggs):
        return spam == eggs

class SpecifyCalculateFixture(unittest.TestCase):
    def setUp(self):
        print '%s %s' % (self.id(), self.shortDescription())

    def makeRow(self, html):
        return Parse(html, ["tr", "td"])

    def numberOfAnnotationsInRow(self, row):
        num = 0
        cell = row
        cellNum = 0
        while cell is not None:
            if (cell.tag.find("bgcolor=") != -1 or
                cell.tag.find("class=") != -1):
##                em("\nin numberOfAnnotationsInRow. \ntag: %s \n body: %s"
##                   % (cell.tag, cell.body))
                num += 1
            cell = cell.more
            cellNum += 1
        return num

    def twoGiven1Result1Comment(self):
        row = self.makeRow(
            "<tr><td>spam</td><td>eggs</td><td> </td>"
            "<td>breakfast</td> <td></td><td>notes</td></tr>")
        obj = CalculateFixtureExample()
        obj.bind(row.parts)
        assert self.numberOfAnnotationsInRow(row.parts) == 0
        assert obj.methods == 1

    def twoGivenNoName1Result1Comment(self):
        row = self.makeRow(
            "<tr><td></td><td></td><td> </td>"
            "<td>breakfast spam eggs</td> <td></td><td>notes</td></tr>")
        obj = CalculateFixtureExample()
        obj.bind(row.parts)
        assert self.numberOfAnnotationsInRow(row.parts) == 0
        assert obj.methods == 1

    def throwExceptionIfRowIsWrongWidth(self):
        obj = CalculateFixtureExample()
        headerRow = self.makeRow(
            "<tr><td></td><td></td><td> </td>"
            "<td>breakfast spam eggs</td> <td></td><td>notes</td></tr>")
        obj.bind(headerRow.parts)
        dataRow = self.makeRow("<tr><td>one</td><td>two</td></tr>")
        obj.doRow(dataRow)
        assert self.numberOfAnnotationsInRow(dataRow.parts) == 1
        assert dataRow.parts.body.find("Row should be 6 columns wide") != 0

    def tearDown(self):
        pass

if __name__ == '__main__':
    unittest.main(defaultTest='makeCalculateFixtureSpecifications')
