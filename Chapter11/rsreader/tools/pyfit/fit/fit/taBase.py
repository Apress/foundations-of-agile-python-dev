# Distributed TypeAdapters for FIT
#legalStuff jr03-05
# Copyright 2003-2005 John H. Roth Jr.
# Released under the terms of the General Public License (GPL), Release 2.1 or later
# See license.txt for terms and disclaimer of all warrenties and liability.
# Last updated for Release 0.8a1
#endLegalStuff

import compiler
import math
import operator
import re
import struct
import sys
import time
from types import *

import fit
from fit.FitException import FitException
from fit import CellHandlers
#import fit.CellHandlers as CellHandlers
from fit.CellHandlers import *
from fit import FitGlobal
from fit.Parse import Parse
from fit.taTable import typeAdapterTable, typeToAdapter, _isApplicationProtocol
from fit.Utilities import em, firstNonNone

try:
    False
except: #pragma: no cover
    True = 1
    False = 0

## Type Adapters ####################################

class TypeAdapter(object):
    fitAdapterProtocol = "Basic"
    def __init__(self, instance, name, typeName, metaData = None):
        __pychecker__ = "no-argsused" # instance and name
        self.typeName = typeName
        self.metaData = metaData

    def parse(self, s): #pragma: no cover
        return s
    
    def equals(self, a, b):
        return a == b

    def stringEquals(self, cellText, b):
        if isinstance(cellText, StringTypes):
            cellText = self.parse(cellText)
        return self.equals(cellText, b)

    def toString(self, o):
        return str(o)

    def _safeEval(self, s):
        """
        Evaluate strings that only contain the following structures:
        const,  tuple,  list,   dict
        Taken from c.l.py newsgroup posting Nov 5, 2003 by Huaiyu Zhu at IBM Almaden
        ??? this may need to be expanded to support complex numbers in lists, etc.
        """
        #print "in _safeEval. input: '%s'" % s
        node1 = compiler.parse(s)

        # !!! special case of attempting to compile a lone string
        if node1.doc is not None and len(node1.node.nodes) == 0:
            #print "in _safeEval. string: '%s' found as docstring" % node1.doc
            return node1.doc

        #print "in _safeEval. nodes: '%s'" % (node1,)
        stmts = node1.node.nodes
        assert len(stmts) == 1
        node = compiler.parse(s).node.nodes[0]
        assert node.__class__ == compiler.ast.Discard
        nodes = node.getChildNodes()
        assert len(nodes) == 1
        result = self._safeAssemble(nodes[0])
        #print "in _safeEval result: '%s'" % (result,)
        return result

    seq_types = {
        compiler.ast.Tuple: tuple,
        compiler.ast.List: list,
        }
    map_types = {
        compiler.ast.Dict: dict,
        }

    oper_types = {
        compiler.ast.Add: operator.add,
        compiler.ast.Sub: operator.sub,
        }

    builtin_consts = {
        "True": True,
        "False": False,
        "None": None,
        }

    def _safeAssemble(self, node):
        """ Recursively assemble parsed ast node """
        cls = node.__class__
        if cls == compiler.ast.Const:
            return node.value
        elif cls in self.seq_types:
            nodes = node.nodes
            args = map(self._safeAssemble, nodes)
            return self.seq_types[cls](args)
        elif cls in self.map_types:
            keys, values = zip(*node.items)
            keys = map(self._safeAssemble, keys)
            values = map(self._safeAssemble, values)
            return self.map_types[cls](zip(keys, values))
        elif cls in self.oper_types:
            left = self._safeAssemble(node.left)
            right = self._safeAssemble(node.right)
            if type(left) == type(1.0j) or type(right) == type(1.0j):
                return self.oper_types[cls](left, right)
            else:
                raise FitException, ("Parse001",)
        elif cls == compiler.ast.Name:
            result = self.builtin_consts.get(node.name, "?")
            if result != "?":
                return result
            else:
                raise FitException, ("Parse002", node.name)
#                return node.name
        else:
            raise FitException, ("Parse003", cls)

## Subclasses ##############################

# This adapter is a proxy for any value object that has a
# constructor that takes a string, an __eq__() and a __str__() method.

