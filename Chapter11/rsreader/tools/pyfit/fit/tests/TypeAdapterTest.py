# test module for Type Adapter
#LegalStuff jr04-05
# Copyright 2004-2005 John H. Roth Jr.
# Released under the terms of the General Public License (GPL), Release 2.1 or later
# See license.txt for terms and disclaimer of all warrenties and liability.
# Last updated for Release 0.8a1
#endLegalStuff
# Created on the occasion of a massive restructuring... JHR
# Note that FrameworkTest also runs a great many tests against TypeAdapter

from unittest import makeSuite, main
from types import *

from fit.Counts import Counts
from fit.InitEnvironment import FG, setupFitGlobalForTests
from fit.FitException import FitException
from fit.Parse import Parse
import fit.TypeAdapter as TypeAdapter
TA = TypeAdapter
from fit.taBase import TypeAdapter as taType
import fit.taProtocol as taPro
from fit.taTable import typeAdapterTable as tat
from tests.TestCommon import FitTestCommon
from fit.Utilities import em

try:
    False
except: #pragma: no cover
    True = 1
    False = 0

OK = "ok"
NEXT = "next"
ERROR = "error"

def makeTypeAdapterTest():
    theSuite = makeSuite(SpecifyTypeAdapter, 'Test')
    theSuite.addTests(
        [makeSuite(SpecifyAccessor, "Test"),
         makeSuite(SpecifyCellHandlerManagement, "should"),
         makeSuite(SpecifyExceptionCellHandlerParameterParsing, "should"),
         makeSuite(SpecifyCheckResult, "test"),
         makeSuite(SpecifyDefaultTypeAdapter, 'should'),
         makeSuite(specifyMapTypeAdapterExit, "should"),
         makeSuite(specifyAcquireAdapterForType, "should"),
         ])
    return theSuite

class AValueClass(object):
    def __init__(self, a):
        self.a = a
    def __eq__(self, other):
        return self.a == other
    def __ne__(self, other):
        return self.a != other
    def __str__(self):
        return str(self.a)

class AdapterMock1(object):
    _typeDict = {}
    
    aStrVar = ""
    _typeDict["aStrVar"] = "String"

    aSubstrVar = ""
    _typeDict["aSubstrVar"] = "String"
    _typeDict["aSubstrVar.addCellHandlers"] = ["SubstringCellHandler"]

    anIntVar = 1
    _typeDict["anIntVar"] = "Int"

    aFloatVar = 1.0
    _typeDict["aFloatVar"] = "Float"
    _typeDict["aFloatVar.precision"] = 2

    bFloatVar = 1.0
    _typeDict["bFloatVar"] = "Float"
    _typeDict["bFloatVar.precision"] = 2

    cFloatVar = 1.0
    _typeDict["cFloatVar"] = "Float"
    _typeDict["cFloatVar.charBounds"] = "9"

    complexVar = 1.0 + 1.0j
    _typeDict["complexVar"] = "Complex"

    dateVar = []
    _typeDict["dateVar"] = "Date"

    _typeDict["noInt"] = "Int"

    aListVar = [1.0, 2.0, 3.0]
    _typeDict["aListVar"] = "List"
    _typeDict["aListVar.scalarType"] = "Float"

    aTupleVar = (1.0, 2.0, 3.0)
    _typeDict["aTupleVar"] = "Tuple"
    _typeDict["aTupleVar.scalarType"] = "Float"

    aDictVar = {"one": 1, "two": 2, "three": 3}
    _typeDict["aDictVar"] = "Dict"

    aTupleVar2 = (1, 2, 3)
    _typeDict["aTupleVar"] = "Tuple"

    anotherVar = ""
    _typeDict['anotherVar'] = "UnknownType"

    def getInt(self):
        return self.anIntVar
    _typeDict["getInt"] = "Int"

    def setInt(self, value):
        self.anIntVar = value
        return None
    _typeDict["setInt"] = "Int"

    def badIntMethod(self, value, valueless):
        pass
    _typeDict["badIntMethod"] = "Int"

    intProperty = property(getInt, setInt)
    _typeDict["intProperty"] = "Int"

    aUserVar = "something"
    _typeDict["aUserVar"] = tat["Boolean"]

    boolVar = True
    _typeDict["boolVar"] = "Boolean"

    bBoolVar = True
    _typeDict["bBoolVar"] = "Boolean"
    _typeDict["bBoolVar.true"] = "ham"
    _typeDict["bBoolVar.false"] = "spam"

    noDictVar = ""

    def noDictGetter(self):
        return self.noDictVar

    _typeDict["genVar"] = "Generic"
    _typeDict["genVar.ValueClass"] = AValueClass
    genVar = None    

class CaeserTypeAdapter(object):
    fitAdapterProtocol = "Basic"
    def parse(self, aString):
        return aString.encode("rot_13")

    def equals(self, a, b):
        return a == b.encode("rot_13")

    def toString(self, aString):
        return aString.encode("rot_13")

    def isCellHandlerApplicable(self, handlerName):
        if handlerName == "NullCellHandler":
            return False
        if handlerName == "SubstringCellHandler":
            return True
        return None

class ReverseCellHandler(object):
    canParse = True
    canCheck = True
    canCheckAfter = False

    # test involves not having an "isTypeAdapterApplicable" method

    def parse(self, cell, callback):
        __pychecker__ = "no-argsused" # callback
        return ("next", None)

    def check(self, cell, obj, callback):
        __pychecker__ = "no-argsused" # callback
        return ("next", None)

class RejectTypeAdapterCellHandler(object):
    canParse = True
    canCheck = True
    canCheckAfter = False

    def isTypeAdapterApplicable(self, taName):
        __pychecker__ = "no-argsused" # taName
        return False

    def parse(self, cell, callback):
        __pychecker__ = "no-argsused" # callback
        return ("next", None)

    def check(self, cell, obj, callback):
        __pychecker__ = "no-argsused" # callback
        return ("next", None)

class CreateErrorCellHandler(object):
    canParse = True
    canCheck = True
    canCheckAfter = False

    def isTypeAdapterApplicable(self, taName):
        __pychecker__ = "no-argsused" # taName
        return True

    def parse(self, cell, callback):
        __pychecker__ = "no-argsused" # callback
        return ("error", "Expected Error")

    def check(self, cell, obj, callback):
        __pychecker__ = "no-argsused" # callback, cell, obj
        return ("error", "Expected Error")

class UcOKParseExit:
    def __call__(self, value):
        __pychecker__ = "no-argsused" # value
        return "OK", value.upper()

class C3ParseExit:
    def __call__(self, value):
        __pychecker__ = "no-argsused" # value
        return "continue", "3"

class CNoneParseExit:
    def __call__(self, value):
        __pychecker__ = "no-argsused" # value
        return "continue", None

class ErrorParseExit:
    def __call__(self, value):
        return "error", '"%s" is invalid as used!' % value

class TestUtilities(FitTestCommon):
    def _buildDefaultTypeAdapter(self, taName, identifier, metaData=None):
        if metaData is None:
            metaData = {identifier: taName}
        elif metaData is False:
            metaData = None
        instance = AdapterMock1()
        accessor = TypeAdapter.on(instance, identifier, metaData)
        return instance, accessor

    def buildAccessorString1(self, taName, identifier, accClass):
        instance = AdapterMock1()
#        accObj = accClass(instance, identifier, None, instance.__class__)
        accessor = TypeAdapter.on(instance, identifier,
                                  {identifier: taName},
                                  accClass = accClass)
        return instance, accessor.adapter, accessor.protocol, accessor

