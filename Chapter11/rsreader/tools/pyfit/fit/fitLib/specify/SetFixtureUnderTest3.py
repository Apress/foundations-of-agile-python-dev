# SetFixtureUnderTest2 from FitLibrary Specification Tests
# Developed by Rick Mugridge
# Copyright 2004 Rick Mugridge, University of Auckland, NZ
# Released under the terms of the GNU General Public License version 2 or later.
# Translation to Python copyright 2005 John H. Roth Jr.

from fitLib.SetFixture import SetFixture

class SetFixtureUnderTest3(SetFixture):
    _typeDict = {"plus": "Int",
                 "ampersand": "String",
                 }
    def __init__(self):
        super(SetFixtureUnderTest3, self).__init__([])
