# ColumnFixtureUnderTest - test fixture from FitLibrary for ColumnFixture
# Copyright 2003 by and developed by Rick Mugridge, University of Auckland, NZ
# Released under the terms of the GNU General Public License version 2 or later.
# Python Translation Copyright 2005 John H. Roth Jr.


from fit.ColumnFixture import ColumnFixture
# import java.util.Calendar

class ColumnFixtureUnderTest(ColumnFixture):
    _typeDict = {
        "count": "Int",
        "a": "Int",
        "b": "Int",
        "camelFieldName": "String",
        "calendar": "fubar"
        }
    count = 1
    a = 0
    b = 0
    camelFieldName = ""
    calendar = None

    _typeDict["plus"] = "Int"    
    def plus(self):
        return self.a + self.b

    _typeDict["minus"] = "Int"    
    def minus(self):
        return self.a - self.b
    
    _typeDict["getCamelFieldName"] = "String"    
    def getCamelFieldName(self):
        return self.camelFieldName

    _typeDict["exceptionMethod"] = "Int"    
    def exceptionMethod(self):
        raise Exception, "this is just a test..."
        
    _typeDict["voidMethod"] = ""    
    def voidMethod(self):
        return None

    _typeDict["increment"] = "Int"    
    def increment(self):
        oldCount = self.count
        self.count = self.count + 1
        return oldCount
    
    _typeDict["useCalendar"] = "fubar"    
    def useCalendar(self):
        return self.calendar