class GenericAdapter(TypeAdapter):
    def __init__(self, instance, name, typeName, metaData = None):
        super(GenericAdapter, self).__init__(instance, name, typeName,
                                             metaData = metaData)
        self.proxiedClass = self.metaData[name + ".ValueClass"]

    def parse(self, s):
        method = getattr(self.proxiedClass, "parse", None)
        if method is not None: #pragma: no cover # shouldn't be supported
            return self.proxiedClass.parse(s)
        return self.proxiedClass(s)
typeAdapterTable["Generic"] = GenericAdapter

# XXX This may not be an adequate substitute for the built-in types
class DefaultAdapter(TypeAdapter):
    fitAdapterProtocol = "EditedString"
    def equals(self, s, obj): #pragma: no cover # 
        new = obj.__class__(s)
        return new == obj
typeAdapterTable["Default"] = DefaultAdapter

class StringAdapter(TypeAdapter):
    def parse(self, s):
        s1 = s.strip()
# removed to see if cell handlers work properly
##        # Fitnessse hacks
##        if type(s1) == type(""):
##            if s1 == "null": return None
##            if s1 == "blank": return ""
##        else:
##            if s1 == u"null": return None
##            if s1 == u"blank": return u""
##        # end objectMentor hack.
        if self._isEvalNeeded(s1):
            value = self._safeEval(s1)
            if isinstance(value, StringTypes):
                #print "in StringAdapter.parse. Returning _safeEval result: '%s'" % (
                #    value)
                return value
        return s1

    def _isEvalNeeded(self, s): # need a regular expression.
        if len(s) <= 1: return False
#        if s.find("\\") != -1: return True
        if s[-1] not in ('"', "'"): return False
        if s[0] not in ("'", '"') and s[1] not in ("'", '"'): return False
        return True

    def toString(self, s):
        if s is None: return None
        s1 = s.strip()
        if s1 == "": return "blank"
        if s1 == u"": return "blank"
        return s1
typeAdapterTable["String"] = StringAdapter
typeToAdapter[str] = StringAdapter

class TaggedStringAdapter(TypeAdapter):      
    fitAdapterProtocol = "RawString"
    def isCellHandlerApplicable(self, a): #pragma: no cover # who cares?
        return False

typeAdapterTable["TaggedString"] = TaggedStringAdapter
typeAdapterTable["RawString"] = TaggedStringAdapter

class IntAdapter(TypeAdapter):
    def parse(self,s):
        return int(s)

typeAdapterTable["Int"] = IntAdapter
typeAdapterTable["Integer"] = IntAdapter
typeToAdapter[int] = IntAdapter

class LongAdapter(TypeAdapter):
    def parse(self,s):
        return long(s)
typeAdapterTable["Long"] = LongAdapter
typeToAdapter[long] = LongAdapter

# Floating Point Type Adapter
# Stuff for Floating Point Special Values

# For references to all the bit twiddling see 
# http://babbage.cs.qc.edu/courses/cs341/IEEE-754references.html#kevin_chart
# or any other ref that gives the bit patterns for the IEEE 754 standard

# check endianess
_big_endian = sys.byteorder == "big"

# and define appropriate constants
if(_big_endian): #pragma: no cover
    Ind    = struct.unpack('d', '\xFF\xF8\x00\x00\x00\x00\x00\x00')[0]
    NaN    = struct.unpack('d', '\xFF\xF8\x00\x00\x00\x00\x00\x01')[0]
    PosInf = struct.unpack('d', '\x7F\xF0\x00\x00\x00\x00\x00\x00')[0]
else:
    Ind    = struct.unpack('d', '\x00\x00\x00\x00\x00\x00\xf8\xff')[0]
    NaN    = struct.unpack('d', '\x01\x00\x00\x00\x00\x00\xf8\xff')[0]
    PosInf = struct.unpack('d', '\x00\x00\x00\x00\x00\x00\xf0\x7f')[0]
NegInf = -PosInf

_floatSpecialValueDict = {
            "inf": PosInf,
            "+inf": PosInf,
            "-inf": NegInf,
            "nan": NaN,
            "ind": Ind,
            }

