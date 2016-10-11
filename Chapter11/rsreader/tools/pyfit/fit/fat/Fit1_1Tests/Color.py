# Copyright (c) 2002 Cunningham & Cunningham, Inc.
# Released under the terms of the GNU General Public License version 2 or later.
# Port to Python copyright 2004 John H. Roth Jr.

# This beast works with the Table fixture to check the colors
# in the result tables. It depends on Table storing the head
# of the result table in its class object.

from fit.PrimitiveFixture import PrimitiveFixture
from fit.Fixture import Fixture

class Color(PrimitiveFixture):

    actualRow = None

    def doRows(self, rows):
        table = self.getSymbol("Table")
        self.actualRow = table.parts
        if rows.size() != self.actualRow.size():
            raise Exception, "wrong size table"
        Fixture.doRows(self, rows)

    def doRow(self, row):
        Fixture.doRow(self, row)
        self.actualRow = self.actualRow.more

    def doCell(self, cell, columnNumber):
        actualColor = self.color(self.actualRow.parts.at(columnNumber))
        self.doCheck(cell, cell.body.strip(), actualColor)

    def color(self, cell):
        b = self.extract(cell.tag, "bgcolor=\"", "white")
        f = self.extract(cell.body, "<font color=", "black")
        if f == "black": return b
        return "%s/%s" % (f, b)

    def extract(self, text, unused, defaultColor):
        index = text.find('class="')
        if index < 0: return defaultColor
        index += 7
        endIndex = text.find('"', index)
        extracted = text[index:endIndex]
        return self._styleDict.get(extracted, defaultColor)

    _styleDict = {"pass": "green",
                 "fail": "red",
                 "error": "yellow",
                 "ignore": "gray",
                 "fit_pass": "green",
                 "fit_fail": "red",
                 "fit_error": "yellow",
                 "fit_ignore": "gray",
                 "fit_stacktrace": "black",
                 "fit_label": "black",
                 "fit_grey": "gray",
                 "fit_green": "black"
                 }

    def decode(self, code):
        if code[0] == "#": code = code[1:]
        if   code == Fixture.redColor: return "red"
        elif code == Fixture.greenColor: return "green"
        elif code == Fixture.yellowColor: return "yellow"
        elif code == Fixture.grayColor: return "gray"
        elif code == Fixture.grayLabelColor: return "gray"
        return code

    def doCheck(self, cell, expected, actual):
        if expected.startswith("<p>"):
            expected = expected[3:-4].strip()
##        print "in Color.check. expected: '%s' actual: '%s'" % (
##            expected, actual)
        if expected == actual:
            self.right(cell)
        else:
            self.wrong(cell, actual)
