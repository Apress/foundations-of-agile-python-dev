# DoFixtureFlowUnderTest from FitLibrary Specification Tests
#legalStuff rm03 jr05-06
# Original version Contains code developed by Rick Mugridge.
# University of Auckland, NZ. Copyright 2003 Rick Mugridge.
# Released under the terms of the General Public License (GPL), Release 2.1 or later
# See license.txt for terms and disclaimer of all warrenties and liability.
# changes Copyright 2005-2006 John H. Roth Jr.
# Last updated for Release 0.8a1
#endLegalStuff

from fit.ColumnFixture import ColumnFixture
from fit.Fixture import Fixture
from fit.Parse import Parse
from fit.RowFixture import RowFixture
from fitLib.DoFixture import DoFixture
from fitLib.SequenceFixture import SequenceFixture
from fitLib.specify.SystemUnderTest import SystemUnderTest

class MyColumnFixture(ColumnFixture): # Static class
    _typeDict = {"x": "Int"}
    x = 0

    def __init__(self, initial):
        self.x = initial

    _typeDict["getX"] = "Int"
    def getX(self):
        return self.x

class Local:
    _typeDict = {"s": "String"}
    s = ""

    def __init__(self, s):
        self.s = s

class LocalRowFixture(RowFixture):
    rows = [[[Local("A0a"), Local("A0b")],
             [Local("A1a"), Local("A1b")],
             [Local("A2a"), Local("A2b")],
             [Local("A3a"), Local("A3b")],
             ],[
             [Local("B0a"), Local("B0b")],
             [Local("B1a"), Local("B1b")],
             [Local("B2a"), Local("B2b")],
             [Local("B3a"), Local("B3b")],
             ]]
            
    row = 0
    column = 0

    def __init__(self, row, column):
        self.row = row
        self.column = column
        super(LocalRowFixture, self).__init__()

    def query(self):
        return self.rows[self.row][self.column]

    def getTargetClass(self):
        return Local

class SequenceFixtureFlowUnderTest(SequenceFixture):
    _typeDict = {}
    DATE_FORMAT = "yyyy/MM/dd HH:mm"

    def __init__(self):
        DoFixture.__init__(self, SystemUnderTest())

    _typeDict["specialAction.types"] = [None, "$Parse"] # command!
    def specialAction(self, cells):
        cells = cells.more
        if cells.text() == "right":
            self.right(cells)
        elif cells.text() == "wrong":
            self.wrong(cells)
    specialAction.fitLibSpecialAction = True


    _typeDict["fixtureObject.types"] = ["$SUT", "Int"]
    def fixtureObject(self, initial):
        return MyColumnFixture(initial)

    _typeDict["hiddenMethod.types"] = [None]
    def hiddenMethod(self):
        pass

    _typeDict["getSlice.types"] = ["$SUT", "Int", "Int"]
    def getSlice(self, row, column):
        return LocalRowFixture(row, column)