class SpecifyTypeAdapter(TestUtilities):
    def setUp(self):
        print '%s %s' % (self.id(), self.shortDescription())
        setupFitGlobalForTests("Batch")

    def tearDown(self):
        TypeAdapter.restoreDefaultCellHandlerList()
        setupFitGlobalForTests("Batch")

    def taCommon(self, varName, typeName, typeDict = None):
        instance = AdapterMock1()
        obj = tat[typeName](instance, varName, typeName,
                                   typeDict or instance._typeDict)
        assert obj.typeName == typeName, "check type name"
        assert isinstance(obj, tat[typeName]), "check instance"
        return obj

    def TestInvalidExpression(self):
        obj = self.taCommon("aListVar", "List")
        self._checkFitException(obj.parse, ("[1 + 2]",),
                    "Add and Subtract only allowed for complex")
        self._checkFitException(obj.parse, ("[1 * 2]",),
                    "Class 'compiler.ast.Mul' not allowed")
        self._checkFitException(obj.parse, ("[fubar]",),
                                "Name 'fubar' not allowed")

    def TestGenericTypeAdapter(self):
        instance, adapter = self._buildDefaultTypeAdapter("Generic",
                                    "genVar", metaData=False)
        parsed = adapter.parse("kitten")
        adapter.set(parsed)
        assert instance.genVar == "kitten"
        assert adapter.toString(adapter.get()) == "kitten"
        assert adapter.equals(adapter.get(), "kitten")

    def Test_StringTypeAdapter(self):
        obj = self.taCommon("aStringVar", "String")
        assert obj.parse(" xxxxxx ") == "xxxxxx", "trim test"
        assert obj.equals("zzzzzz", "zzzzzz"), "equals test"
        assert obj.stringEquals("zzzzzz", "zzzzzz"), "string equals test"
        assert obj.toString("yyyyyy") == "yyyyyy", "toString test"
        assert obj.equals("zzzzzz", "aaaaaa") is False, "equals test - False"
        assert obj.stringEquals("zzzzzz", "bbbbbb") is False, "string equals test - False"
        assert obj.toString("yyyyyy") != "cccccc", "toString test - False"
        assert obj.typeName == "String", "check type name"

    def Test_StringTypeAdapter2(self):
        obj = self.taCommon("aStringVar", "String")
        assert obj.parse(' "asdf" ') == 'asdf', "quoted string test"
        assert obj.parse(' "qwerty\\\'uiop"') == "qwerty'uiop"
        assert obj.parse(' "qwerty\\\"uiop"') == 'qwerty"uiop'

    def Test_IntTypeAdapter(self):
        obj = self.taCommon("anIntVar", "Int")
        assert obj.parse(10) == 10, "parse test"
        assert obj.equals(20 , 20), "equals test"
        assert obj.stringEquals("10", 10), "string equals test 1"
        # definition of stringEquals changed 0.7a1
        self.failIf(obj.stringEquals(15, "15"), "string equals test 2")
        assert obj.toString(35) == "35", "toString test"
        assert obj.equals(20, 42) is False, "equals test - False"
        assert obj.stringEquals("999", 987) is False, "string equals test - False"
        assert obj.toString(19) != "very good year", "toString test - False"
        assert obj.typeName == "Int", "check type name"

    # Long is depreciated - Int now does whatever long used to do.
    def Test_LongTypeAdapter(self):
        obj = self.taCommon("aLongVar", "Long")
        assert obj.parse(10) == 10, "parse test"
        assert obj.equals(20 , 20), "equals test"
        assert obj.stringEquals("10", 10), "string equals test 1"
        # definition of stringEquals changed 0.7a1
        self.failIf(obj.stringEquals(15, "15"), "string equals test 2")
        assert obj.toString(35) == "35", "toString test"
        assert obj.equals(20, 42) is False, "equals test - False"
        assert obj.stringEquals("999", 987) is False, "string equals test - False"
        assert obj.toString(19) != "very good year", "toString test - False"
        assert obj.typeName == "Long", "check type name"

    def Test_FloatTypeAdapter(self):
        obj = self.taCommon("aFloatVar", "Float")
        assert obj.parse(10) == 10.0, "parse test"
        assert obj.equals(20.0 , 20.0), "equals test"
        assert obj.stringEquals("10", 10.0), "string equals test 1"
        assert obj.stringEquals(15.0, "15.0"), "string equals test 2"
        assert obj.toString(35.0) == "35.0", "toString test"
        assert obj.equals(20.0, 42.0) is False, "equals test - False"
        assert obj.stringEquals("999.0", 987.0) is False, "string equals test - False"
        assert obj.toString(19.0) != "very good year", "toString test - False"
        assert obj.typeName == "Float", "check type name"

    def _floatingPrecisionEquals(self, a, b, prec, expected):
        instance = AdapterMock1()
        instance._typeDict["bFloatVar.precision"] = int(prec)
        obj = tat["Float"](instance, "bFloatVar", "Float",
                                       metaData = instance._typeDict)
        assert obj.equals(a, b) == expected, ("a: %s b: %s result: %s" %
                                              (a, b, expected))

    def Test_FloatingPrecisionEquals(self):
        for a, b, prec, result in [(10.0, 10.0, 2, True),
                                   (10.0, 10.1, 2, False),
                                   (10.0, 9.9, 2, False),
                                   (10.0, 9.8, 2, False),
                                   (10.0, 10.2, 2, False),
                                   (100.0, 100.0, 2, True),
                                   (100.0, 101.0, 2, False),
                                   (100.0, 99.0, 2, False),
                                   (100.0, 98.0, 2, False),
                                   (100.0, 102.0, 2, False),                                   ]:
            self._floatingPrecisionEquals(a, b, prec, result)


    def _floatingPrecisionStringEquals(self, a, b, expected, varName):
        obj = self.taCommon(varName, "Float")
        assert obj.stringEquals(a, b) == expected, (
            "a: '%s', b: '%s' expected: '%s'" % (a, b, expected))

    def Test_FloatingPrecisionStringEquals(self):
        for a, b, expected in [("10.0", 10.0, True),
                                   ("10.0", 10.04, True),
                                   ("10.0", 10.06, False),
                                   ("10.0", 9.96, True),
                                   ("10.0", 9.94, False),
                                   ("10", 10.0, True),
                                   ("10", 10.4, True),
                                   ("10", 10.6, False),
                                   ("10", 9.6, True),
                                   ("10", 9.4, False),
                                   ("10.0e6", 10.00e6, True),
                                   ("10.0e6", 10.04e6, True),
                                   ("10.0e6", 10.06e6, False),
                                   ("10.0e6", 9.96e6, True),
                                   ("10.0e6", 9.94e6, False),
                                   ("-10.0", -10.0, True),
                                   ("-10.0", -10.04, True),
                                   ("-10.0", -10.06, False),
                                   ("-10.0", -9.96, True),
                                   ("-10.0", -9.94, False),
                                   ("-10", -10.0, True),
                                   ("-10", -10.4, True),
                                   ("-10", -10.6, False),
                                   ("-10", -9.6, True),
                                   ("-10", -9.4, False),
                                   ("-10.0e6", -10.00e6, True),
                                   ("-10.0e6", -10.04e6, True),
                                   ("-10.0e6", -10.06e6, False),
                                   ("-10.0e6", -9.96e6, True),
                                   ("-10.0e6", -9.94e6, False),
                                   ]:
            self._floatingPrecisionStringEquals(a, b, expected, "bFloatVar")

    def Test_FloatingPrecisionStringEquals9(self):
        for a, b, expected in [("10.0", 10.0, True),
                                   ("10.0", 10.08, True),
                                   ("10.0", 10.1, False),
                                   ("10.0", 9.92, True),
                                   ("10.0", 9.9, False),
                                   ("10", 10.0, True),
                                   ("10", 10.8, True),
                                   ("10", 11.0, False),
                                   ("10", 9.2, True),
                                   ("10", 9.0, False),
                                   ("10.0e6", 10.00e6, True),
                                   ("10.0e6", 10.08e6, True),
                                   ("10.0e6", 10.1e6, False),
                                   ("10.0e6", 9.92e6, True),
                                   ("10.0e6", 9.9e6, False),
                                   ]:
            self._floatingPrecisionStringEquals(a, b, expected, "cFloatVar")

    def Test_FloatSpecialValues(self):
        obj = self.taCommon("bFloatVar", "Float")
        NaN = obj.parse("NaN")
        assert obj.toString(NaN) == "NaN"
        assert not obj.equals("NaN", 3.14)
        assert obj.equals("+Inf > _", 3.14)
        pInf = obj.parse("+Inf")
        assert obj.toString(pInf) == "Inf"
        assert obj.toString(obj.parse("-Inf")) == "-Inf"
        assert obj.toString(obj.parse("Ind")) == "Ind"

    def Test_FloatingEpsilon(self):
        for a,b, expected in [("10.0 +/- .1", 10.01, True),
                              ("10.0 +/- .1", 10.15, False),
                              ("-10.0 +/- -.1", -10.05, True),
                              (u"10.0 \u00b1 .1", 10.15, False),
                              ]:
            self._floatingPrecisionStringEquals(a, b, expected, "bFloatVar")

    def Test_FloatingRange(self):
        for a, b, expected in [("9.9 < x < 10.1", 10.0, True),
                               ("9.7 < x < 9.9", 10.0, False),
                               ("10.1 < x < 10.3", 10.0, False),
                               ("9.9 <= x <= 10.1", 10.0, True),
                               ("9.7 <= x <= 9.9", 10.0, False),
                               ("10.1 <= x <= 10.3", 10.0, False),
                               (u"10.1 \u2264 x  \u2264 10.3", 10.2, True),
                               (u"10.1 < x \u2264 10.3", 10.2, True),
                               (u"10.1 <= x \u2264 10.3", 10.2, True),
                               (u"10.1 \u2264 x  < 10.3", 10.2, True),
                               (u"10.1 \u2264 x  <= 10.3", 10.2, True),
                               ("10.3 > x > 10.1", 10.2, True),
                               (u"10.3 \u2265 x \u2265 10.1", 10.2, True),
                               (u"10.3 > x \u2265 10.1", 10.2, True),
                               (u"10.3 >= x \u2265 10.1", 10.2, True),
                               (u"10.3 \u2265 x > 10.1", 10.2, True),
                               (u"10.3 \u2265 x >= 10.1", 10.2, True),
                               ]:
            self._floatingPrecisionStringEquals(a, b, expected, "bFloatVar")

    def Test_FloatingUnclosedRange(self):
        for a, b, expected in [("9.9 < x", 10.0, True),
                               ("x < 9.9", 10.0, False),
                               ("10.1 < x", 10.0, False),
                               ("9.9 <= x", 10.0, True),
                               ("<= 9.9", 10.0, False),
                               ]:
            self._floatingPrecisionStringEquals(a, b, expected, "bFloatVar")

    def TestFloatingCheckProhibitited(self):
        obj = self.taCommon("aFloatVar", "Float", {"aFloatVar": "Float",
                                        "aFloatVar.checkType": "fff"})
        self._checkFitException(obj.equals, ("3.14", 3.14), "noFloatCheck1")
        self._checkFitException(obj.equals, (3.14, 3.14), "noFloatCheck1")
        self._checkFitException(obj.equals, ("3.14 +/- .01", 3.14),
                                "noFloatCheckEpsilon")
        self._checkFitException(obj.equals, ("3.13 < _", 3.14),
                                "noFloatCheckRange")
        self._checkFitException(obj.equals, ("_ < 3.15", 3.14),
                                "noFloatCheckRange")
        self._checkFitException(obj.equals, ("_ < _", 3.13), "invRangeExp")
        self._checkFitException(obj.equals, ("3.12 < 3.14", 3.13),
                                "invRangeExp")
        self._checkFitException(obj.equals, ("3.13 < _ < 3.15", 3.14),
                                "noFloatCheckRange")
        self._checkFitException(obj.equals, ("3.13 < < < 3.15", 3.14),
                                "floatImproperSyntax")

    def TestFloatingObjectCompare(self):
        obj = self.taCommon("aFloatVar", "Float", {"aFloatVar": "Float",
                                        "aFloatVar.checkType": "cff"})
        assert obj.equals("3.14", 3.14)

    def Test_complex(self):
        obj = self.taCommon("complexVar", "Complex")
        complexVar = 1.0 + 1.0j
        assert obj.toString(complexVar) == "(1+1j)"
        assert obj.parse("1.0+1.0j") == 1 + 1j
        assert obj.parse("1.0 + 1.0j") == 1 + 1j
        assert obj.equals(complexVar, complexVar)
        newVar = complexVar + 0.1
        assert obj.equals(complexVar, newVar)
        newVar = complexVar + 1.0
        assert obj.equals(complexVar, newVar) is False

    def Test_BooleanTypeAdapter(self):
        obj = self.taCommon("boolVar", "Boolean")
        for a, expected in [("True", True), ("t", True), ("1", True), ("y", True),
                            ("yes", True), ("+", True),
                            ("false", False), ("f", False), ("no", False),
                            ("n", False), ("-", False), ("0", False),
                            ]:
            assert obj.parse(a) == expected, "parse(%s) expected: '%s' result: '%s'" % (
                a, expected, obj.parse(a))
        self._checkFitException(obj.parse, ("fubar",), "Invalid Boolean Value: 'fubar'")
        self._checkFitException(obj.parse, (42,), "Invalid Boolean Value: '42'")
        assert obj.parse(1)
        assert obj.equals("true", "yes"), "equals test: true == yes"
        assert obj.stringEquals("false", "n"), "string equals test 1"
        assert obj.toString(True) == "True", "toString test"

    def Test_BooleanAddTrueFalse(self):
        obj = self.taCommon("bBoolVar", "Boolean")
        assert obj.typeName == "Boolean", "check type name"
        assert isinstance(obj, tat["Boolean"]), "check instance"
        assert obj.equals("Ham", "True"), "equals test: Ham == True"
        assert obj.stringEquals("Spam", "False"), "string equals test Spam == False"

    def Test_DateTypeAdapter(self):
        obj = self.taCommon("dateVar", "Date")
        assert obj.parse("January 1, 2004")[:3] == (2004, 1, 1), "date 1"
        assert obj.parse("2000 February 29")[:3] == (2000, 2, 29), "date 2"
        assert obj.equals("2000 Feb 28", (2000, 2, 28))
        # TODO when 2.2 support dropped: equals with new date/time classes
        assert obj.toString(obj.parse("4 July 1776")) == "1776 July 4"
        self._checkFitException(obj.parse, ("Fi Fi fo fum",), "Smart Date Format error")
        self._checkFitException(obj.parse, ("m1xed up cas3",), "Smart Date Format error")
        self._checkFitException(obj.parse, ("July 99 1026",), "Smart Date Format error")
        self._checkFitException(obj.parse, ("1 1 1",), "Smart Date Format error")

    def Test_ListTypeAdapter(self):
        obj = self.taCommon("aListVar", "List")
        assert obj.parse("1.0, 2.0") == [1.0, 2.0], "check parse"
        assert obj.parse("[1.0, 'Hi There', 42]") == [1.0, "Hi There", 42], "new format"
