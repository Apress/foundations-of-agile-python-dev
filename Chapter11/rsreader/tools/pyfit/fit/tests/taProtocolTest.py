# test module for type adapter protocols
# copyright 2005, John H. Roth Jr.
# Released under the terms of the GNU Public License, Version 2.
# See license.txt for conditions and exclusion of all warrenties.

import types
import unittest
from fit.Parse import Parse
from fit.ScientificFloat import ScientificFloat
from fit.taBase import TypeAdapter as taType
from fit import taProtocol as taPro
from fit.taProtocol import *
from fit.taTable import typeAdapterTable as tat

try:
    False
except: #pragma: no cover
    True = 1
    False = 0

def makeProtocolTest():
    theSuite = unittest.makeSuite(TestBasicProtocolForString, 'test')
    theSuite.addTest(unittest.makeSuite(TestBasicProtocolForInt, 'test'))
    theSuite.addTest(unittest.makeSuite(TestBasicProtocolCompatability, 'test'))
    theSuite.addTest(unittest.makeSuite(TestDefaultProtocol, 'test'))
    theSuite.addTest(unittest.makeSuite(TestEditedStringProtocolForFloat, 'test'))
    theSuite.addTest(unittest.makeSuite(TestEditedStringProtocolCompatability, 'test'))
    theSuite.addTest(unittest.makeSuite(TestRawStringProtocol, 'test'))
    theSuite.addTest(unittest.makeSuite(TestRawStringIntProtocol, 'test'))
    theSuite.addTest(unittest.makeSuite(TestCellAccessProtocol, 'test'))
    theSuite.addTest(unittest.makeSuite(TestApplicationProtocolForState, 'test'))
    theSuite.addTest(unittest.makeSuite(TestApplicationProtocolCompatability, 'test'))
    theSuite.addTest(unittest.makeSuite(TestInvalidProtocolThrowsException, 'test'))
    return theSuite

class TestBasicProtocolForString(unittest.TestCase):
    def setUp(self):
        self.ta = tat["String"](self, "aStringVar", "String")
        self.pro = taPro.getProtocolFor(self.ta)
        self.cell = Parse(tag="td", body="spam")
        print '%s %s' % (self.id(), self.shortDescription())

    def testProtocolForStringAdapter(self):
        assert isinstance(self.pro, taPro.BasicProtocol)
        assert isinstance(self.pro.ta, taType)
        assert self.pro.ta.fitAdapterProtocol == "Basic"

    def testBasicProtocolParse(self):
        assert self.pro.parse(self.cell) == "spam"

    def testBasicProtocolEquals(self):
        obj = self.pro.parse(self.cell)
        assert self.pro.equals(self.cell, obj)

    def testBasicProtocolToString(self):
        obj = self.pro.parse(self.cell)
        assert self.pro.toString(obj) == "spam"

class TestBasicProtocolForInt(unittest.TestCase):
    def setUp(self):
        self.ta = tat["Integer"](self, "anIntVar", "Integer")
        self.pro = taPro.getProtocolFor(self.ta)
        self.cell = Parse(tag="td", body="1")
        print '%s %s' % (self.id(), self.shortDescription())

    def testProtocolForIntAdapter(self):
        assert isinstance(self.pro, taPro.ProtocolBase)
        assert isinstance(self.pro.ta, taType)

    def testBasicProtocolParse(self):
        assert self.pro.parse(self.cell) == 1

    def testBasicProtocolEquals(self):
        obj = self.pro.parse(self.cell)
        assert self.pro.equals(self.cell, obj)

    def testBasicProtocolToString(self):
        obj = self.pro.parse(self.cell)
        assert self.pro.toString(obj) == "1"