class FloatAdapter(TypeAdapter):
    fitAdapterProtocol = "EditedString"
    def __init__(self, instance, name, typeName, metaData = None):
        __pychecker__ = "no-noeffect" # two or stmts below
        super(FloatAdapter, self).__init__(instance, name, typeName,
                                           metaData = metaData)
        metaData = metaData or {}
        self.precision = metaData.get("%s.precision" % name) or 4
        self.charBounds = metaData.get("%s.charBounds" % name) or "5"
        self.checkOptions = "eer" # current default, change for 2.0???
        self.checkOptions = firstNonNone(FitGlobal.appConfigInterface(
                            "fpTypeAdapterCheck"), self.checkOptions)
        self.checkOptions = firstNonNone(metaData.get(
                            "%s.checkType" % name), self.checkOptions)

    def parse(self, s):
        if isinstance(s, StringTypes):
            specValue = _floatSpecialValueDict.get(s.strip().lower())
            if specValue is not None:
                return specValue
        return float(s)

    def equals(self, a, b):
        if isinstance(a, StringTypes):
            return self._stringEquals(a, b)
        elif (isinstance(b, StringTypes)):
            return self._stringEquals(b, a)
        else:
            return self._objEquals(a, b)
    stringEquals = equals

    def _objEquals(self, a, b):
        if self.checkOptions[0] == "f":
            raise FitException("noFloatCheck1")
        # XXX does not handle NaN properly
        if a == b:
            return True # hack!
        # same routine unittest supposedly uses.
        return round(a - b, self.precision) == 0

    def _stringEquals(self, a, b):
        self.value = a
        parts = re.split(ur"(<=|<|>=|>|\+/-|\u00b1|\u2264|\u2265)", a)
        parts = [x.strip() for x in parts]
        if len(parts) == 1:
            if self.checkOptions[0] == "f":
                raise FitException("noFloatCheck1")
            specValue = _floatSpecialValueDict.get(parts[0].lower())
            # XXX does not handle NaN correctly.
            # XXX does not handle case of b being a special value.
            if specValue is not None:
                return specValue == b
            if self.checkOptions[0] == "c":
                return self._objEquals(float(parts[0]), b)
            return self._appendCheck(a, b)
        if len(parts) == 3:
            if parts[1] in ("+/-", u"\u00b1"):
                return self._epsilonCheck(parts, b)
            return self._openRangeCheck(parts, b)
        elif len(parts) == 5:
            return self._rangeCheck(parts, b)
        else:
            raise FitException("floatImproperSyntax", self.value)

    def _appendCheck(self, a, b):
        a = a.strip()
        if isinstance(b, StringTypes): b = self.parse(b)
        locE = a.lower().find('e')
        locDot = a.find('.')
        if locE >= 0:
            bound = a[:locE] + self.charBounds + a[locE:]
        elif locDot >= 0:
            bound = a + self.charBounds
        else:
            bound = a + "." + self.charBounds
        a = self.parse(a)
        bound = abs(a - self.parse(bound))
        return not (abs(a - b) > bound)

    def _epsilonCheck(self, parts, aFloat):
        if self.checkOptions[1] == "f":
            raise FitException("noFloatCheckEpsilon")
        base = self.parse(parts[0])
        epsilon = self.parse(parts[2])
        low = base - epsilon
        high = base + epsilon
        if low < high:
            return low < aFloat < high
        else:
            return high <= aFloat <= low

    def _rangeCheck(self, parts, aFloat):
        a = self.parse(parts[0])
        b = self.parse(parts[4])
        result = self._compare(a, parts[1], aFloat)
        if result:
            result = self._compare(aFloat, parts[3], b)
        if self.checkOptions[2] == "f":
            raise FitException("noFloatCheckRange")
        return result

    def _compare(self, a, op, b):
        if op == "<":
            return a < b
        if op in ("<=", u"\u2264"):
            return a <= b
        if op == ">":
            return a > b
        if op in (">=", u"\u2265"):
            return a >= b
        raise FitException("invRangeExp", self.value) #pragma: no cover
        # ??? regex won't allow anything except the values above.

    def _openRangeCheck(self, parts, aFloat):
        a = self._parse(parts[0])
        b = self._parse(parts[2])
        if a is None and b is None:
            raise FitException("invRangeExp", self.value)
        if a is not None and b is not None:
            raise FitException("invRangeExp", self.value)
        if a is None:
            a = aFloat
        else:
            b = aFloat

        result = self._compare(a, parts[1], b)
        if self.checkOptions[2] == "f":
            raise FitException("noFloatCheckRange")
        return result

    def _parse(self, aString):
        try:
            result = self.parse(aString)
        except:
            result = None
        return result

    def toString(self, o):
        listVal = list(struct.unpack('8B', struct.pack('d', o)))
        if not _big_endian:
            listVal.reverse()
        exp = ((listVal[0] & 0x7f) << 4) + ((listVal[1] & 0xf0) >> 4)
        if exp != 2047:
            return str(o)
        sign = ((listVal[0]) & 0x80) >> 7
        m1bit = (listVal[1] >> 3) & 0x01
        m2plus = ((listVal[1] & 0x07) + listVal[2] + listVal[3] + listVal[4] +
             listVal[5] + listVal[6] + listVal[7])
        if sign == 1: # negative
            if m2plus == 0:
                if m1bit == 1:
                    result = "Ind"
                else:
                    result = "-Inf"
            else:
                result = "NaN"
        else:
            if m1bit == 0 and m2plus == 0:
                result = "Inf"
            else: #pragma: no cover # no way of entering this variant!
                result = "NaN"
        return result

