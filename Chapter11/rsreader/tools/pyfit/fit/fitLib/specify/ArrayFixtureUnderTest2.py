# ArrayFixtureUnderTest2 from FitLibrary Specification Tests
# Developed by Rick Mugridge
# Copyright 2004 Rick Mugridge, University of Auckland, NZ
# Released under the terms of the GNU General Public License version 2 or later.
# Translation to Python copyright 2005 John H. Roth Jr.

from fitLib.ArrayFixture import ArrayFixture
from fitLib.specify.MockCollection import MockCollection

class ArrayFixtureUnderTest2(ArrayFixture):
    def __init__(self):
        super(ArrayFixtureUnderTest2, self).__init__(
            [MockCollection(1, "one"),
             MockCollection(1, "two"),
             MockCollection(2, "two"),
             Some(),
             ]
            )
    _typeDict = {"plus": "Int",
                 "ampersand": "String",
                 "some": "String"
                 }
        
class Some:
    def some(self):
        return "one"
