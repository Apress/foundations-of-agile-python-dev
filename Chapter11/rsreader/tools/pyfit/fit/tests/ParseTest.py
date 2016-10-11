# test module for Parse
#legalStuff jr03-05
# Copyright 2003-2005 John H. Roth Jr.
# Released under the terms of the General Public License (GPL), Release 2.1 or later
# See license.txt for terms and disclaimer of all warrenties and liability.
# Last updated for Release 0.8a1
#endLegalStuff

# A lot of the unit tests for Parse are in FrameworkTest. This hasn't
# been updated since the initial conversion.

import types
from unittest import makeSuite, TestCase, main
from fit import FitGlobal
from fit import InitEnvironment
from fit.Parse import Parse, ParseException
from fit.Utilities import em

try:
    False
except: #pragma: no cover
    True = 1
    False = 0

def makeParseTest():
    theSuite = makeSuite(TestParse, 'test')
    theSuite.addTest(makeSuite(FitNesseSpecificTests, "specify"))
    return theSuite

class TestParse(TestCase):
    def setUp(self):
        print '%s %s' % (self.id(), self.shortDescription())

    def testParseException(self):
        try:
            unused = Parse("leader<table><tr><th>one</th><th>two</th><th>three</th></tr><tr><td>four</td></tr></table>trailer")
        except ParseException, e:
            assert e.offset == 17
            assert e.message == "Can't find tag: td"
            assert str(e) == "Can't find tag: td, 17"
            return
        self.fail("expected exception not thrown")

    def testMissingEndTag(self):
        try:
            unused = Parse("leader<table><tr><td>one</th></tr></table>trailer")
        except ParseException, e:
            assert e.offset == 17
            assert e.message == "Can't find tag: td"
            assert str(e) == "Can't find tag: td, 17"
            return
        self.fail("expected exception not thrown")

    def _printParseTree(self, tree): # not  unicode safe
        if tree.parts is None:
            body = tree.body
        else:
            body = id(tree.parts)
        if tree.more is None:
            trailer = tree.trailer[:5]
        else:
            trailer = id(tree.more)
        print "%s %s | %s | %s | %s | %s" % (id(tree), tree.leader[:5],
                                             tree.tag, body, tree.end,
                                             trailer)
        if tree.parts is not None:
            self._printParseTree(tree.parts)
        if tree.more is not None:
            self._printParseTree(tree.more)

    def testEmbeddedTable(self): # Rich Mugridge's enhancement
        text = ("leader<table><tr><td><table><tr><td>body1</td></tr></table>"
                "<table><tr><td>body2</td></tr></table></td></tr></table>"
                "trailer")
        p = Parse(text)
        self._printParseTree(p)
        body1 = p.parts.parts.parts.parts.parts.body
        assert body1 == "body1"
        body2 = p.parts.parts.parts.more.parts.parts.body
        assert body2 == "body2"
        assert p.trailer == "trailer"
        assert p.leader == "leader"

    def testMissingEmbeddedEndTag(self):
        text = ("leader<table><tr><td><table><tr><td>body1</td></tr>trailer")
        try:
            unused = Parse(text)
        except ParseException, e:
            assert str(e) == "Can't find tag: table, 0"
            return
        self.fail("expected exception not thrown")

