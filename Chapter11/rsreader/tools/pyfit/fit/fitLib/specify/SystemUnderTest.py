# SystemUnderTest from Acceptance Tests for FitLibrary
# Developed by Rick Mugridge
# copyright 2004 Rick Mugridge, University of Auckland, NZ
# Released under the terms of the GNU General Public License version 2 or later.
# Translation to Python copyright 2005, John H. Roth Jr.

# NOTE - only the parts needed for the current tests are translated.
# some of it may remain untranslated forever...

try:
    False
except:
    False = 0
    True = 1

from fit.Fixture import Fixture
from fitLib.ArrayFixture import ArrayFixture
from fitLib.FitLibraryExceptions import FitFailureException
from fitLib.SequenceFixture import SequenceFixture
from fitLib.SetFixture import SetFixture
from fitLib.SubsetFixture import SubsetFixture

#
# Internal classes hoisted to module level
#

# class used with otherObject to test ability to invoke static methods.
# this is a static class; Python doesn't have such. I'm not sure why we
# care, actually.

class A(object):
    _typeDict = {}
    _typeDict["accessOther.types"] = ["Boolean"]
    def accessOther():
        return True
    accessOther = staticmethod(accessOther)

    _typeDict["otherInt.types"] = ["Int"]
    def otherInt():
        return 4
    otherInt = staticmethod(otherInt)

class Point(object):
    _typeDict = {"x": "Int",
                 "y": "Int"
                 }
    x = 0
    y = 0
    def __init__(self, x, y):
        self.x = x
        self.y = y

class SystemUnderTest(object):
    _typeDict = {}
    sum_ = 0
    concat_ = ""
    value_ = 0

    _typeDict["add.types"] = [None, "Int"]
    def add(self, i):
        self.sum_ += i

    _typeDict["sum.types"] = ["Int"]
    def sum(self):
        return self.sum_

    _typeDict["plus.types"] = ["Int"]
    def plus(self):
        return self.sum()

    _typeDict["addAndAppend.types"] = [None, "Int", "String"]
    def addAndAppend(self, i, s):
        self.add(i)
        self.concat_ += s;

    _typeDict["addAmpersandAppend.types"] = [None, "Int", "String"]
    def addAmpersandAppend(self, i, s):
        self.addAndAppend(i, s)

    _typeDict["appends.types"] = ["String"]
    def appends(self):
        return self.concat_

    _typeDict["plusPlus.types"] = ["String"]
    def plusPlus(self):
        return self.appends()

    _typeDict["aRightAction.types"] = ["Boolean", "Int"]
    def aRightAction(self, i):
        return True

    _typeDict["aWrongAction.types"] = ["Boolean", "Float", "Float"]
    def aWrongAction(self, x, y):
        return False

    _typeDict["anExceptionAction.types"] = ["Int"]
    def anExceptionAction(self):
        raise FitFailureException, "testing" # Was Runtime Exception

    _typeDict["value.types"] = [None, "Int"]
    def value(self, i):
        self.value_ = i

# !!! following shadows the first add method!
##    _typeDict["add.types"] = [None]    
##    def add(self):
##        self.add(self.value_)

# XXX This is kind of a cheat to get the OtherTypes DoFixture test to pass
#     Python doesn't have a Date type that can do quite what is asked.
##    public Date sameDate(Date date) {
##        return date;
    _typeDict["sameDate.types"] = ["String", "String"]
    def sameDate(self, date):
        return date

    def hiddenMethod(self):
        raise FitFailureException, "testing"

    _typeDict["anotherObject.types"] = ["$SUT"] # returns a fixture
    def anotherObject(self):
        return SequenceFixture(A())

    _typeDict["booleanProperty"] = "Boolean"
    def getBooleanProperty(self):
        return True
    booleanProperty = property(getBooleanProperty)

    _typeDict["intProperty"] = "Int"
    def getIntProperty(self):
        return 2
    intProperty = property(getIntProperty)

##    public boolean booleanProperty() {
##        return true;
##    }
##    public boolean isBooleanProperty() {
##        return true;
##    }
##    public int getIntProperty() {
##        return 2;
##    }


# There are five routines here because Java has
# five collection classes. Python only has three,
# and only one (a list) is supported for automatic
# collections. I'm maintaining five routines so that
# the specification tests work as written.

    _typeDict["anArrayOfPoint.types"] = ["$Array"]
    def anArrayOfPoint(self):
        return ([Point(0, 0), Point(5, 5)], Point._typeDict)

    _typeDict["aListOfPoint.types"] = ["$Set"]
    def aListOfPoint(self):
        return ([Point(0, 0), Point(5, 5)], Point._typeDict)

    # This should be an iterator; I'm not going to do that here
    # since it's tested elsewhere.
    _typeDict["anIteratorOfPoint.types"] = ["$Set"]
    def anIteratorOfPoint(self):
        return ([Point(0, 0), Point(5, 5)], Point._typeDict)

    _typeDict["aSetOfPoint.types"] = ["$Set"]
    def aSetOfPoint(self):
        return ([{"x": 0, "y": 0}, {"x": 5, "y": 5},], Point._typeDict)

    _typeDict["aSortedSetOfPoint.types"] = ["$Subset"]
    def aSortedSetOfPoint(self):
        return ([{"x": 0, "y": 0}, {"x": 5, "y": 5},], Point._typeDict)

    _typeDict["aMapOfPoint.types"] = ["$Set"]
    def aMapOfPoint(self):
        return ({(0,0): {"x": 0, "y": 0},
                (5,5): {"x": 5, "y": 5}
                }, Point._typeDict)

    _typeDict["plusAB.types"] = ["Int", "Int", "Int"]
    def plusAB(self, a, b):
        return a + b

    _typeDict["shown.types"] = ["String"]
    def shown(self):
        return "<ul><li>ita<li>lics</ul>";
