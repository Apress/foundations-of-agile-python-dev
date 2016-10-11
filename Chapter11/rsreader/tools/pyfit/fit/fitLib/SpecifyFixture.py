# SpecifyFixture from FitLibrary
# Copyright 2005 Rick Mugridge, University of Auckland, NZ
# Released under the terms of the GNU General Public License, version 2 or later.
# Translation to Python copyright 2005, John H. Roth Jr.

import sys
from fit.Fixture import Fixture
from fit.Parse import Parse
from fitLib import ParseUtility

try:
    False
except:
    True = 1
    False = 0

# Uses embedded tables to specify how fixtures work, based on
# simple subclasses of those fixtures.

class SpecifyFixture(Fixture):
    def doTable(self, table):
        actual = table.parts.more.parts.parts
        expectedCell = table.parts.more.more.parts
        expected = expectedCell.parts
        Fixture().doTables(actual)
        if self.reportsEqual(actual, expected):
            self.right(expectedCell)
        else:
            self.wrong(expectedCell)
            ParseUtility.printParse(actual, "actual")

    def reportsEqual(self, p1, p2):
        if p1 is None:
            return p2 is None
        if p2 is None:
            return False
        result = (self.equalTags(p1, p2) and
            self.equalStrings(p1.leader, p2.leader) and
            self.equalBodies(p1, p2) and
            self.equalStrings(p1.trailer, p2.trailer) and
            self.reportsEqual(p1.more, p2.more) and
            self.reportsEqual(p1.parts, p2.parts))
        return result

    def equalBodies(self, p1, p2):
        body2 = p2.body
        if p1.body is None:
            return body2 is None
        if body2 is None:
            return False
        if body2 == "IGNORE":
            return True
        if p1.body == body2:
            return True
        stackTrace = "class=\"fit_stacktrace\">"
        if body2.indexOf(stackTrace) >= 0:
            end = body2.find("</div>")
            pattern = body2[:end]
            return p1.body.startswith(pattern)
        return False

    def equalTags(self, p1, p2):
        return p1.tag == p2.tag

    def equalStrings(self, s1, s2):
        if s1 is None:
            return s2 is None or s2.strip() == "" or s2 == "\n"
        if s2 is None:
            return s1.strip() == "" or s1 == "\n"
        return s1.strip() == s2.strip()