typeAdapterTable["Float"] = FloatAdapter
typeToAdapter[float] = FloatAdapter

class ComplexAdapter(TypeAdapter):
    def __init__(self, instance, name, typeName, metaData = None):
        super(ComplexAdapter, self).__init__(instance, name, typeName,
                                           metaData = metaData)
        self.precision = metaData.get("%s.precision" % name) or 0.5

    def parse(self, s):
        value = "".join(s.split(" "))
        return complex(value)

    def equals(self, a, b):
        diff = a - b
        radius = math.sqrt(diff.real ** 2 + diff.imag ** 2)
        return radius < self.precision
typeAdapterTable["Complex"] = ComplexAdapter
typeToAdapter[complex] = ComplexAdapter

class BooleanAdapter(TypeAdapter):
    _booleanTable = {
        "true": True, "t": True, "yes": True, "1": True, "y": True, "+": True,
        "false": False, "f": False, "no": False, "0": False, "n": False, "-": False,
        }

    def __init__(self, instance, name, typeName, metaData = None):
        super(BooleanAdapter, self).__init__(instance, name, typeName,
                                           metaData = metaData)
        self._addToDict(name, "true", metaData, True)
        self._addToDict(name, "false", metaData, False)

    def _addToDict(self, name, mKey, metaData, value):
        if metaData.has_key("%s.%s" % (name, mKey)) is False:
            return
        aList = metaData["%s.%s" % (name, mKey)]
        self._booleanTable = self._booleanTable.copy()
        if isinstance(aList, StringTypes):
            aList = [aList]
        for key in aList:
            self._booleanTable[key.lower()] = value

    
    def parse(self, s):
        result = self._strToBool(s, None)
        if result not in (True, False):
            raise FitException, ("BooleanValue", s)
        return result

    def _strToBool(self, value, default):
        if isinstance(value, StringTypes):
            return self._booleanTable.get(value.lower(), default)
        if value in (0, 1, True, False):
            return value
        else:
            return default

    def equals(self, a, b):
        a = self._strToBool(a, "A")
        b = self._strToBool(b, "B")
        return a == b

    def toString(self, value):
        return str(self._strToBool(value, False))
typeAdapterTable["Boolean"] = BooleanAdapter
typeToAdapter[bool] = BooleanAdapter

