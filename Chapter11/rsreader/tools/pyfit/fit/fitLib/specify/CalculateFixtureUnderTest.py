# CalculateFixtureUnderTest from FitLibrary Acceptance Tests
# Developed by Rick Mugridge
# Copyright 2004 Rick Mugridge, University of Auckland, NZ
# Released under the terms of the GNU General Public License version 2 or later.
# Translation to Python copyright 2005 John H. Roth Jr.

import sys
from fitLib.CalculateFixture import CalculateFixture
from fitLib.ListTree import ListTree, TreeTypeAdapter

def em(msg):
    return
    if msg[-1] != "\n":
        msg += "\n"
    sys.stderr.write(msg)

class CalculateFixtureUnderTest(CalculateFixture):
    _typeDict = {"count": "Int"}
    count = 1
    
    _typeDict["plusAB.types"] = ["Int", "Int", "Int"]
    def plusAB(self, a, b):
        return a + b

    _typeDict["sum.types"] = ["Int", "Int", "Int"]
    def sum(self, a, b):
        return a + b

    _typeDict["minusAB.types"] = ["Int", "Int", "Int"]
    def minusAB(self, a, b):
        return a - b

    _typeDict["plusA.types"] = ["Int","Int"]
    def plusA(self, a):
        return a

    _typeDict["getCamelFieldName.types"] = ["String", "String"]
    def getCamelFieldName(self, name):
        return name

    _typeDict["plusName.types"] = ["String", "String"]
    def plusName(self, name):
        return name + "+"

    _typeDict["exceptionMethod.types"] = ["String"]
    def exceptionMethod(self):
        raise Exception

    _typeDict["voidMethod.types"] = [None]
    def voidMethod(self):
        return

    _typeDict["increment.types"] = ["Int"]
    def increment(self):
        result = self.count
        self.count += 1
        return result

    # Deliberate invocation of a missing type adapter - tests expect an exception
    _typeDict["useCalendar.types"] = ["String", "Calendar"] 
    def useCalendar(self, calendar):
        return calendar

    _typeDict["plus12.types"] = [TreeTypeAdapter, TreeTypeAdapter,
                                 TreeTypeAdapter]
    def plus12(self, t1, t2):
#        em("in plus12. t1: '%s' t2: '%s'" % (t1, t2))
        result = ListTree("", [t1, t2])
        return result