class TestDefaultProtocol(unittest.TestCase):
    def setUp(self):
        self.ta = FakeDefaultTypeAdapter()
        self.pro = taPro.getProtocolFor(self.ta)
        self.cell = Parse(tag="td", body="1")
        print '%s %s' % (self.id(), self.shortDescription())

    def testProtocolForDefaultAdapter(self):
        assert isinstance(self.pro, taPro.BasicProtocol)
        assert isinstance(self.pro.ta, FakeDefaultTypeAdapter)

    def testDefaultProtocolParse(self):
        assert self.pro.parse(self.cell) == 1

    def testDefaultProtocolEquals(self):
        obj = self.pro.parse(self.cell)
        assert self.pro.equals(self.cell, obj)

    def testDefaultProtocolToString(self):
        obj = self.pro.parse(self.cell)
        assert self.pro.toString(obj) == "1"

class FakeDefaultTypeAdapter(object):
    def parse(self, aString):
        return int(aString)
    def equals(self, a, b):
        return a == b
    def toString(self, anInt):
        return str(anInt)
        
class TestEditedStringProtocolForFloat(unittest.TestCase):
    def setUp(self):
        self.ta = tat["Float"](self, "aFloatVar", "Float", metaData={})
        self.pro = taPro.getProtocolFor(self.ta)
        self.cell = Parse(tag="td", body="3.14")
        print '%s %s' % (self.id(), self.shortDescription())

    def testProtocolForFloatAdapter(self):
        assert isinstance(self.pro, taPro.EditedStringProtocol)
        assert isinstance(self.pro.ta, taType)
        assert self.pro.ta.fitAdapterProtocol == "EditedString"

    def testEditedStringProtocolParse(self):
        self.assertAlmostEqual(self.pro.parse(self.cell), 3.14, 1)

    def testEditedStringProtocolEquals(self):
        obj = self.pro.parse(self.cell)
        assert self.pro.equals(self.cell, obj)
        assert self.pro.equals(3.14, obj)

    def testEditedStringProtocolToString(self):
        obj = self.pro.parse(self.cell)
        assert self.pro.toString(obj) == "3.14"

class FakeRawStringTypeAdapter(object):
    fitAdapterProtocol = "RawString"
    def parse(self, aString):
        return aString
    def equals(self, a, b):
        return a == b
    def toString(self, aString):
        return aString

class TestRawStringProtocol(unittest.TestCase):
    def setUp(self):
        self.ta = FakeRawStringTypeAdapter()
        self.pro = taPro.getProtocolFor(self.ta)
        self.cell = Parse(tag="td", body="<tag you're=it>")
        print '%s %s' % (self.id(), self.shortDescription())

    def testProtocolForRawStringAdapter(self):
        assert isinstance(self.pro, taPro.RawStringProtocol)
        assert isinstance(self.pro.ta, FakeRawStringTypeAdapter)
        assert self.pro.ta.fitAdapterProtocol == "RawString"

    def testRawStringProtocolParse(self):
        assert self.pro.parse(self.cell) == "<tag you're=it>"
        assert self.pro.parse(self.cell.body) == "<tag you're=it>"

    def testRawStringProtocolEquals(self):
        obj = self.pro.parse(self.cell)
        assert self.pro.equals(self.cell, obj)
        assert self.pro.equals(self.cell.body, obj)

    def testRawStringProtocolToString(self):
        obj = self.pro.parse(self.cell)
        assert self.pro.toString(obj) == "<tag you're=it>"

class FakeRawStringIntTypeAdapter(FakeDefaultTypeAdapter):
    fitAdapterProtocol = "RawString"
    def equals(self, a, b):
        return int(a) == b

class TestRawStringIntProtocol(unittest.TestCase):
    def setUp(self):
        self.ta = FakeRawStringIntTypeAdapter()
        self.pro = taPro.getProtocolFor(self.ta)
        self.cell = Parse(tag="td", body="1")
        print '%s %s' % (self.id(), self.shortDescription())

    def testProtocolForRawStringAdapter(self):
        assert isinstance(self.pro, taPro.RawStringProtocol)
        assert isinstance(self.pro.ta, FakeRawStringIntTypeAdapter)
        assert self.pro.ta.fitAdapterProtocol == "RawString"

    def testRawStringIntProtocolParse(self):
        assert self.pro.parse(self.cell) == 1
        assert self.pro.parse(self.cell.body) == 1

    def testRawStringIntProtocolEquals(self):
        obj = self.pro.parse(self.cell)
        assert self.pro.equals(self.cell, obj)
        assert self.pro.equals(self.cell.body, obj)
        assert self.pro.equals(1, obj)

    def testRawStringIntProtocolToString(self):
        obj = self.pro.parse(self.cell)
        assert self.pro.toString(obj) == "1"

