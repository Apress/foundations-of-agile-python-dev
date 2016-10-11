# DoFixtureFlowUnderTest from FitLibrary Specification Tests
#legalStuff rm03 jr05-06
# Original version Contains code developed by Rick Mugridge.
# University of Auckland, NZ. Copyright 2003 Rick Mugridge.
# Released under the terms of the General Public License (GPL), Release 2.1 or later
# See license.txt for terms and disclaimer of all warrenties and liability.
# changes Copyright 2005-2006 John H. Roth Jr.
# Last updated for Release 0.8a1
#endLegalStuff

from fit.ColumnFixture import ColumnFixture
from fit.Fixture import Fixture
from fit.Parse import Parse
from fit.FitException import FitException
from fit.RowFixture import RowFixture
from fitLib.DoFixture import DoFixture
from fitLib.specify.SystemUnderTest import SystemUnderTest
from fit.Utilities import em

#
# Note - this module has a lot of internal classes which
#  appear at the beginning. The actual
#  DoFixtureFlowUnderTest class is near the middle
#

class TypeAdapterBase:
    pass

class ClassWithNoTypeAdapter:
    def toString(self):
        return "77"

#
# This almost satisfies the Type Adapter protocol.
#
class MyClass(object):
    i = 1
    def __init__(self, i):
        self.i = i

    def parse(s):
        return MyClass(int(s))
    parse = staticmethod(parse)
    
    def toString(self):
        return str(self.i)

    def equals(self, object):
        return self.i == object.i

#
#
# !!! Since this is a subtype of ColumnFixture, it needs the older
#     style of metadata.
class MyColumnFixture(ColumnFixture):
    _typeDict = {"x": "Int"}
    x = 0
    def __init__(self, initial):
        ColumnFixture.__init__(self)
        self.x = initial

    _typeDict["getX.types"] = ["Int"]
    _typeDict["getX"] = "Int"
    def getX(self):
        return self.x

#
#
#

class Local:
    _typeDict = {"s": "String"}
    s = ""

    def __init__(self, s):
        self.s = s

class LocalRowFixture(RowFixture):
    rows = [[[Local("A0a"), Local("A0b")],
             [Local("A1a"), Local("A1b")],
             [Local("A2a"), Local("A2b")],
             [Local("A3a"), Local("A3b")],
             ],[
             [Local("B0a"), Local("B0b")],
             [Local("B1a"), Local("B1b")],
             [Local("B2a"), Local("B2b")],
             [Local("B3a"), Local("B3b")],
             ]]
            
    row = 0
    column = 0

    def __init__(self, row, column):
        self.row = row
        self.column = column
        super(LocalRowFixture, self).__init__()

    def query(self):
        return self.rows[self.row][self.column]

    def getTargetClass(self):
        return Local

# added this because it's not a Python library class.
class Point(object):
    _typeDict = {}
    _x = 0
    _y = 0
    def __init__(self, x, y):
        self._x = x
        self._y = y

    _typeDict["x.types"] = ["Int"]
    _typeDict["x"] = "Int"
    _typeDict["getX.RenameTo"] = "x"
    def x(self):
        return self._x

    _typeDict["y"] = "Int"
    _typeDict["y.types"] = ["Int"]
    def y(self):
        return self._y

class PointTypeAdapter(object):
    def parse(self, dummy='aString'):
        return Point(1, 1) # XXX not sure what the string should look like!

    def stringEquals(self, aString, aPoint):
        aPoint = self.parse(aString)
        return aPoint == aPoint

    def toString(self, aPoint):
        return "%s, %s" % (aPoint.x(), aPoint.y())
        
class PointHolder(object):
    _typeDict = {"point.types": ["$SUT"]} 
    def point(self):
        return Point(24, 7)

# Stub for Java integer class.
class Integer(object):
    _typeDict = {}
    i = 0
    def __init__(self, i):
        self.i = i
    _typeDict["parseInt.types"] = ["Int", "String"]
    def parseInt(s):
        return int(s)
    parseInt = staticmethod(parseInt)

    _typeDict["doubleValue.types"] = ["Float"]
    def doubleValue(self):
        return float(self.i)
        

# -----------------------
# This is the real class!
# -----------------------

class DoFixtureFlowUnderTest(DoFixture):
#   DATE_FORMAT = SimpleDateFormat("yyyy/MM/dd HH:mm");
    DATE_FORMAT = "yyyy/MM/dd HH:mm"

    def __init__(self):
        DoFixture.__init__(self, SystemUnderTest())

    _typeDict = {}
    def specialAction(self, cells):
        cells = cells.more
        if cells.text() == "right":
            self.right(cells)
        elif cells.text() == "wrong":
            self.wrong(cells)
    specialAction.fitLibSpecialAction = True # !!! mark it.

    _typeDict["hiddenMethod.types"] = [None]
    def hiddenMethod(self):
        pass

    _typeDict["fixtureObject.types"] = [None, "Int"]
    def fixtureObject(self, initial):
        return MyColumnFixture(initial)

    _typeDict["aPoint.types"] = [PointTypeAdapter] # need a point type adapter
    def aPoint(self):
        return Point(2,3) # need a point object

    _typeDict["getDate.types"] = ["Date"]
    def getDate(self):
#        return new Date(2004-1900,2,3);
        return 2004-1900, 2, 3

    _typeDict["getException.types"] = [None]
    def getException(self):
        raise FitException, "ForcedException"

    _typeDict["anInteger.types"] = ["$SUT"]
    def anInteger(self):
        return Integer(23)

    _typeDict["myClass.types"] = ["Class"] # XXX needs fixing somehow    
    def myClass(self):
        return MyClass(3) # XXX likewise

    _typeDict["useToString.types"] = ["Class"] # Class with no type adapter
    def useToString(self):
        return ClassWithNoTypeAdapter()

    _typeDict["getSlice.types"] = ["Int", "Int", "Int"]
    def getSlice(self, row, column):
        return LocalRowFixture(row, column)

    # was getPointHolder - Java version of a property.
    # Python does't use get nomenclature. May put in a property
    #  feature for FitLibrary later.
    _typeDict["pointHolder.types"] = ["$SUT"]
    def pointHolder(self):
        return PointHolder()
    


