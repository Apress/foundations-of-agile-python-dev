# ArrayFixtureUnderTest3 from FitLibrary Specification Tests
# Developed by Rick Mugridge
# Copyright 2004 Rick Mugridge, University of Auckland, NZ
# Released under the terms of the GNU General Public License version 2 or later.
# Translation to Python copyright 2005 John H. Roth Jr.

from fitLib.ArrayFixture import ArrayFixture

class ArrayFixtureUnderTest3(ArrayFixture):
    _typeDict = {"plus": "Int",
                 "ampersand": "String",
                 }
    def __init__(self):
        super(ArrayFixtureUnderTest3, self).__init__([])
