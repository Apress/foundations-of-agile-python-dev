# CalculateFixtureUnderTest3 from FitLibrary AcceptanceTests
# Developed by Rick Mugridge
# Copyright 2004 Rick Mugridge, University of Auckland, NZ
# Released under the terms of the GNU General Public License version 2 or later.
# Translation to Python copyright 2005 John H. Roth Jr.

from fitLib.CalculateFixture import CalculateFixture

class CalculateFixtureUnderTest3(CalculateFixture):
    def __init__(self, sut=None):
        CalculateFixture.__init__(self, sut)
        self.setRepeatString("")

    _typeDict = {}
    _typeDict["plusAB.types"] = ["Int", "Int", "Int"]
    def plusAB(self, a, b):
        return a + b
