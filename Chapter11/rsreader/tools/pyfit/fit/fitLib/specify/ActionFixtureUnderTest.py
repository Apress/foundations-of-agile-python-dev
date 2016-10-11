#ActionFixtureUnderTest from FitLibrary
#legalStuff rm03 jr05
# Original version Contains code developed by Rick Mugridge.
# University of Auckland, NZ. Copyright 2003 Rick Mugridge.
# Released under the terms of the General Public License (GPL), Release 2.1 or later
# See license.txt for terms and disclaimer of all warrenties and liability.
# changes Copyright 2005 John H. Roth Jr.
# Last updated for Release 0.8a1
#endLegalStuff jr05

# Note that a number of actions don't have metadata. This is because
# neither the start nor press actions require metadata. Also, there
# are a couple of invalid methods that there is no way to enter
# metadata for in the current structure.


# !!! WARNING ---- I had to change the switchback logic because of an
# import loop; using a callback to reset the actor is arguable better
# design anyway, but it's not what's in the Fit Book.

from fit.ActionFixture import ActionFixture
from fit.Fixture import Fixture
from fitLib.specify.AnotherActor import AnotherActor

try:
    False
except:
    False = 0
    True = 1

class ActionFixtureUnderTest(Fixture):
    _typeDict = {"result": "Integer"}
    result = 0

    _typeDict["pressMethod"] = "Boolean"
    def pressMethod(self): # methods using invoke need metadata as of 0.8
        pass

    _typeDict["enterString"] = "String"
    def enterString(self, s):
        pass

    _typeDict["enterResult"] = "Int"    
    def enterResult(self, result):
        self.result = result

    _typeDict["intResultMethod"] = "Int"
    def intResultMethod(self):
        return self.result

    _typeDict["booleanResultMethod"] = "Boolean"
    def booleanResultMethod(self):
        return False

    _typeDict["enterThrows"] = "String"
    def enterThrows(self, s):
        raise Exception, "this is a test"

    def pressThrows(self):
        raise Exception, "this is a test"

    _typeDict["checkThrows"] = "String"
    def checkThrows(self):
        raise Exception, "this is a test"

    _typeDict["pressMethodReturningInt"] = "Integer"
    def  pressMethodReturningInt(self):
        return 123

    def enterMethodWithNoArgs(self):
        pass

    def enterMethodWithTwoArgs(self, a, b):
        pass

    _typeDict["switchActor"] = "Boolean"
    def switchActor(self):
        ActionFixture.actor = AnotherActor(Callback(ActionFixture.actor))

class Callback(object):
    def __init__(self, oldActor):
        self.oldActor = oldActor

    def __call__(self):
        ActionFixture.actor = self.oldActor