class DummyFloatCellTypeAdapter(object):        
    fitAdapterProtocol = "CellAccess"
    def parse(self, cell):
        return float(cell.body)
    def equals(self, cell, obj):
        a = float(cell.body)
        return abs(a - obj) < .1
    def toString(self, obj, cell):
        cell.parts = None
        cell.body = str(obj)
        return str(obj)

class TestCellAccessProtocol(unittest.TestCase):    
    def setUp(self):
        self.ta = DummyFloatCellTypeAdapter()
        self.pro = taPro.getProtocolFor(self.ta)
        self.cell = Parse(tag="td", body="1.0")
        print '%s %s' % (self.id(), self.shortDescription())

    def _checkFitException(self, callable, parms, expected):
        try:
            callable(*parms)
            self.fail("No Exception Raised")
        except FitException, e:
            result = e.getMeaningfulMessage()
            if result[2] != expected:
                self.fail("unexpected message in exception: '%s'" % result[2])
            return

    def testProtocolForCellAccessAdapter(self):
        assert isinstance(self.pro, taPro.CellAccessProtocol)
        assert isinstance(self.pro.ta, DummyFloatCellTypeAdapter)
        assert self.pro.ta.fitAdapterProtocol == "CellAccess"

    def testRawStringIntProtocolParse(self):
        assert self.pro.parse(self.cell) == 1.0
        self._checkFitException(self.pro.parse, ("1.0",),
                        "Cell Access Protocol Requires a parse cell")

    def testRawStringIntProtocolEquals(self):
        obj = self.pro.parse(self.cell)
        assert self.pro.equals(self.cell, obj)
        self._checkFitException(self.pro.equals, ("1.0", obj),
                        "Cell Access Protocol Requires a parse cell")

    def testRawStringIntProtocolToString(self):
        obj = self.pro.parse(self.cell)
        self.cell.body = ""
        assert self.pro.toString(obj, self.cell) == "1.0"
        assert self.cell.body == "1.0"
        self._checkFitException(self.pro.toString, (obj, None),
                        "Cell Access Protocol Requires a parse cell")

class TestApplicationProtocolForState(unittest.TestCase):
    def setUp(self):
        self.ta = PrimitiveState
        self.pro = taPro.getProtocolFor(self.ta)
        self.cell = Parse(tag="td", body="fi")
        print '%s %s' % (self.id(), self.shortDescription())

    def testProtocolForPrimitiveState(self):
        assert isinstance(self.pro, taPro.ApplicationProtocol)
        assert not isinstance(self.pro.ta, taType)

    def testApplicationProtocolParse(self):
        assert self.pro.parse(self.cell) == "fi"

    def testApplicationProtocolEquals(self):
        obj = self.pro.parse(self.cell)
        assert self.pro.equals(self.cell, obj)

    def testApplicationProtocolToString(self):
        obj = self.pro.parse(self.cell)
        assert self.pro.toString(obj) == "fi"

class TestBasicProtocolCompatability(unittest.TestCase):
    def setUp(self):
        self.ta = tat["String"](self, "aStringVar", "String")
        self.pro = taPro.getProtocolFor(self.ta)
        self.cell = Parse(tag="td", body="spam")
        print '%s %s' % (self.id(), self.shortDescription())

    def testProtocolForStringAdapter1(self):
        assert isinstance(self.pro, taPro.BasicProtocol)
        assert isinstance(self.pro.ta, taType)
        assert self.pro.ta.fitAdapterProtocol == "Basic"

    def testBasicProtocolParse(self):
        assert self.pro.parse(self.cell.text()) == "spam"

    def testBasicProtocolEquals(self):
        obj = self.pro.parse(self.cell.text())
        assert self.pro.equals(self.cell.text(), obj)

    def testBasicProtocolToString(self):
        obj = self.pro.parse(self.cell)
        assert self.pro.toString(obj) == "spam"