#        saveScalarAdapter = obj.scalarAdapter
        obj.scalarAdapter = None
        assert obj.parse("1.0, 'Hi There', 42") == [1.0, "Hi There", 42], "new format"
        assert obj.parse("[1.0 + 1.0j]") == [1.0 + 1.0j]
        assert obj.parse("[1.0 - 1.0j]") == [1.0 - 1.0j]
        assert obj.parse("[True]") == [True]
        assert obj.equals("1.0, 'Hi There', 42", [1.0, "Hi There", 42])
        assert obj.toString([1, "Hi There", 42]) == "[1, 'Hi There', 42]"

    def Test_TupleTypeAdapter(self):
        obj = self.taCommon("aTupleVar", "Tuple")
        assert obj.parse("1.0, 2.0") == (1.0, 2.0), "check parse"
        assert obj.parse("(1.0, 'Hi There', 42)") == (1.0, "Hi There", 42), "new format"
        assert obj.parse("1.0") == (1.0,), "one element"
        assert obj.parse("('fubar',)") == ('fubar',), "one element, new format"
#        saveScalarAdapter = obj.scalarAdapter
        obj.scalarAdapter = None
        assert obj.parse("1.0, 'Hi There', 42") == (1.0, "Hi There", 42), "new format"
        assert obj.parse("1.0") == (1.0,), "one element"
        assert obj.parse("('fubar',)") == ('fubar',), "one element, new format"
        assert obj.equals("1.0, 'Hi There', 42", (1.0, "Hi There", 42))
        assert obj.toString((1, "Hi There", 42)) == "(1, 'Hi There', 42)", (
            "actual: '%s'" % obj.toString((1, "Hi There", 42)))

    def TestDictTypeAdapter(self):
        obj = self.taCommon("aDictVar", "Dict")
        assert obj.parse("{'a': 1, 'b': 2}") == {'a': 1, 'b': 2}, "check parse"
        assert obj.parse("'a': 1, 'b': 2") == {'a': 1, 'b': 2}, "new format"
        assert obj.equals("{'a': 1, 'b': 2}", {'a': 1, 'b': 2})

    def TestTypeAdapterFactoryFunction(self):
        instance = AdapterMock1()
        adapter = TypeAdapter._getTypeAdapter(instance, "anIntVar",
                                              instance._typeDict)
        assert isinstance(adapter, tat["Integer"])
        adapter = TypeAdapter._getTypeAdapter(instance, "")
        assert isinstance(adapter, tat["String"])
        adapter = TypeAdapter._getTypeAdapter(instance, "aListVar")
        assert isinstance(adapter, tat["List"])
        assert isinstance(adapter.scalarAdapter, tat["Float"])
        adapter = TypeAdapter._getTypeAdapter(instance, "aUserVar")
        assert isinstance(adapter, tat["Boolean"])
        
    def Test_MissingMetadata(self):
        instance = AdapterMock1()
        self._checkFitException(TypeAdapter._getTypeAdapter,
                    (instance, "SomethingMything", instance._typeDict),
                     "Metadata for 'SomethingMything' not found in class 'AdapterMock1'")

    def Test_UnknownType(self):
        instance = AdapterMock1()
        self._checkFitException(TypeAdapter._getTypeAdapter,
                    (instance, "anotherVar", instance._typeDict),
                     "Cannot identify type 'UnknownType'")

# ----------- Accessor Tests ----------------------------

class SpecifyAccessor(TestUtilities):
    def setUp(self):
        print '%s %s' % (self.id(), self.shortDescription())
        setupFitGlobalForTests("Batch")
        
    def tearDown(self):
        TypeAdapter.restoreDefaultCellHandlerList()
        setupFitGlobalForTests("Batch")        

    def checkAccessorGet(self, accessor, expected):
        result = accessor.get()
        assert result == expected, (
         "accessor.get. result: '%s' expected: '%s'" % (result, expected))

    def TestAccessorBaseClassAccess(self):        
