# SymbolTest module with fixtures for the SymbolTest.htm test
# Copyright 2005 John H. Roth Jr.
# Released under the GNU General Public License, version 2.0 or later

from fit.ColumnFixture import ColumnFixture
from fit.RowFixture import RowFixture

# This contains three fixtures and an object.

# Fixture 1

class AnObject(object):
    _typeDict = {"output": "Int"}
    def __init__(self, aString):
        self.anInt = int(aString)

    def __eq__(self, other):
        return id(self) == id(other)

    def __str__(self):
        return str(self.anInt)

    def input(self):
        return self

    def output(self):
        return self.anInt

AnObject._typeDict["input"] = AnObject(1) # an instance

theCollection = []

class ColumnFixture1(ColumnFixture):
    _typeDict = {"input": "Int",
                 "output": AnObject(1)} # an instance

    def output(self):
        __pychecker__ = "no-classattr"
        obj = AnObject(self.input)
        theCollection.append(obj)
        self.setSymbol("theCollection", theCollection)
        return obj

class ColumnFixture2(ColumnFixture):
    _typeDict = {"input": AnObject(1),
                 "output": "Int"}

    def output(self):
        __pychecker__ = "no-classattr"
        return self.input.anInt

class RowFixture1(RowFixture):
    _typeDict = {"input": AnObject(1),
                 "output": "Int"}

    def query(self):
        return self.getSymbol("theCollection")

       
