# SequenceFixtureUnderTest from FitLibrary Acceptance Tests
#legalStuff rm03 jr05-06
# Original version Contains code developed by Rick Mugridge.
# University of Auckland, NZ. Copyright 2003 Rick Mugridge.
# Released under the terms of the General Public License (GPL), Release 2.1 or later
# See license.txt for terms and disclaimer of all warrenties and liability.
# changes Copyright 2005-2006 John H. Roth Jr.
# Last updated for Release 0.8a1
#endLegalStuff

from fitLib.SequenceFixture import SequenceFixture
from fitLib.specify.SystemUnderTest import SystemUnderTest

class SequenceFixtureUnderTest(SequenceFixture):
    def __init__(self):
        SequenceFixture.__init__(self, SystemUnderTest())
    _typeDict = {}

    def specialAction(self, cells):
        cells = cells.more
        if cells.text() == "right":
            self.right(cells)
        elif cells.text() == "wrong":
            self.wrong(cells)
    specialAction.fitLibSpecialAction = True

    _typeDict["hiddenMethod.types"] = [None]
    def hiddenMethod(self):
        return

