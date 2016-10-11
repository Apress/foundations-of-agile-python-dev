# RowFixtureUnderTest from FitLibrary Acceptance Tests
# Developed by Rick Mugridge
# Copyright 2003 Rick Mugridge, University of Auckland, NZ
# Released under the terms of the GNU General Public License version 2 or later.
# Translation to Python copyright 2005 John H. Roth Jr.

from fit.RowFixture import RowFixture

class RowFixtureUnderTest(RowFixture):
   
    def query(self):
        return [
            MockClass(1, "one"),
            MockClass(1, "two"),
            MockClass(2, "two")
            ]

    def getTargetClass(self):
        return MockClass

class MockClass:
    _typeDict = {"a": "Int",
                 "s": "String",
                 "camelField": "Float",
                 }
    a = 0
    s = ""    
    camelField = 1.5

    def __init__(self, a, s):
        self.a = a
        self.s = s
