# Tests for ParseUtility
# Developed by Rick Mugridge
# Copyright 2004, 2005 Rick Mugridge, University of Auckland, NZ
# Released under the terms of the GNU General Public License version 2 or later.
# Python Translation copyright 2005 John H. Roth Jr.

import unittest
from fit.Parse import Parse
import fitLib.ParseUtility
ParseUtility = fitLib.ParseUtility

try:
    False
except:
    True = 1
    False = 0

def makeParseUtilityTest():
    theSuite = unittest.makeSuite(Test_ParseUtility, 'test')
#    theSuite.addTest(unittest.makeSuite(Test_FooBar, 'Test'))
    return theSuite

class Test_ParseUtility(unittest.TestCase):

    html = ("<html><title>table</title><body>"
    	"t1<table><tr><td>Test</td></tr></table>t2"
    	"t3<table><tr><td>Test</td></tr></table>t4"
    	"</body></html>")
    setUpHtml = ("<html><title>setup</title><body>"
    	"s1<table><tr><td>SetUp</td></tr></table>s2"
    	"s3<table><tr><td>SetUp</td></tr></table>s4"
    	"</body></html>")
    tearDownHtml = ("<html><title>teardown</title><body>"
    	"front<table><tr><td>TearDown</td></tr></table>back"
    	"T3<table><tr><td>TearDown</td></tr></table>T4"
    	"</body></html>")

    def setUp(self):
        print '%s %s' % (self.id(), self.shortDescription())
        self._tables = Parse(self.html)
        self._setUp = Parse(self.setUpHtml)
        self._tearDown = Parse(self.tearDownHtml)

    def testAppend(self):
        expected = ("<html><title>setup</title><body>"
            "s1<table><tr><td>SetUp</td></tr></table>s2"
            "s3<table><tr><td>SetUp</td></tr></table>s4"
            "<br>front<table><tr><td>TearDown</td></tr></table>back"
            "T3<table><tr><td>TearDown</td></tr></table>T4"
            "</body></html>")
        ParseUtility.append(self._setUp, self._tearDown)
        self._assertEquals(expected, self._setUp)

    def testAppendNone(self):
        ParseUtility.append(self._setUp, None)
        self._assertEquals(self.setUpHtml, self._setUp)

    def testAppendSetUp(self):
        expected = ("<html><title>table</title><body>"
            "s1<table><tr><td>SetUp</td></tr></table>s2"
            "s3<table><tr><td>SetUp</td></tr></table>"
            "s4<br>t1<table><tr><td>Test</td></tr></table>t2"
            "t3<table><tr><td>Test</td></tr></table>t4"
            "</body></html>")
        ParseUtility.appendToSetUp(self._setUp, self._tables)
        self._assertEquals(expected, self._setUp)

    def testAppendSetUpWithNull(self):
        ParseUtility.appendToSetUp(self._setUp, None)
        self._assertEquals(self.setUpHtml, self._setUp)

    def testAppendAll(self):
        expected = ("<html><title>table</title><body>"
            "s1<table><tr><td>SetUp</td></tr></table>s2"
            "s3<table><tr><td>SetUp</td></tr></table>"
            "s4<br>t1<table><tr><td>Test</td></tr></table>t2"
            "t3<table><tr><td>Test</td></tr></table>"
            "t4<br>front<table><tr><td>TearDown</td></tr></table>back"
            "T3<table><tr><td>TearDown</td></tr></table>T4"
            "</body></html>")
        ParseUtility.append(self._tables, self._tearDown)
        ParseUtility.appendToSetUp(self._setUp, self._tables)
        self._assertEquals(expected, self._setUp)

    
    def _assertEquals(self, expected, tables2):
        self.assertEquals(expected, ParseUtility.toString(tables2))

    def testFixHeader(self):
        result = ParseUtility.removeHeader(self._tables)
        self.assertEquals("<html><title>table</title><body>", result)
        self._assertEquals("t1<table><tr><td>Test</td></tr></table>t2"
                "t3<table><tr><td>Test</td></tr></table>t4"
                "</body></html>", self._tables)

    def testInitialTable(self):
        self._assertEquals("<html><title>table</title><body>"
                "t1<table><tr><td>Test</td></tr></table>t2"
                "t3<table><tr><td>Test</td></tr></table>t4"
                "</body></html>", self._tables)

    def testChangeHeader(self):
        ParseUtility.changeHeader(self._tables,"<html><title>new</title><body><hr>")
        self._assertEquals("<html><title>new</title><body><hr>"
                "t1<table><tr><td>Test</td></tr></table>t2"
                "t3<table><tr><td>Test</td></tr></table>t4"
                "</body></html>", self._tables)

    def testCompleteTrailerThatIsComplete(self):
        ParseUtility.completeTrailer(self._tables)
        self._assertEquals("<html><title>table</title><body>"
                "t1<table><tr><td>Test</td></tr></table>t2"
                "t3<table><tr><td>Test</td></tr></table>t4"
                "</body></html>",self._tables)

    def testCompleteTrailerThatIsInComplete(self):
        self._tables.last().trailer = "JUNK"
        ParseUtility.completeTrailer(self._tables)
        self._assertEquals("<html><title>table</title><body>"
            "t1<table><tr><td>Test</td></tr></table>t2"
            "t3<table><tr><td>Test</td></tr></table>JUNK"
            "\n</body></html>\n",self._tables)

    def testFixTrailersNone(self):
        setUpHtml = ("<html><title>setup</title><body>"
            "<table><tr><td>SetUp</td></tr></table>"
            "</body></html>")
        setUp2 = Parse(setUpHtml)
        ParseUtility.fixTrailers(setUp2, self._tables)
        self._assertEquals("<html><title>setup</title><body>"
        		"<table><tr><td>SetUp</td></tr></table>",
        		setUp2)
        self._assertEquals("<html><title>table</title><body>"
                "t1<table><tr><td>Test</td></tr></table>t2"
                "t3<table><tr><td>Test</td></tr></table>t4"
                "</body></html>",
                self._tables)

    def testFixTrailers(self):
        ParseUtility.removeHeader(self._tables)
        ParseUtility.fixTrailers(self._setUp, self._tables)
        self._assertEquals("<html><title>setup</title><body>"
            "s1<table><tr><td>SetUp</td></tr></table>s2"
            "s3<table><tr><td>SetUp</td></tr></table>",
            self._setUp)
        self._assertEquals(
            "s4<br>t1<table><tr><td>Test</td></tr></table>t2"
            "t3<table><tr><td>Test</td></tr></table>t4"
            "</body></html>",
            self._tables)
        
# New tests because five of the original methods weren't tested. JHR

    def testCopyParse(self):
        newTree = ParseUtility.copyParse(self._tables)
        self._assertEquals(self.html, newTree)

    def testCopyParseNone(self):
        newTree = ParseUtility.copyParse(None)
        self.assertEquals(newTree, None)
        
        
        

    def tearDown(self):
        pass

if __name__ == '__main__':
    unittest.main(defaultTest='makeParseUtilityTest')

