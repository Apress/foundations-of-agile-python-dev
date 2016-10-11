# test module for Variations
#legalStuff jr04-06
# Copyright 2004-2006 John H. Roth Jr.
# Released under the terms of the General Public License (GPL), Release 2.1 or later
# See license.txt for terms and disclaimer of all warrenties and liability.
# Last updated for Release 0.8a1
#endLegalStuff
# Just a few tests for additions to Variations. See FrameworkTest for older
# tests that came with the java version.
# 0.8a2 - accept underscore for camel and Graceful Names

import unittest
from fit.FitException import FitException
from fit.InitEnvironment import FG, setupFitGlobalForTests
import fit.Variations as Variations
from tests.TestCommon import FitTestCommon

try:
    False
except:
    True = 1
    False = 0

def makeVariationsTest():
    theSuite = unittest.makeSuite(SpecifyVariations, 'test')
    theSuite.addTest(unittest.makeSuite(SpecifyMapLabel, "should"))
    return theSuite

class SpecifyVariations(unittest.TestCase):
    def setUp(self):
        print '%s %s' % (self.id(), self.shortDescription())

    def testCamel(self):
        obj = Variations.VariationsBase()
        for header, identifier in [("hi there!", "hiThere"),
                                   ("123.45", "one2345"),
                                   ("pass", "pass_"),
                                   ("try_this", "try_this"), #0.8a2 was tryThis
                                   ("Leading caps", "LeadingCaps"),
                                   ("One2buckle My shoe", "One2buckleMyShoe"),
                                   ]:
            result = obj.camel(header)
            assert result == identifier, (
                "'%s' should transform to: '%s' is: '%s'" %
                (header, identifier, result))

    def testGracefulName(self):
        obj = Variations.FitNesseVariation()
        for header, identifier in [("hi there!", "hiThere"),
                                   ("", ""),
                                   ("123.45", "one2345"),
                                   ("pass", "pass_"),
                                   ("try_this", "try_this"), # 0.8a2 was tryThis
                                   ("Leading caps", "LeadingCaps"),
                                   ("One2buckle My shoe", "One2BuckleMyShoe"),
                                   ]:
            result = obj.camel(header)
            assert result == identifier, (
                "'%s' should transform to: '%s' is: '%s'" %
                (header, identifier, result))

    def testExtendedCamel(self):
        obj = Variations.VariationsBase()
        for label, identifier in [
            ("two words", "twoWords"),
            ("three wee words", "threeWeeWords"),
            ("\" hi \"", "quoteHiQuote"),
            ("!#$%age", "bangHashDollarPercentAge"),
            ("&'()*", "ampersandSingleQuoteLeftParenthesisRightParenthesisStar"),
            ("+,-./:", "plusCommaMinusDotSlashColon"),
            (";=?", "semicolonEqualsQuestion"),
            ("@[]\\", "atLeftSquareBracketRightSquareBracketBackslash"),
            ("^`{}~", "caretBackquoteLeftBraceRightBraceTilde"),
            ("cost $", "costDollar"),
            ("cost$", "costDollar"),
            ("!", "bang"),
            ("!!", "bangBang"),
            ("meet @", "meetAt"),
            ("rick@mugridge.com", "rickAtMugridgeDotCom"),
            ("", "blank"),
            ("2 words", "twoWords"),
            ("return", "return_"),
            (u"\u216C", u"u216C"),
            (u"\u216D\uFFFE", u"u216DuFFFE"),
            (u"\uFFFF", u"uFFFF"),
            (u"\u0041b", u"Ab"),
            ]:
            result = obj._extendedLabelMapping(label)
            assert result == identifier, (
                "'%s' should transform to: '%s' is: '%s'" %
                (label, identifier, result))

    def tearDown(self):
        pass

class SpecifyMapLabel(FitTestCommon):
    def setUp(self):
        print '%s %s' % (self.id(), self.shortDescription())
        setupFitGlobalForTests("Batch")
        self.obj = Variations.VariationsBase()

    def tearDown(self):
        setupFitGlobalForTests("Batch")

    def mustMapLabel(self, given, kind, expected):
        result = self.obj.mapLabel(given, kind)
        assert expected == result, ("given: '%s' kind: '%s' expected: '%s' result: '%s'"
                                    % (given, kind, expected, result))

    def shouldInvokeCamel(self):
        self.mustMapLabel("3teen <4teen", "camel", "threeteen4teen")

    def shouldInvokeGracefulNames(self):
        self.mustMapLabel("3teen <4teen", "gracefulNames", "threeTeen4Teen")

    def shouldInvokeExtended(self):
        self.mustMapLabel("3teen <4teen", "extended", "threeteenLessThan4teen")

    def shouldInvokeCamelForDefaultAndNotFitNesse(self):
        self.mustMapLabel("3teen <4teen", "default", "threeteen4teen")

    def shouldInvokeGracefulNamesForDefaultAndFitNesse(self):
        FG.Environment = "FitNesse"
        self.mustMapLabel("3teen <4teen", "default", "threeTeen4Teen")

    def shouldInvokeDefaultIfKindNotSpecified(self):        
        self.mustMapLabel("3teen <4teen", None, "threeteen4teen")

    def shouldThrowExceptionIfKindIncorrect(self):
        try:
            self.mustMapLabel("3teen <4teen", "fubar", "threeteen4teen")
        except:
            return
        self.fail("expected exception not thrown. kind: 'fubar'")

    def shouldAcceptTypeFromExit(self):
        class mapLabelExit(object):
            def mapLabel(self, label):
                return ("force", "extended")
        self._installApplicationExit(mapLabelExit)
        self.mustMapLabel("Hi There!", "camel", "HiThereBang")

    def shouldReturnIdentifierFromExit(self):
        class mapLabelExit(object):
            def mapLabel(self, label):
                return ("done", label)
        self._installApplicationExit(mapLabelExit)
        self.mustMapLabel("Hi There!", "camel", "Hi There!")

if __name__ == '__main__':
    unittest.main(defaultTest='makeVariationsTest')