class TestEditedStringProtocolCompatability(unittest.TestCase):
    def setUp(self):
        self.ta = tat["Float"](self, "aFloatVar", "Float", metaData={})
        self.pro = taPro.getProtocolFor(self.ta)
        self.cell = Parse(tag="td", body="3.14")
        print '%s %s' % (self.id(), self.shortDescription())

    def testProtocolForFloatAdapter(self):
        assert isinstance(self.pro, taPro.EditedStringProtocol)
        assert isinstance(self.pro.ta, taType)
        assert self.pro.ta.fitAdapterProtocol == "EditedString"

    def testEditedStringProtocolParse(self):
        self.assertAlmostEqual(self.pro.parse(self.cell.text()), 3.14, 1)

    def testEditedStringProtocolEquals(self):
        obj = self.pro.parse(self.cell)
        assert self.pro.equals(self.cell.text(), obj)

    def testEditedStringProtocolToString(self):
        obj = self.pro.parse(self.cell)
        assert self.pro.toString(obj) == "3.14"        

class TestApplicationProtocolCompatability(unittest.TestCase):
    def setUp(self):
        self.ta = ScientificFloat
        self.pro = taPro.getProtocolFor(self.ta)
        self.cell = Parse(tag="td", body="2.798")
        print '%s %s' % (self.id(), self.shortDescription())

    def testProtocolForPrimitiveState(self):
        assert isinstance(self.pro, taPro.ApplicationProtocol)
        assert not isinstance(self.pro.ta, taType)

    def testApplicationProtocolParse(self):
        self.assertAlmostEqual(self.pro.parse(self.cell.text()), 2.798, 3)

    def testApplicationProtocolEquals(self):
        obj = self.pro.parse(self.cell.text())
        assert self.pro.equals(self.cell.text(), obj)
        assert self.pro.equals(ScientificFloat("2.798"), obj)

    def testApplicationProtocolToString(self):
        obj = self.pro.parse(self.cell)
        assert self.pro.toString(obj) == "2.798"

class TestInvalidProtocolThrowsException(unittest.TestCase):
    def setUp(self):
        self.ta = ScientificFloat
        self.cell = Parse(tag="td", body="2.798")
        print '%s %s' % (self.id(), self.shortDescription())
        
    def _checkFitException(self, callable, parms, expected):
        try:
            callable(*parms)
            self.fail("No Exception Raised")
        except FitException, e:
            result = e.getMeaningfulMessage()
            if result[2] != expected:
                self.fail("unexpected message in exception: '%s'" % result[2])
            return

    def testInvalidProtocolThrowsException(self):
        ta = TypeAdapterWithInvalidProtocolName
        self._checkFitException(taPro.getProtocolFor, (ta,),
                    "Type Adapter requests invalid ptotocol: 'fubar'")

class TypeAdapterWithInvalidProtocolName(FakeRawStringTypeAdapter):        
    fitAdapterProtocol = "fubar"

class PrimitiveState(object):
    def __init__(self, stateName):
        if self._stateDict.get(stateName) is not None:
            self._stateName = stateName
        else:
            raise Exception, "invalid state"

    def __eq__(self, other):
        if isinstance(other, types.StringTypes):
            return self._stateName == other
        return self._stateName == other._stateName

    def __ne__(self, other):
        if isinstance(other, types.StringTypes):
            return self._stateName != other
        return self._stateName != other._stateName

    def __str__(self):
        return self._stateName

    _stateDict = {"fie": True,
                  "fi": True,
                  "fo": True,
                  "fum": "not yet",
                  }
        
if __name__ == '__main__':
    unittest.main(defaultTest='makeProtocolTest')