#        instance = AdapterMock1()
        accessor = TypeAdapter.on(None, "Name", {"Name": "String"})
        assert accessor.get() is None
        accessor.set("fubar")
        assert accessor.get() == "fubar"
        assert accessor.invoke() == "fubar"

    def Test_FieldAccessor(self):
        instance, adapter, protocol, Accessor = self.buildAccessorString1(
            "String", "aStrVar", TypeAdapter.FieldAccessor)
        assert isinstance(Accessor, TypeAdapter.AccessorBaseClass), "check instance"
        self.checkAccessorGet(Accessor, "")
        Accessor.set("froob")
        assert instance.aStrVar == "froob", "check set method"
        self._checkFitException(Accessor.invoke, (), "You can't invoke a field!")

    def Test_FieldAccessorWithIntAdapter(self):
        instance, adapter, protocol, Accessor = self.buildAccessorString1(
            "Integer", "anIntVar", TypeAdapter.FieldAccessor)
        assert isinstance(Accessor, TypeAdapter.AccessorBaseClass), "check instance"
        self.checkAccessorGet(Accessor, 1)
        Accessor.set("42")
        assert instance.anIntVar == "42", "check set method"
        self._checkFitException(Accessor.invoke, (), "You can't invoke a field!")
        assert Accessor.parse("33") == 33, "check parse proxy method"
        assert Accessor.equals(10, 10) is True, "check equals for True"
        assert Accessor.equals(20, 42) is False, "check equals for False"
        assert Accessor.stringEquals("10", 10) is True, "check stringEquals - True"
        assert Accessor.toString(10) == "10", "check toString"

    def Test_getMethodAccessorWithIntAdapter(self):
        instance, adapter, protocol, Accessor = self.buildAccessorString1(
            "Integer", "getInt", TypeAdapter.GetMethodAccessor)
        assert isinstance(Accessor, TypeAdapter.AccessorBaseClass), "check instance"
        self.checkAccessorGet(Accessor, 1)
        self._checkFitException(Accessor.set, (42,),
                               "Cannot call set on a getter!")
        assert Accessor.invoke() == 1, "check invoke method"
        assert Accessor.parse("33") == 33, "check parse proxy method"
        assert Accessor.equals(10, 10) is True, "check equals for True"
        assert Accessor.equals(20, 42) is False, "check equals for False"
        assert Accessor.stringEquals("10", 10) is True, "check stringEquals - True"
        assert Accessor.toString(10) == "10", "check toString"

    def Test_setMethodAccessorWithIntAdapter(self):
        instance, adapter, protocol, Accessor = self.buildAccessorString1(
            "Integer", "setInt", TypeAdapter.SetMethodAccessor)
        assert isinstance(Accessor, TypeAdapter.AccessorBaseClass), "check instance"
        self._checkFitException(Accessor.get, (), "Cannot call get on a setter!")
        Accessor.set(42)
        assert instance.anIntVar == 42, "check set method"
        self._checkFitException(Accessor.invoke, (), "Cannot invoke a setter!")
        assert Accessor.parse("33") == 33, "check parse proxy method"
        assert Accessor.equals(10, 10) is True, "check equals for True"
        assert Accessor.equals(20, 42) is False, "check equals for False"
        assert Accessor.stringEquals("10", 10) is True, "check stringEquals - True"
        assert Accessor.toString(10) == "10", "check toString"

    def Test_FieldAccessorForPropertyWithIntAdapter(self):
        instance, adapter, protocol, Accessor = self.buildAccessorString1(
            "Integer", "intProperty", TypeAdapter.FieldAccessor)
        assert isinstance(Accessor, TypeAdapter.AccessorBaseClass), "check instance"
        assert Accessor.get() == 1, "check get method"
        Accessor.set("42")
        print instance.anIntVar
        assert instance.anIntVar == "42", "check set method"
        self._checkFitException(Accessor.invoke, (), "You can't invoke a field!")
        assert Accessor.parse("33") == 33, "check parse proxy method"
        assert Accessor.equals(10, 10) is True, "check equals for True"
        assert Accessor.equals(20, 42) is False, "check equals for False"
        assert Accessor.stringEquals("10", 10) is True, "check stringEquals - True"
        assert Accessor.toString(10) == "10", "check toString"

    def getAccessorHelper(self, identifier, accessor):
        __pychecker__ = "no-local" # protocol
        instance = AdapterMock1()
        adapter = TypeAdapter._getTypeAdapter(instance, identifier)
        protocol = taPro.getProtocolFor(adapter)
        Accessor = TypeAdapter._getAccessor(instance, identifier,
                                          None, instance.__class__)
        assert isinstance(Accessor, accessor), ("wrong accesssor class:"
            " expected: '%s' actual: '%s'" % (Accessor.__class__.__name__,
                                              accessor.__class__.__name__))
        
    def Test__getAccessor(self):
        self.getAccessorHelper("anIntVar", TypeAdapter.FieldAccessor)
        self.getAccessorHelper("noInt", TypeAdapter.FieldAccessor)
        self.getAccessorHelper("getInt", TypeAdapter.GetMethodAccessor)
        self.getAccessorHelper("setInt", TypeAdapter.SetMethodAccessor)
        # ??? can we replace this clutter?
        instance = AdapterMock1()
#        adapter = TypeAdapter._getTypeAdapter(instance, "badIntMethod")
#        protocol = taPro.getProtocolFor(adapter)
        self._checkFitException(TypeAdapter._getAccessor,
                (instance, "badIntMethod", None, instance.__class__),
                "Method 'badIntMethod' in class 'AdapterMock1' has wrong number of parameters")
        self.getAccessorHelper("intProperty", TypeAdapter.FieldAccessor)

    def TestTypeAdapterOnFactoryFunction(self):
        instance = AdapterMock1()
        Accessor = TypeAdapter.on(instance, "anIntVar")
        assert isinstance(Accessor, TypeAdapter.FieldAccessor)
        assert isinstance(Accessor.adapter, tat["Integer"])
        self._checkFitException(TypeAdapter.on, (None, "anIntVar", None),
                               "Metadata is required if no instance is supplied")
        self._checkFitException(TypeAdapter.on, (None, None, None),
                               "Metadata is required if no instance is supplied")
        Accessor = TypeAdapter.on(instance, "anIntVar",
                                         {"anIntVar": "Boolean"})
        assert isinstance(Accessor, TypeAdapter.FieldAccessor)
        assert isinstance(Accessor.adapter, tat["Boolean"])
        self._checkFitException(TypeAdapter.on,
                                (instance, "anIntVar", {"anIntVar":"fubar"}),
                               "Cannot identify type 'fubar'")
        adapter = TypeAdapter._getTypeAdapter(instance, "boolVar")
        Accessor = TypeAdapter.on(instance, "intProperty",
                                         {"intProperty" : adapter}) 
        assert isinstance(Accessor, TypeAdapter.FieldAccessor)
        assert isinstance(Accessor.adapter, tat["Boolean"])
        Accessor = TypeAdapter.on(instance, "intProperty",
                                         {"intProperty": tat["Boolean"]})
        assert isinstance(Accessor, TypeAdapter.FieldAccessor)
        assert isinstance(Accessor.adapter, tat["Boolean"])
        self._checkFitException(TypeAdapter.on,
                                (instance, "anIntVar", {"anIntVar":1.0}),
                               "Cannot identify type 'float'")
        Accessor = TypeAdapter.on(None, "snafu", {"snafu": "String"})
        assert isinstance(Accessor, TypeAdapter.AccessorBaseClass)
        assert isinstance(Accessor.adapter, tat["String"])
        self._checkFitException(TypeAdapter.on,
                                (instance, "fubar", {"snafu": 1.0}),
                               "Metadata for 'fubar' not found in class 'AdapterMock1'")

    def Test_getBlankName(self):
        instance = AdapterMock1()
        Accessor = TypeAdapter.on(instance, "")
        assert isinstance(Accessor, TypeAdapter.AccessorBaseClass)
        assert isinstance(Accessor.adapter, tat["String"])

    def Test_getQuestionName(self):
        instance = AdapterMock1()
        Accessor = TypeAdapter.on(instance, "?")
        assert isinstance(Accessor, TypeAdapter.AccessorBaseClass)
        assert isinstance(Accessor.adapter, tat["String"])

    def TestUserAdapterClass(self):
        instance = AdapterMock1()
        Accessor = TypeAdapter.on(instance, "aStringVar",
                                  {"aStringVar": CaeserTypeAdapter})
        assert isinstance(Accessor, TypeAdapter.FieldAccessor)
        assert isinstance(Accessor.adapter, CaeserTypeAdapter)
        assert Accessor.hasCellHandler("NullCellHandler") is False

    def TestUserAdapterInstance(self):
        instance = AdapterMock1()
        adapterInstance = CaeserTypeAdapter()
        Accessor = TypeAdapter.on(instance, "aStringVar",
                                  {"aStringVar": adapterInstance})
        assert isinstance(Accessor, TypeAdapter.FieldAccessor)
        assert Accessor.adapter is adapterInstance

    # XXX depreciated function
    def TestAddUserTypeAdapter(self):
        numAdapters = len(tat)
        TypeAdapter.addTypeAdapterToDictionary("Caeser", CaeserTypeAdapter)
        assert len(tat) == numAdapters + 1

    # XXX depreciated function
    def TestCantReplaceBuiltinTypeAdapter(self):
        numAdapters = len(tat)
        TypeAdapter.addTypeAdapterToDictionary("Integer", CaeserTypeAdapter)
        assert len(tat) == numAdapters

    # XXX adapterOnType is to be rewritten, these tests are obsolete
    def Test_adapterOnType(self):
        __pychecker__ = "no-local" # instance
        instance = AdapterMock1()
        Accessor = TypeAdapter.adapterOnType(None, "Boolean")
        assert isinstance(Accessor, TypeAdapter.AccessorBaseClass)
        assert isinstance(Accessor.adapter, tat["Boolean"])

    def Test_adapterOnType_Float(self):
        __pychecker__ = "no-local" # instance
        instance = AdapterMock1()
        Accessor = TypeAdapter.adapterOnType(None, "fubar", metaData = {
            "fubar": "Float",
            "fubar.precision": 4})
        assert isinstance(Accessor, TypeAdapter.AccessorBaseClass)
        assert isinstance(Accessor.adapter, tat["Float"])
        
    def Test_adapterOnType_ListFloat(self):
        __pychecker__ = "no-local" # instance
        instance = AdapterMock1()
        Accessor = TypeAdapter.adapterOnType(None, "fubar", metaData = {
            "fubar": "List",
            "fubar.scalarType": "Float",
            "fubar.precision": 8})
        assert isinstance(Accessor, TypeAdapter.AccessorBaseClass)
        assert isinstance(Accessor.adapter, tat["List"])
        scalarAdapter = Accessor.adapter.scalarAdapter
        assert isinstance(scalarAdapter, tat["Float"])
        assert scalarAdapter.precision == 8

    def Test_adapterForStringTypeName(self):
        __pychecker__ = "no-local" # instance
        instance = AdapterMock1()
        Accessor = TypeAdapter.adapterForStringTypeName("Boolean")
        assert isinstance(Accessor, TypeAdapter.AccessorBaseClass)
        assert isinstance(Accessor.adapter, tat["Boolean"])
        # ??? why no test against instance?
