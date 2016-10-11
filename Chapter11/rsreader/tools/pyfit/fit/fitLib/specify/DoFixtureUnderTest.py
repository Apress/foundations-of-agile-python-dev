# DoFixtureUnderTest from Acceptance Tests for FitLibrary
#legalStuff rm04 jr05-06
# Original version Contains code developed by Rick Mugridge.
# University of Auckland, NZ. Copyright 2004 Rick Mugridge.
# Released under the terms of the General Public License (GPL), Release 2.1 or later
# See license.txt for terms and disclaimer of all warrenties and liability.
# changes Copyright 2005-2006 John H. Roth Jr.
# Last updated for Release 0.8a1
#endLegalStuff

from fitLib.DoFixture import DoFixture
from fitLib.specify.StartDoSpecification import StartDoSpecification

class DoFixtureUnderTest(DoFixture):
    _typeDict = {}
    def __init__(self):
        SUT = StartDoSpecification().SUT
        DoFixture.__init__(self, SUT)

    # !!! specialAction doesn't have any metadata because
    #     it's a fixture action, not a SUT method.
    # --> However, it has a custom attribute on the method.
    def specialAction(self, cells):
        cells = cells.more
        if cells.text() == "right":
            self.right(cells)
        elif cells.text() == "wrong":
            self.wrong(cells)
    specialAction.fitLibSpecialAction = True


    _typeDict["hiddenMethod.types"] = [None]
    def hiddenMethod(self):
        return None