# fails in subroutine - how to get a failure in the main routine?
##    def testMalformedTag(self):
##        text = ("leader<table><trtrailer")
##        try:
##            p = Parse(text)
##        except ParseException, e:
##            em("in testMalformedTag: '%s'" % str(e))
##            assert str(e) == "Can't find tag: tr, 0"
##            return
##        self.fail("expected exception not thrown")
##

    def testEmbeddedTableWithDataInEndTag(self): # Rich Mugridge's enhancement
        text = ("leader<table><tr><td><table><tr><td>body1</td></tr></table>"
                "<table><tr><td>body2</td></tr></table fubar></td></tr></table>"
                "trailer")
        p = Parse(text)
        self._printParseTree(p)
        body1 = p.parts.parts.parts.parts.parts.body
        assert body1 == "body1"
        body2 = p.parts.parts.parts.more.parts.parts.body
        assert body2 == "body2"
        assert p.trailer == "trailer"
        assert p.leader == "leader"

    def testExtractOneTable(self):
        text = ("leader<table><tr><td><table><tr><td>body1</td></tr></table>"
                "<table><tr><td>body2</td></tr></table></td></tr></table>"
                "trailer")
        p = Parse(text)
        embedded2 = p.parts.parts.parts.more
        text = embedded2.oneHTMLTagToString()
        assert text == "<table><tr><td>body2</td></tr></table>"

    def testExtractOneTableWithMalformedTrailer(self):
        text = ("leader<table><tr><td><table><tr><td>body1</td></tr></table>"
                "<table><tr><td>body2</td></tr></table></td></tr></table>"
                "trailer")
        p = Parse(text)
        embedded2 = p.parts.parts.parts.more
        embedded2.trailer = None
        text = embedded2.oneHTMLTagToString()
        assert text == "<table><tr><td>body2</td></tr></table>"

    def testRemoveNonBreakTags(self):
        text = ("leader<table><tr><td><foo><br></foo>"
                "</td></tr></table>"
                "trailer")
        p = Parse(text)
        td = p.parts.parts
        newText = td.removeNonBreakTags()
        assert newText == "<br />"

    def testRemoveMalformedNonBreakTags(self):
        assert Parse._removeNonBreakTags("<fee><br /><fi") == "<br /><fi"

    def testToPrint(self):
        text = ("leader<table><tr><td><table><tr><td>body1</td></tr></table>"
                "<table><tr><td>body2</td></tr></table></td></tr></table>"
                "trailer")
        p = Parse(text)
        newText = p.toPrint()
        assert newText == text

    def testToPrintUnicode(self):
        text = (u"leader<table><tr><td><table><tr><td>body1</td></tr></table>"
                u"<table><tr><td>body2</td></tr></table></td></tr></table>"
                u"trailer")
        p = Parse(text)
        newText = p.toPrint()
        assert newText == text
        assert isinstance(newText, types.StringType)

    def testToString(self):
        text = ("leader<table><tr><td><table><tr><td>body1</td></tr></table>"
                "<table><tr><td>body2</td></tr></table></td></tr></table>"
                "trailer")
        p = Parse(text)
        newText = p.toString()
        assert newText == text
        newText = p()
        assert newText == text

    def testStrBuiltin(self):
        text = ("leader<table><tr><td><table><tr><td>body1</td></tr></table>"
                "<table><tr><td>body2</td></tr></table></td></tr></table>"
                "trailer")
        p = Parse(text)
        newText = str(p)
        assert newText == text

    def testStrBuiltinUnicodeException(self):
        text = (u"leader<table><tr><td><table><tr><td>\x90body1</td></tr></table>"
                u"<table><tr><td>body2</td></tr></table></td></tr></table>"
                u"trailer")
        p = Parse(text)
        try:
            unused = str(p)
        except UnicodeEncodeError:
            return
        self.fail("expected exception not thrown")

    def testToList(self):
        text = (u"<table><tr><td>One</td></tr>"
                u"<tr><td>Two</td></tr></table>")
        p = Parse(text)
        aList = p.parts.toList()
        assert len(aList) == 2

    def testEquals(self):
        text = ("leader<table><tr><td><table><tr><td>body1</td></tr></table>"
                "<table><tr><td>body2</td></tr></table></td></tr></table>"
                "trailer")
        p1 = Parse(text)
        p2 = Parse(text)
        assert p1 == p2
        assert (p1 != p2) is False
        assert (p1 == None) is False
        assert (p1 == 42) is False

    def testBatchTextRoutine(self):
        cell = Parse(tag="td", body="Hi <br /> There!")
        text = cell.text()
        assert text == "Hi \n There!"

    def testGreenLabelWhenActualIsNotAString(self):
        cell = Parse(tag="td", body="aNumber: ")
        cell.addGreenLabel(42)
        assert cell.body.find("42") > -1

    def testRedLabelWhenActualIsNotAString(self):
        cell = Parse(tag="td", body="aNumber: ")
        cell.addRedLabel(42)
        assert cell.body.find("42") > -1

    def testExceptionWhereMessageIsNotStackTrace(self):
        cell = Parse(tag="td", body="Oops!")
        cell.exception("Darn it!", exc=False)
        assert cell.body == "Oops!<hr>Darn it!"

    def testExceptionWhereItsWrong(self):
        cell = Parse(tag="td", body="Oops!")
        cell.exception("Clean it up!", bkg="wrong")
        assert cell.tagIsWrong()

    def testExceptionWhereItsAllRight(self):
        cell = Parse(tag="td", body="Oops!")
        cell.exception("Clean it up!", bkg="right")
        assert cell.tagIsRight()

    def testNodeList(self):
        table = Parse("<table><tr><td>LightFixture</td></tr>"
                      "<tr><td>bulb</td><td>socket</td><td>switch</td></tr>"
                      "</table>")
        result = table.toNodeList()
        assert result.count("\n") == 6




class FitNesseSpecificTests(TestCase):
    def setUp(self):
        print '%s %s' % (self.id(), self.shortDescription())
        self.saveEnv = FitGlobal.Environment
        FitGlobal.Environment = "FitNesse"

    def tearDown(self):
        FitGlobal.Environment = self.saveEnv

    def specifyFitNesseTextRoutine(self):
        cell = Parse(tag="td", body="Hi <br /> There!")
        text = cell.text()
        assert text == "Hi  There!"

    def specifyFitNesseTextWithUnclosedTag(self):
        cell = Parse(tag="td", body="Hi <br / There!")
        text = cell.text()
        assert text == "Hi <br / There!"

if __name__ == '__main__':
    main(defaultTest='makeParseTest')