# end tests for depreciated factory functions

    # ------------- Parse Exit Tests ------------------

    # XXX parse exit functionality is depreciated.
    def Test_defaultParseExit(self):
        obj = TypeAdapter.DefaultParseExit()
        assert obj("some stuff") == ("continue", None)

    def Test_setParseExit(self):
        instance, adapter, protocol, accessor = self.buildAccessorString1(
            "String", "aStrVar", TypeAdapter.FieldAccessor)
        assert accessor.parse("qwerty") == "qwerty"
        accessor.setParseExit(UcOKParseExit())
        assert accessor.parse("qwerty") == "QWERTY"

    def Test_setIntParseExit(self):        
        instance, adapter, protocol, accessor = self.buildAccessorString1(
            "Int", "anIntVar", TypeAdapter.FieldAccessor)
        accessor.setParseExit(UcOKParseExit())
        assert accessor.parse("qwerty") == "QWERTY"
        accessor.setParseExit(C3ParseExit()) # "continue", "3"
        assert accessor.parse("qwerty") == 3
        accessor.setParseExit(CNoneParseExit())
        assert accessor.parse("42") == 42
        accessor.setParseExit(ErrorParseExit())
        self._checkFitException(accessor.parse, ("Hi There!",),
                                '"Hi There!" is invalid as used!')

    def Test_clearIntParseExit(self):            
        instance, adapter, protocol, Accessor = self.buildAccessorString1(
            "Integer", "anIntVar", TypeAdapter.FieldAccessor)
        Accessor.setParseExit(UcOKParseExit())
        assert Accessor.parse("qwerty") == "QWERTY"
        Accessor.clearParseExit()
        assert Accessor.parse("99") == 99

    def TestThatParseAndSetReturnsParseOK(self):
        inst, acc = self._buildDefaultTypeAdapter("Int", "anIntVar")
        cell = Parse(tag="td", body="1")
        result = acc.parseAndSet(cell)
        assert isinstance(result, TA.CheckResult_ParseOK)
        assert result.value == 1

    def TestThatParseAndSetReturnsException(self):
        inst, acc = self._buildDefaultTypeAdapter("Int", "anIntVar")
        cell = Parse(tag="td", body="foo")
        result = acc.parseAndSet(cell)
        assert isinstance(result, TA.CheckResult_Exception)
        assert result.value is None

    def TestThatParseAndSetReturnsRightIfErrorKwdAndError(self):
        inst, acc = self._buildDefaultTypeAdapter("Int", "anIntVar")
        cell = Parse(tag="td", body="exception[ValueError,,'foo']")
        result = acc.parseAndSet(cell)
        assert isinstance(result, TA.CheckResult_Right)
        assert result.value is None

    def TestThatParseAndSetRaisesExceptionForInvalidExceptionCellHandler(self):
        inst, acc = self._buildDefaultTypeAdapter("Int", "anIntVar")
        cell = Parse(tag="td", body="exception[ValueError]")
        self._checkFitException(acc.parseAndSet, (cell,), "parseExceptionCHNoValue")

    def TestThatParseAndSetReturnsExceptionWrongIfErrorKwdAndWrongError(self):
        inst, acc = self._buildDefaultTypeAdapter("Int", "anIntVar")
        cell = Parse(tag="td", body="exception[FooError,,'foo']")
        result = acc.parseAndSet(cell)
        assert isinstance(result, TA.CheckResult_ExceptionWrong)
        assert result.value is None

    def TestThatParseAndSetReturnsExceptionWrongIfErrorKwdAndWrongMsg(self):
        inst, acc = self._buildDefaultTypeAdapter("Int", "anIntVar")
        cell = Parse(tag="td", body="exception[,'Wrong message','foo']")
        result = acc.parseAndSet(cell)
        assert isinstance(result, TA.CheckResult_ExceptionWrong)
        assert result.value is None

    def TestThatParseAndSetReturnsWrongIfErrorKwdAndNoError(self):
        inst, acc = self._buildDefaultTypeAdapter("Int", "anIntVar")
        cell = Parse(tag="td", body="exception[FooError,,'1']")
        result = acc.parseAndSet(cell)
        assert isinstance(result, TA.CheckResult_Wrong)
        assert result.value == 1

    def TestThatCheckOfBlankCellReturnsInfoWithValue(self):        
        inst, acc = self._buildDefaultTypeAdapter("Int", "anIntVar")
        inst.anIntVar = 1
        cell = Parse(tag="td", body="")
        result = acc.check(cell)
        assert isinstance(result, TA.CheckResult_Info)
        assert result.value == 1
        assert result.actual == "1"

    def TestThatCheckReturnsRightIfCorrectException(self):
        inst, acc = self._buildDefaultTypeAdapter("Int", "anIntVar")
        inst.anIntVar = 1
        cell = Parse(tag="td", body="exception[ValueError,,'Foo']")
        result = acc.check(cell)
        assert isinstance(result, TA.CheckResult_Right)
        assert result.value == 1

    def TestThatCheckReturnsWrongIfNoException(self):
        inst, acc = self._buildDefaultTypeAdapter("Int", "anIntVar")
        inst.anIntVar = 1
        cell = Parse(tag="td", body="exception[ValueError,,'1']")
        result = acc.check(cell)
        assert isinstance(result, TA.CheckResult_Wrong)
        assert result.value == 1

