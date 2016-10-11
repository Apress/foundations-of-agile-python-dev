# CamelRowFixtureUnderTest from FitLibrary Specification Tests
# Developed by Rick Mugridge
# Copyright 2004 Rick Mugridge, University of Auckland, NZ
# Released under the terms of the GNU General Public License version 2 or later.
# Translation to Python copyright 2005 John H. Roth Jr.

from fit.RowFixture import RowFixture
from fitLib.specify.MockCollection import MockCollection

class CamelRowFixtureUnderTest(RowFixture):
    # Type Dictionary for MockCollection belongs here.
    _typeDict = {"plus": "Int",
                 "ampersand": "String",
                 "some": "Int",
                 }
    _typeDict["prop"] = "Int"
    
    
    def query(self):
         return [MockCollection(1, "one"),
                 MockCollection(1, "two"),
                 MockCollection(2, "two")
                 ]
    def getTargetClass(self):
        return MockCollection