class DateAdapter(TypeAdapter):
    def __init__(self, instance, name, typeName, metaData = None):
        super(DateAdapter, self).__init__(instance, name, typeName,
                                          metaData = metaData)

    def parse(self, aDate):
        aList = []
        for char in aDate:
            if char.isalnum():
                aList.append(char)
            else:
                aList.append(" ")
        aStr = "".join(aList)
        aList = aStr.split()
        month = None
        day = None
        year = None
        #print "in DateAdapter.parse('%s') %s" % (aDate, aList)
        if len(aList) != 3:
            raise FitException, "SmartDateFormatError"
        for item in aList:
            if item.isalpha():
                month = item
            elif item.isdigit() is False:
                raise FitException, "SmartDateFormatError"
            elif len(item) == 4:
                year = int(item)
            elif 1 <= int(item) <= 31:
                day = int(item)
            else:
                raise FitException, "SmartDateFormatError"
        #print "after breakout year: %s month: %s day: %s" % (
        #      year, month, day)
        if (year and month and day) is None:
            raise FitException, "SmartDateFormatError"
        month = monthTable.get(month[:3].lower())
        #print "after month lookup month: %s" % month
        aStr = "%04i %s %s" % (year, month, day)
        result = time.strptime(aStr, "%Y %m %d")
        #print "after strptime: '%s'" % (result,)
        return result
    
    def getTuple(self, a):
        if isinstance(a, StringTypes):
            return self.parse(a)
        if hasattr(a, "timetuple"): #pragma: no cover
            return a.timetuple() # add test when 2.2 support dropped
        return a

    def equals(self, a, b):
        aTuple = self.getTuple(a)
        bTuple = self.getTuple(b)
        return aTuple[:3] == bTuple[:3]

    def toString(self, o):
        aTuple = self.getTuple(o)
        result = "%04i %s %s" % (aTuple[0], monthNumList[aTuple[1]], aTuple[2])
        return result

typeAdapterTable["Date"] = DateAdapter
monthTable = {"jan": 1, "january": 1, "feb": 2, "february": 2, "mar": 3,
              "march": 3, "apr": 4, "april": 4, "may": 5, "jun": 6, "june": 6,
              "jul": 7, "july": 7, "aug": 8, "august": 8, "sep": 9,
              "september": 9, "oct": 10, "october": 10, "nov": 11, 
              "november": 11, "dec": 12, "december": 12}
monthNumList = ["", "January", "February", "March", "April", "May", "June",
               "July", "August", "September", "October", "November", "December"]

class ListAdapter(TypeAdapter):
    def __init__(self, instance, name, typeName, metaData = None):
        super(ListAdapter, self).__init__(instance, name, typeName,
                                          metaData = metaData)
        self._delims = ('[', ']')
        scalarKeyName = "%s.scalarType" % name
        scalarType = metaData.get(scalarKeyName)
        if scalarType is None:
            self.scalarAdapter = None
            return
        newMetaData = metaData.copy()
        del newMetaData[scalarKeyName]
        newMetaData[name] = scalarType
        self.scalarAdapter = fit.taTable._getTypeAdapter(None, name, newMetaData)

    def parse(self, text):
        startDelim, endDelim = self._delims
        stripped = text.strip()
        if stripped.startswith(startDelim):
            result = self._safeEval(stripped)
        elif self.scalarAdapter is None:
            if stripped.count(',') == 0: # hack for tuple
                endDelim = ',' + endDelim
            result = self._safeEval(startDelim + stripped + endDelim)
        else:
            result = [self.scalarAdapter.parse(x.strip()) for x in text.split(",")]
        return result

    def equals(self, a, b):
        # XXX Basic protocol should handle this.
        # ToDo some diagnosis of where the mismatch is.
        if isinstance(a, StringTypes):
            a = self.parse(a)
        return a == b
   
typeAdapterTable["List"] = ListAdapter
typeToAdapter[list] = ListAdapter

class TupleAdapter(ListAdapter):
    def __init__(self, instance, name, typeName, metaData = None):
        super(TupleAdapter, self).__init__(instance, name, typeName,
                                      metaData = metaData)
        self._delims = ('(', ')')

    def parse(self, text):
        return tuple(super(TupleAdapter, self).parse(text))
typeAdapterTable["Tuple"] = TupleAdapter
typeToAdapter[tuple] = TupleAdapter

class DictAdapter(ListAdapter):
    def __init__(self, instance, name, typeName, metaData = None):
        super(DictAdapter, self).__init__(instance, name, typeName,
                                      metaData = metaData)
        self._delims = ('{', '}')

typeAdapterTable["Dict"] = DictAdapter
typeToAdapter[dict] = DictAdapter