class SpecifyCellHandlerManagement(TestUtilities):
    def setUp(self):
        print '%s %s' % (self.id(), self.shortDescription())
        setupFitGlobalForTests("Batch")
        TypeAdapter.restoreDefaultCellHandlerList()

    def tearDown(self):
        setupFitGlobalForTests("Batch")
        TypeAdapter.restoreDefaultCellHandlerList()

    def shouldCellHandlerParse(self):
        instance, adapter, protocol, Accessor = self.buildAccessorString1(
            "String", "aStrVar", TypeAdapter.FieldAccessor)
        assert Accessor.runCellHandlerParseList("blank") == (OK, "")
        assert Accessor.runCellHandlerParseList("something else") == (NEXT, None)
        assert Accessor.runCellHandlerParseList("null") == (OK, None)
        
    def shouldCellHandlerParse2(self):
        instance, adapter, protocol, Accessor = self.buildAccessorString1(
            "String", "aStrVar", TypeAdapter.FieldAccessor)
        assert Accessor.parse("blank") == ""
        assert Accessor.parse("something else") == "something else"
        assert Accessor.parse("null") is None

    def shouldCellHandlerCheck(self):
        instance, adapter, protocol, Accessor = self.buildAccessorString1(
            "String", "aStrVar", TypeAdapter.FieldAccessor)
        assert Accessor.runCellHandlerCheckList("blank", "") == (OK, True)
        assert Accessor.runCellHandlerCheckList("blank", "check") == (OK, False)
        assert Accessor.runCellHandlerCheckList("something else", "foo") == (
            NEXT, None)
        assert Accessor.runCellHandlerCheckList("null", None) == (OK, True)
        assert Accessor.runCellHandlerCheckList("null", 99) == (OK, False)

    def shouldCellHandlerCheck2(self):
        __pychecker__ = "no-local" # result
        instance, adapter, protocol, Accessor = self.buildAccessorString1(
            "String", "aStrVar", TypeAdapter.FieldAccessor)
        assert Accessor.stringEquals("blank", "") is True
        assert Accessor.stringEquals("blank", "check") is False
        assert Accessor.stringEquals("something else", "foo") is False
        assert Accessor.stringEquals("null", None) is True
        assert Accessor.stringEquals("null", 99) is False
        result = Accessor.stringEquals("fail[blank]", "")
        assert Accessor.stringEquals("fail[blank]", "") is False
##        assert Accessor.stringEquals("fail[fail[blank]]", "") is True
        # ??? above commented out. Why?

    def shouldIntegerNumericRange(self):
        instance, adapter, protocol, Accessor = self.buildAccessorString1(
            "Int", "anIntVar", TypeAdapter.FieldAccessor)
        assert Accessor.stringEquals("40..60", 50) is True
        assert Accessor.stringEquals(" 40 .. 60", 70) is False

    def shouldFloatNumericRange(self):
        instance, adapter, protocol, Accessor = self.buildAccessorString1(
            "Float", "aFloatVar", TypeAdapter.FieldAccessor)
        assert Accessor.stringEquals("41.06 ..66.24", 50.0) is True
        assert Accessor.stringEquals("41.06 ..66.24", 50) is True
        assert Accessor.stringEquals(" 41.06 .. 66.24", 70) is False

    def shouldAddSubstringCellHandler(self):
        instance, adapter, protocol, Accessor = self.buildAccessorString1(
            "String", "aSubstrVar", TypeAdapter.FieldAccessor)
        TypeAdapter._addCellHandlersToAccessor(Accessor, ["Substring"])
        result = Accessor.stringEquals("startswith[spam]", "spamandeggs")
        assert result

    def shouldAddCellHandlerMetadata(self):
        instance = AdapterMock1()
        Accessor = TypeAdapter.on(instance, "anIntVar", {"anIntVar": "Int",
                    "anIntVar.addCellHandlers": ["Substring"]})
        assert isinstance(Accessor, TypeAdapter.FieldAccessor)
        assert isinstance(Accessor.adapter, tat["Integer"])

    def shouldRejectAddOfDuplicateCellHandler(self):
        instance = AdapterMock1()
        Accessor = TypeAdapter.on(instance, "anIntVar", {"anIntVar": "Int"})
        numHandlers = len(Accessor.cellHandlerList)
        Accessor = TypeAdapter.on(instance, "anIntVar", {"anIntVar": "Int",
                    "anIntVar.addCellHandlers": ["Substring",
                                                 "Substring"]})
        assert len(Accessor.cellHandlerList) == numHandlers + 1

    def shouldAddCellHandlerClass(self):
        instance = AdapterMock1()
        Accessor = TypeAdapter.on(instance, "anIntVar", {"anIntVar": "Int"})
        numHandlers = len(Accessor.cellHandlerList)
        Accessor = TypeAdapter.on(instance, "anIntVar", {"anIntVar": "Int",
                    "anIntVar.addCellHandlers": [ReverseCellHandler]})
        assert len(Accessor.cellHandlerList) == numHandlers + 1

    def shouldRemoveCellHandlerMetadata(self):
        instance = AdapterMock1()
        Accessor = TypeAdapter.on(instance, "anIntVar", {"anIntVar": "Int",
                "anIntVar.removeCellHandlers": ["NumericRange"]})
        assert isinstance(Accessor, TypeAdapter.FieldAccessor)
        assert isinstance(Accessor.adapter, tat["Integer"])

    def shouldRemoveRangeCellHandler(self):
        instance, adapter, protocol, Accessor = self.buildAccessorString1(
            "Float", "aFloatVar", TypeAdapter.FieldAccessor)
        assert Accessor.stringEquals("41.06 ..66.24", 50.0) is True
        TypeAdapter._removeCellHandlersFromAccessor(Accessor,
                                        ["NumericRange"])
        self.assertRaises(ValueError, Accessor.stringEquals,
                          "41.06 ..66.24", 50.0)

    def shouldCellHandlerErrorOnParse(self):
        instance = AdapterMock1()
        Accessor = TypeAdapter.on(instance, "anIntVar", {"anIntVar": "Int",
                "anIntVar.addCellHandlers": [CreateErrorCellHandler]})
        cell = Parse(tag="td", body="1")
        self.assertRaises(FitException, Accessor.parse, cell)

    def shouldCellHandlerErrorOnCheck(self):
        instance = AdapterMock1()
        Accessor = TypeAdapter.on(instance, "anIntVar", {"anIntVar": "Int",
                "anIntVar.addCellHandlers": [CreateErrorCellHandler]})
        cell = Parse(tag="td", body="1")
        self.assertRaises(FitException, Accessor.equals, cell, 1)

    def shouldEqualsWithRawString(self):
        instance = AdapterMock1()
        Accessor = TypeAdapter.on(instance, "aFloatVar")
        assert Accessor.equals("1.0", 1.0)

    def shouldCellHandlerWithoutTypeAdapterCheck(self):
        ta = TypeAdapter
        ta.AccessorBaseClass.cellHandlerList.addHandler(ReverseCellHandler)
        instance = AdapterMock1()
        Accessor = ta.on(instance, "anIntVar")
        assert isinstance(Accessor, TypeAdapter.FieldAccessor)
        assert isinstance(Accessor.adapter, tat["Integer"])
        assert Accessor.hasCellHandler("ReverseCellHandler")

    def shouldCellHandlerRejectsTypeAdapter(self):
        ta = TypeAdapter
        ta.AccessorBaseClass.cellHandlerList.addHandler(
            RejectTypeAdapterCellHandler)
        instance = AdapterMock1()
        Accessor = ta.on(instance, "anIntVar")
        assert isinstance(Accessor, TypeAdapter.FieldAccessor)
        assert isinstance(Accessor.adapter, tat["Integer"])
        assert Accessor.hasCellHandler("RejectTypeAdapterCellHandler") is False

    def shouldAddOptionalHandlerToList(self):
        ta = TypeAdapter
        numHandlers = len(ta.AccessorBaseClass.cellHandlerList)
        assert numHandlers == len(ta.getCurrentCellHandlerList())
        assert ta.addOptionalHandlerToList("Substring")
        assert numHandlers + 1 == len(ta.AccessorBaseClass.cellHandlerList)

    def shouldntAddNonExistantHandlerToList(self):
        ta = TypeAdapter
        numHandlers = len(ta.AccessorBaseClass.cellHandlerList)
        assert numHandlers == len(ta.getCurrentCellHandlerList())
        assert ta.addOptionalHandlerToList("FubarCellMisHandler") is False
        assert numHandlers == len(ta.AccessorBaseClass.cellHandlerList)

    def shouldRemoveHandlerFromList(self):
        ta = TypeAdapter
        numHandlers = len(ta.AccessorBaseClass.cellHandlerList)
        assert numHandlers == len(ta.getCurrentCellHandlerList())
        assert ta.removeHandlerFromList("NumericRange")
        assert numHandlers - 1 == len(ta.AccessorBaseClass.cellHandlerList)

    def shouldDontRemoveNonExistantHandlerFromList(self):
        ta = TypeAdapter
        numHandlers = len(ta.AccessorBaseClass.cellHandlerList)
        assert numHandlers == len(ta.getCurrentCellHandlerList())
        assert ta.removeHandlerFromList("FubarCellMisHandler") is False
        assert numHandlers == len(ta.AccessorBaseClass.cellHandlerList)

    def shouldClearAndRestoreCellHandlerList(self):
        ta = TypeAdapter
        assert (len(ta.AccessorBaseClass.cellHandlerList) ==
                len(ta.getCurrentCellHandlerList()))
        ta.clearCellHandlerList()
        assert len(ta.AccessorBaseClass.cellHandlerList) == 0
        ta.restoreDefaultCellHandlerList()
        assert (len(ta.AccessorBaseClass.defaultCellHandlerList) ==
                len(ta.AccessorBaseClass.cellHandlerList))

    def shouldDeleteCellHandlerListIfExitReturnsFalse(self):        
        class DenyCellHandler(object):
            def manageCellHandlers(self, anObj):
                return False
        self._installApplicationExit(DenyCellHandler)
        instance = AdapterMock1()
        acc = TypeAdapter.on(instance, "aStrVar")
        assert len(acc.cellHandlerList) == 0

    def shouldRemoveInitialListIfRequested(self):        
        class RemoveCellHandler(object):
            def manageCellHandlers(self, anObj):
                return {".startWithDefaultList": "no"}
        self._installApplicationExit(RemoveCellHandler)
        instance = AdapterMock1()
        acc = TypeAdapter.on(instance, "aStrVar")
        assert len(acc.cellHandlerList) == 0

