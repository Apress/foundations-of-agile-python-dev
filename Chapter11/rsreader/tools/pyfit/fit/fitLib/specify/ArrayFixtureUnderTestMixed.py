# ArrayFixtureUnderTestMixed from FitLibrary Specification Tests
# Developed by Rick Mugridge
# Copyright 2004 Rick Mugridge, University of Auckland, NZ
# Released under the terms of the GNU General Public License version 2 or later.
# Translation to Python copyright 2005 John H. Roth Jr.

from fitLib.ArrayFixture import ArrayFixture
from fitLib.specify.MockCollection import MockCollection

class ArrayFixtureUnderTestMixed(ArrayFixture):
    _typeDict = {"plus": "Int",
                 "ampersand": "String"
                 }

    def query(self):
        result = []
        result.append(self.makeMap(1, "one"))
        result.append(MockCollection(1, "two"))
        result.append(self.makeMap(2, "two"))
        return result

    def makeMap(self, plus, ampersand):
        return {"plus": plus,
               "ampersand": ampersand,
               }
