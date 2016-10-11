# SetUpFixtureUnderTest from FitLibrary Acceptance Tests
#legalStuff rm04 jr05
# Original version Contains code developed by Rick Mugridge.
# University of Auckland, NZ. Copyright 2004 Rick Mugridge.
# Released under the terms of the General Public License (GPL), Release 2.1 or later
# See license.txt for terms and disclaimer of all warrenties and liability.
# changes Copyright 2005 John H. Roth Jr.
# Last updated for Release 0.8a1
#endLegalStuff

from fitLib.SetUpFixture import SetUpFixture

class SetUpFixtureUnderTest(SetUpFixture):
    _typeDict = {}
    
    _typeDict["aB.types"] = [None, "Int", "Int"]
    def aB(self, a, b):
        __pychecker__ = "no-argsused"
        if a < 0:
            raise Exception, "Testing..."