# For what seemed like good reasons at the time, some of the tests
# are in the cell handler test module. I suspect all of them should
# be there, but we would have problems with circular dependencies.
# if we moved the exception cell handler parsing class.

class SpecifyExceptionCellHandlerParameterParsing(TestUtilities):
    def setUp(self):
        print '%s %s' % (self.id(), self.shortDescription())
        setupFitGlobalForTests("Batch")
        TypeAdapter.restoreDefaultCellHandlerList()

    def tearDown(self):
        setupFitGlobalForTests("Batch")
        TypeAdapter.restoreDefaultCellHandlerList()

    def shouldRaiseExceptionIfUnknownSignature(self):
        self._checkFitException(TA.ExceptionCellHandlerParameters,
                    ("'Larry', 'Moe', 'Curly'",),
                    "exceptionCHinvalidSignature")

    def shouldRaiseExceptionIfUnrecognizableToken(self):
        self._checkFitException(TA.ExceptionCellHandlerParameters,
                    ("'Larry' # 'Moe', 'Curly'",),
                    "exceptionCHUnknownToken")

    def shouldRaiseExceptionIfUnparsableInput(self):
        self._checkFitException(TA.ExceptionCellHandlerParameters,
                    ("Foo?",), "exceptionCHParseError")

    # 0.9 capture and convert TokenError.

class SpecifyCheckResult(TestUtilities):
    def setUp(self):
        print '%s %s' % (self.id(), self.shortDescription())
        setupFitGlobalForTests("Batch")

    def tearDown(self):
        setupFitGlobalForTests("Batch")

    def testCheckResultBase(self):
        obj = TA.CheckResult()
        assert not obj.isRight()
        assert str(obj) == "CheckResult: No data to report"
        assert not obj

    def testCheckResultDoNothing(self):
        obj = TA.CheckResult_DoNothing()
        assert not obj.isRight()
        assert str(obj) == "CheckResult: Do Nothing object"
        assert not obj

    def testCheckResultParseOK(self):
        obj = TA.CheckResult_ParseOK()
        obj.value = "1"
        obj.result = 1
        obj.parseResult = "1"
        assert obj.isRight()
        assert str(obj) == "CheckResult: Parse and Set successful. Parse result: 1"
        assert obj
        cell = Parse(tag="td", body="Foo")
        obj.annotateCell(cell)
        assert cell.tagIsNotAnnotated()
        counts = Counts()
        obj.tabulateResult(counts)
        assert counts == Counts(0)

    def testCheckResultRightWithDefaultValue(self):
        obj = TA.CheckResult_Right()
        assert obj.isRight()
        assert str(obj) == "CheckResult_Right. actual data: 'None'"
        assert obj
        cell = Parse(tag="td", body="Foo")
        obj.annotateCell(cell)
        assert cell.tagIsRight()
        counts = Counts()
        obj.tabulateResult(counts)
        assert counts == Counts(1)

    def testCheckResultRightWithSuppliedValue(self):
        obj = TA.CheckResult_Right("Bar")
        assert obj.isRight()
        assert str(obj) == "CheckResult_Right. actual data: 'Bar'"
        assert obj
        cell = Parse(tag="td", body="Foo")
        obj.annotateCell(cell)
        assert cell.tagIsRight()
        assert cell.infoIsRight()
        assert cell.body.find("Bar") > -1

    def testCheckResultWrongWithDefaultValue(self):
        obj = TA.CheckResult_Wrong()
        assert not obj.isRight()
        assert str(obj) == "CheckResult_Wrong. actual data: 'None'"
        assert not obj
        cell = Parse(tag="td", body="Foo")
        obj.annotateCell(cell)
        assert cell.tagIsWrong()
        counts = Counts()
        obj.tabulateResult(counts)
        assert counts == Counts(0, 1)

    def testCheckResultWrongWithSuppliedValue(self):
        obj = TA.CheckResult_Wrong("Bar")
        assert not obj.isRight()
        assert str(obj) == "CheckResult_Wrong. actual data: 'Bar'"
        assert not obj
        cell = Parse(tag="td", body="Foo")
        obj.annotateCell(cell)
        assert cell.tagIsWrong()
        assert cell.infoIsWrong()
        assert cell.body.find("Bar") > -1

    def testCheckResultInfo(self):
        obj = TA.CheckResult_Info("Bar")
        assert not obj.isRight()
        assert str(obj) == "CheckResult_Info. actual data: 'Bar'"
        assert not obj
        cell = Parse(tag="td", body="Foo")
        obj.annotateCell(cell)
        assert cell.tagIsNotAnnotated()
        assert cell.infoIsIgnored()
        assert cell.body.find("Bar") > -1
        counts = Counts()
        obj.tabulateResult(counts)
        assert counts == Counts(0)

    def testCheckResultIgnore(self):
        obj = TA.CheckResult_Ignore()
        assert not obj.isRight()
        assert str(obj) == "CheckResult_Ignore"
        assert not obj
        cell = Parse(tag="td", body="Foo")
        obj.annotateCell(cell)
        assert cell.tagIsIgnored()
        counts = Counts()
        obj.tabulateResult(counts)
        assert counts == Counts(0,0,1)

    def testCheckResultExceptionWithNoTrace(self):
        try:
            raise FitException("missingActorNameCell")
        except FitException, exc:
            obj = TA.CheckResult_Exception(exc)
        assert not obj.isRight()
        assert str(obj).find("CheckResult_Exception") > -1
        assert not obj
        cell = Parse(tag="td", body="Foo")
        obj.annotateCell(cell)
        assert cell.tagIsError()
        assert not cell.infoIsTrace()
        counts = Counts()
        obj.tabulateResult(counts)
        assert counts == Counts(0,0,0,1)

    def testCheckResultExceptionWithTrace(self):
        try:
            raise FitException("WrongValueForTypeAdapter")
        except FitException, exc:
            obj = TA.CheckResult_Exception(exc)
        assert not obj.isRight()
        assert str(obj).find("CheckResult_Exception") > -1
        assert not obj
        cell = Parse(tag="td", body="Foo")
        obj.annotateCell(cell)
        assert cell.tagIsError()
        assert cell.infoIsTrace()
        counts = Counts()
        obj.tabulateResult(counts)
        assert counts == Counts(0,0,0,1)

    def testCheckResultExceptionWithIgnore(self):
        try:
            raise FitException("IgnoreException")
        except FitException, exc:
            obj = TA.CheckResult_Exception(exc)
        assert not obj.isRight()
        assert str(obj) == "CheckResult: Do Nothing object"
        assert not obj
        cell = Parse(tag="td", body="Foo")
        obj.annotateCell(cell)
        assert not cell.tagIsError()
        assert not cell.infoIsTrace()
        counts = Counts()
        obj.tabulateResult(counts)
        assert counts == Counts(0)

    def testCheckResultExceptionRightWithTrace(self):
        try:
            raise FitException("WrongValueForTypeAdapter")
        except FitException, exc:
            obj = TA.CheckResult_Exception(exc)
        obj.__class__ = TA.CheckResult_ExceptionRight
        assert obj.isRight()
        assert str(obj).find("CheckResult_ExceptionRight") > -1
        assert obj
        cell = Parse(tag="td", body="Foo")
        obj.annotateCell(cell)
        assert cell.tagIsRight()
        assert cell.infoIsTrace()
        counts = Counts()
        obj.tabulateResult(counts)
        assert counts == Counts(1)

    def testCheckResultExceptionWrongWithTrace(self):
        try:
            raise FitException("WrongValueForTypeAdapter")
        except FitException, exc:
            obj = TA.CheckResult_Exception(exc)
        obj.__class__ = TA.CheckResult_ExceptionWrong
        assert not obj.isRight()
        assert str(obj).find("CheckResult_ExceptionWrong") > -1
        assert not obj
        cell = Parse(tag="td", body="Foo")
        obj.annotateCell(cell)
        assert cell.tagIsWrong()
        assert cell.infoIsTrace()
        counts = Counts()
        obj.tabulateResult(counts)
        assert counts == Counts(0,1)

    def testCheckResultExceptionWrongWithNoTrace(self):
        try:
            raise FitException("InvokeField")
        except FitException, exc:
            obj = TA.CheckResult_Exception(exc)
        obj.__class__ = TA.CheckResult_ExceptionWrong
        assert not obj.isRight()
        assert str(obj).find("CheckResult_ExceptionWrong") > -1
        assert not obj
        cell = Parse(tag="td", body="Foo")
        obj.annotateCell(cell)
        assert cell.tagIsWrong()
        assert not cell.infoIsTrace()
        counts = Counts()
        obj.tabulateResult(counts)
        assert counts == Counts(0,1)



