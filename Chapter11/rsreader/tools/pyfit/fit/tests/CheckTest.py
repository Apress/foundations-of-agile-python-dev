# test module for the check routines in Fixture and TypeAdapter
# copyright 2004, 2005 John H. Roth Jr.
# Licensed under the terms of the GNU Public License, Version 2 or later.
# See license.txt for conditions and exclusion of all warrenties.

import types
import unittest
from fit.Fixture import Fixture
from fit.Parse import Parse
import fit.TypeAdapter as ta
from fit.Utilities import em

try:
    False
except:
    True = 1
    False = 0

def makeCheckTest():
    theSuite = unittest.makeSuite(Test_Check, 'test')
#    theSuite.addTest(unittest.makeSuite(SpecifyFoo, 'Test'))
    return theSuite

class testClass(Fixture):
    _typeDict = {"int1": "Int"}

    def __init__(self):
        self.int1 = 1

    _typeDict["badInt"] = "Int"
    def badInt(self):
        return int("fubar")

class Test_Check(unittest.TestCase):
    def setUp(self):
        print '%s %s' % (self.id(), self.shortDescription())

    def _checkTest(self, method, cellContent, resultObjName):        
        obj = testClass()
        adapter = ta.on(obj, method)
        cell = Parse(tag="td", body=cellContent)
        checkResult = adapter.check(cell)
        assert checkResult.__class__.__name__ == resultObjName
        return checkResult

    def testIntegerRight(self):
        self._checkTest("int1", "1", "CheckResult_Right")

    def testIntegerWrong(self):
        self._checkTest("int1", "2", "CheckResult_Wrong")

    def testNotAnInteger(self):
        self._checkTest("int1", "fubar", "CheckResult_Exception")

    def testExceptionCellHandlerExceptionType(self):
        self._checkTest("badInt", "exception[ValueError]",
                        "CheckResult_Right")

    def testExceptionErrorKeyword(self):
        self._checkTest("badInt", "error", "CheckResult_Right")

    def testExceptionErrorKeywordNoError(self):
        self._checkTest("int1", "error", "CheckResult_Wrong")

    def testExceptionCellHandlerExceptionMessage(self):
        self._checkTest("badInt",
                        "exception['invalid literal for int(): fubar']",
                        "CheckResult_Right")

    def testExceptionCellHandlerExceptionNameAndMessage(self):
        self._checkTest("badInt",
                        "exception[ValueError: 'invalid literal for int(): fubar']",
                        "CheckResult_Right")

    def testIntegerRightFail(self):
        self._checkTest("int1", "Fail[1]", "CheckResult_Wrong")

    def testIntegerWrongFail(self):
        self._checkTest("int1", "Fail[2]", "CheckResult_Right")

    def testIntegerRightFail2(self):
        self._checkTest("int1", "Fail[Fail[1]]", "CheckResult_Right")

    def testIntegerWrongFail2(self):
        self._checkTest("int1", "Fail[Fail[2]]", "CheckResult_Wrong")

    def testExceptionCellHandlerExceptionTypeFail(self):
        self._checkTest("badInt", "Fail[exception[ValueError]]",
                        "CheckResult_Wrong")

    def testExceptionCellHandlerExceptionType2Fail(self):
        self._checkTest("badInt", "Fail[Fail[exception[ValueError]]]",
                        "CheckResult_Right")

        

    def tearDown(self):
        pass

if __name__ == '__main__':
    unittest.main(defaultTest='makeCheckTest')
