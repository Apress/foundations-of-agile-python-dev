# Test Fixtture for parse exit facility
#legalStuff jr04-05
# Copyright 2004-2005 John H. Roth Jr.
# Released under the terms of the General Public License (GPL), Release 2.1 or later
# See license.txt for terms and disclaimer of all warrenties and liability.
# Last updated for Release 0.8a1
#endLegalStuff

from fit.Fixture import Fixture
from fit.TypeAdapter import on as Adapter

class ParseExit(Fixture):
    aValue = None # pychecker complains if this is missing

    def doRows(self, rows):
        Fixture.doRows(self, rows.more)

    def doCell(self, cell, column):
        if column == 0:
            self.adapter= Adapter(self, "aValue", {"aValue": cell.text().title()})
        elif column == 1:
            self.setUpExit(cell)
        elif column == 2:
            parsed = self.adapter.parse(cell.text())
            self.adapter.set(parsed)
        elif column == 3:
            if self.adapter.get() == cell.text():
                self.right(cell)
            else:
                self.wrong(cell, self.adapter.get())
        elif column == 4:
            self.setUpExit(cell)
        elif column == 5:
            expected = self.adapter.parse(cell.text())
            if self.adapter.equals(self.aValue, expected):
                self.right(cell,)
            else:
                self.wrong(cell, self.adapter.toString(self.aValue))
        else:
            return

    def setUpExit(self, cell):
        exitName = cell.text()
        if exitName == "":
            self.adapter.clearParseExit()
        else:
            parseExit = getattr(self, exitName) # does this get a bound method?
            self.adapter.setParseExit(parseExit)

    def reverse(self, value):
        aList = []
        for char in value:
            aList.append(char)
        aList.reverse()
        return "OK", "".join(aList)

    def sort(self, value):
        aList = []
        for char in value:
            aList.append(char)
        aList.sort()
        return "OK", "".join(aList)