class SpecifyDefaultTypeAdapter(TestUtilities):
    def setUp(self):
        print '%s %s' % (self.id(), self.shortDescription())
        setupFitGlobalForTests("Batch")

    def tearDown(self):
        setupFitGlobalForTests("Batch")
        if hasattr(AdapterMock1, "noDictVar"):
            del AdapterMock1.noDictVar

    def shouldHandleTheseObjectsAsFields(self):
        def mustTranslateTo(obj, className):
            AdapterMock1.noDictVar = obj
            inst, acc = self._buildDefaultTypeAdapter("Default", "noDictVar")
            adapterName = acc.adapter.__class__.__name__
            assert adapterName == className, (
                "class name expected: '%s' actual: '%s'" %
                (className, adapterName))
        mustTranslateTo("", "StringAdapter")
        mustTranslateTo(1, "IntAdapter")
        mustTranslateTo(1.0, "FloatAdapter")
        mustTranslateTo(True, "BooleanAdapter")
        mustTranslateTo(1.0 + 2.4j, "ComplexAdapter")
        mustTranslateTo(["Hi There!"], "ListAdapter")
        mustTranslateTo(("Goodbye!",), "TupleAdapter")
        mustTranslateTo({"Life": 42}, "DictAdapter")

    def shouldHandleTheseObjectsReturnedFromGetter(self):
        def mustTranslateTo(body, obj, className):
            AdapterMock1.noDictVar = obj
            inst, acc = self._buildDefaultTypeAdapter("Default", "noDictGetter")
            cell = Parse(tag="tr", body=body)
            result = acc.check(cell)
            assert result, "%s == %s returned %s" % (body, obj, result)
            adapterName = acc.adapter.__class__.__name__
            assert adapterName == className, (
                "class name expected: '%s' actual: '%s'" %
                (className, adapterName))
        mustTranslateTo("foo", "foo", "StringAdapter")
        mustTranslateTo("1", 1, "IntAdapter")
        mustTranslateTo("1.0", 1.0, "FloatAdapter")
        mustTranslateTo("true", True, "BooleanAdapter")
        mustTranslateTo("1.0 + 2.4j", 1.0 + 2.4j, "ComplexAdapter")
        mustTranslateTo('["Hi There!"]', ["Hi There!"], "ListAdapter")
        mustTranslateTo('("Goodbye!",)', ("Goodbye!",), "TupleAdapter")
        mustTranslateTo('{"Life": 42}', {"Life": 42}, "DictAdapter")

    def shouldRaiseExceptionIfAppExitDeniesImplicitDefaultTA(self):
        class DenyDefaultExit(object):
            def canDefaultMissingMetadata(self):
                return False
        self._installApplicationExit(DenyDefaultExit)
        instance = AdapterMock1()
        self._checkFitException(TypeAdapter.on, (instance, "noDictVar"),
                               "NoTypeInfo")

    def shouldAcceptMissingMetadataIfAppExitAllowsImplicitDefaultTA(self):
#        __pychecker__ = "unusednames=[['Accessor']]" # doesn't work
        __pychecker__ = "no-local" # Accessor
        class AcceptDefaultExit(object):
            def canDefaultMissingMetadata(self):
                return True
        self._installApplicationExit(AcceptDefaultExit)
        instance = AdapterMock1()
        Accessor = TypeAdapter.on(instance, "noDictVar")
        # ??? why no check?

    def shouldRaiseExceptionForMissingMetadataIfNoAppExit(self):
        instance = AdapterMock1()
        self._checkFitException(TypeAdapter.on, (instance, "noDictVar"),
                               "NoTypeInfo")

    def shouldRaiseExceptionForMissingFieldIfDefaultTARequested(self):
        instance = AdapterMock1()
        self._checkFitException(TypeAdapter.on,
                (instance, "noDictVar", {"noDictVar": "Default"}),
                               "defaultTANoAttribute")

    def shouldRaiseExceptionIfGetAdapterForObjectReturnsFalse(self):
        class CantUseObject(object):
            def getAdapterForObject(self, anObj):
                return False
            def canDefaultMissingMetadata(self):
                return True
        self._installApplicationExit(CantUseObject)
        AdapterMock1.noDictVar = None
        instance = AdapterMock1()
        self._checkFitException(TypeAdapter.on, (instance, "noDictVar"),
                               "defaultTAinvalidAdapter")

    def shouldRaiseExceptionIfDefaultTAOnAProperty(self):
        instance = AdapterMock1()
        self._checkFitException(TypeAdapter.on,
                (instance, "intProperty", {"intProperty": "Default"}),
                               "descriptorInvalidForDefaultTA")

    def shouldUseStringAdapterForDefaultTAOnSetterMethod(self):
        instance = AdapterMock1()
        accessor = TypeAdapter.on(instance, "setInt", {"setInt": "Default"})
        accessor.set("a string")
        assert instance.anIntVar == "a string"

class specifyMapTypeAdapterExit(TestUtilities):
    def setUp(self):
        print '%s %s' % (self.id(), self.shortDescription())
        setupFitGlobalForTests("Batch")

    def tearDown(self):
        setupFitGlobalForTests("Batch")

    def shouldRaiseExceptionWhenExitReturnsFalse(self):
        class RefuseTypeAdapter(object):
            def mapTypeAdapter(self, anObj):
                return False
        self._installApplicationExit(RefuseTypeAdapter)
        instance = AdapterMock1()
        self._checkFitException(TypeAdapter.on, (instance, "aStrVar"),
                               "taRejected")

    def shouldAcceptAtNameIfExitReturnsAdapter(self):
        class ReturnTypeAdapter(object):
            def mapTypeAdapter(self, anObj):
                return tat.get("String")
        self._installApplicationExit(ReturnTypeAdapter)
        instance = AdapterMock1()
        accessor = TypeAdapter.on(instance, "aStrVar",
                                  {"aStrVar": "@String"})
        instance.aStrVar = ""
        accessor.set("a string")
        assert instance.aStrVar == "a string"

    def shouldBeUnableToOverrideBuiltinTypeAdapter(self):
        class ReturnTypeAdapter(object):
            def mapTypeAdapter(self, anObj):
                return tat.get("String")
        self._installApplicationExit(ReturnTypeAdapter)
        instance = AdapterMock1()
        self._checkFitException(TypeAdapter.on, (instance, "aStrVar"),
                               "taRejected")

class specifyAcquireAdapterForType(TestUtilities):
    def setUp(self):
        print '%s %s' % (self.id(), self.shortDescription())
        setupFitGlobalForTests("Batch")

    def tearDown(self):
        setupFitGlobalForTests("Batch")

    def shouldReturnFalseIfExitReturnsNone(self):
        class CantUseObject(object):
            def getAdapterForObject(self, anObj):
                return False
            def canDefaultMissingMetadata(self):
                return True
        self._installApplicationExit(CantUseObject)
        instance = AdapterMock1()
        result = TypeAdapter._acquireAdapterForType(instance, "aStrVar",
                                                    "a string", {})
        assert result is None

    def shouldReturnAdapterForStandardType(self):
        instance = AdapterMock1()
        result = TypeAdapter._acquireAdapterForType(instance, "aStrVar",
                                                    "a string", {})
        assert isinstance(result, tat["String"])

    def shouldReturnClassIfInstanceSatisfiesApplicationObjectProtocol(self):
        instance = AdapterMock1()
        result = TypeAdapter._acquireAdapterForType(instance, "aStrVar",
                                                    AValueClass(""), {})
        assert result is AValueClass

    def shouldReturnNewAdapterInstanceIfInstanceSatisfiesAdapterProtocol(self):
        instance = AdapterMock1()
        obj = CaeserTypeAdapter()
        result = TypeAdapter._acquireAdapterForType(instance, "aStrVar",
                                            obj, {})
        assert isinstance(result, CaeserTypeAdapter)
        assert result is not obj

    def shouldReturnNoneIfObjectSatisfiesNeitherProtocol(self):
        instance = AdapterMock1()
        obj = ReverseCellHandler()
        result = TypeAdapter._acquireAdapterForType(instance, "aStrVar",
                                            obj, {})
        assert result is None

if __name__ == '__main__':
    main(defaultTest='makeTypeAdapterTest')
