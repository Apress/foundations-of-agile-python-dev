# ArrayFixtureUnderTestWithMap from FitLibrary Specification Tests
#legalStuff rm03 jr05
# Original version Contains code developed by Rick Mugridge.
# University of Auckland, NZ. Copyright 2003 Rick Mugridge.
# Released under the terms of the General Public License (GPL), Release 2.1 or later
# See license.txt for terms and disclaimer of all warrenties and liability.
# changes Copyright 2005 John H. Roth Jr.
# Last updated for Release 0.8a1
#endLegalStuff

from fitLib.ArrayFixture import ArrayFixture

class ArrayFixtureUnderTestWithMap(ArrayFixture):
    _typeDict = {"plus": "Int",
                 "ampersand": "String"
                 }
        
    def query(self):
        result = []
        result.append(self.makeMap(1, "one"))
        result.append(self.makeMap(1, "two"))
        result.append(self.makeMap(2, "two"))
        return result

    def makeMap(self, plus, ampersand):
        return {"plus": plus,
               "ampersand": ampersand
               }
