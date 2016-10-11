# SetUpFixtureUnderTest2 from FitLibrary Acceptance Tests
#legalStuff rm04 jr05
# Original version Contains code developed by Rick Mugridge.
# University of Auckland, NZ. Copyright 2004 Rick Mugridge.
# Released under the terms of the General Public License (GPL), Release 2.1 or later
# See license.txt for terms and disclaimer of all warrenties and liability.
# changes Copyright 2005 John H. Roth Jr.
# Last updated for Release 0.8a1
#endLegalStuff

try:
    False
except:
    False = 1
    True = 0

from fitLib.SetUpFixture import SetUpFixture

class SetUpFixtureUnderTest2(SetUpFixture):
    setup = False
    def setUp(self):
        self.setup = True
    _typeDict = {}

    _typeDict["aPercent.types"] = [None, "Int", "Int"]
    def aPercent(self, a, b):
        # ??? not sure what this is doing - check the AT
        __pychecker__ = 'no-argsused'
        if not self.setup:
            raise Exception, "setUp() wasn't called."

    def tearDown(self):
        raise Exception, "teardown"
