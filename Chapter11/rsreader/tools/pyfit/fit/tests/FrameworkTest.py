"""
Python translation of fit..
which is copyright (c) 2002 Cunningham & Cunningham, Inc.
Released under the terms of the GNU General License version 2 or later.
Python port copyright 2002, Simon Michael
Changes to the Java version, copyright 2004, Robert and Micah Martin
Changes to the Python port copyright 2003, 2004 John H. Roth Jr.
See license.txt for terms and general disclaimer of warrenty and liability
"""

import os, os.path
#import string
import sys
import unittest

from fit.Parse import Parse, ParseException
from fit.Fixture import Fixture
from fit.ColumnFixture import ColumnFixture
from fit.TypeAdapter import adapterOnType, adapterOnField, adapterOnMethod
from fit.ScientificDouble import ScientificDouble

print "current Python path: '%s'" % "\n".join(sys.path)

class FrameworkTest(unittest.TestCase):
    def setUp(self):
        cwd = os.getcwd()
        head, self.tail = os.path.split(cwd)
        os.chdir("..")

    def tearDown(self):
        os.chdir(self.tail)

    def testParsing(self):
        print "----- in testParsing"
        tags = ("table",)
        p = Parse("leader<Table foo=2>body</table>trailer", tags)
        self.assertEquals("leader", p.leader)
        self.assertEquals("<Table foo=2>", p.tag)
        self.assertEquals("body", p.body)
        self.assertEquals("trailer", p.trailer)
    
    def testRecursing(self):
        print "----- in testRecursing"
        p = Parse("leader<table><TR><Td>body</tD></TR></table>trailer")
        self.assertEquals("", p.body) # change 0.7 wrong invariant
        self.assertEquals("", p.parts.body) # change 0.7 wrong invariant
        self.assertEquals("body", p.parts.parts.body)
    
    def testIterating(self):
        p = Parse("leader<table><tr><td>one</td><td>two</td><td>three</td></tr></table>trailer")
        self.assertEquals("one", p.parts.parts.body)
        self.assertEquals("two", p.parts.parts.more.body)
        self.assertEquals("three", p.parts.parts.more.more.body)
    
    def testIndexing(self):
        p = Parse("leader<table><tr><td>one</td><td>two</td><td>three</td></tr><tr><td>four</td></tr></table>trailer")
        self.assertEquals("one", p.at(0,0,0).body)
        self.assertEquals("two", p.at(0,0,1).body)
        self.assertEquals("three", p.at(0,0,2).body)
        self.assertEquals("three", p.at(0,0,3).body)
        self.assertEquals("three", p.at(0,0,4).body)
        self.assertEquals("four", p.at(0,1,0).body)
        self.assertEquals("four", p.at(0,1,1).body)
        self.assertEquals("four", p.at(0,2,0).body)
        self.assertEquals(1, p.size())
        self.assertEquals(2, p.parts.size())
        self.assertEquals(3, p.parts.parts.size())
        self.assertEquals("one", p.leaf().body)
        self.assertEquals("four", p.parts.last().leaf().body)

    def testParseException(self):
        try:
            Parse("leader<table><tr><th>one</th><th>two</th><th>three</th></tr><tr><td>four</td></tr></table>trailer")
        except ParseException, e:
            self.assertEquals(17, e.offset)
            self.assertEquals("Can't find tag: td", e.message)
            return
        self.fail("expected exception not thrown")

    def testText(self):
        tags =("td",)
        print "----- in testText"
        p = Parse("<td>a&lt;b</td>", tags)
        self.assertEquals("a&lt;b", p.body)
        self.assertEquals("a<b", p.text())
        p = Parse("<td>\ta&gt;b&nbsp;&amp;&nbsp;b>c &&&nbsp;</td>", tags)
        self.assertEquals("a>b & b>c &&", p.text())
        p = Parse("<td>\ta&gt;b&nbsp;&amp;&nbsp;b>c &&nbsp;</td>", tags)
        self.assertEquals("a>b & b>c &", p.text())
        p = Parse("<TD><P><FONT FACE=\"Arial\" SIZE=2>GroupTestFixture</FONT></TD>", tags)
        self.assertEquals("GroupTestFixture",p.text())

    def testUnescape(self):
        self.assertEquals("a<b", Parse().unescape("a&lt;b"))
        self.assertEquals("a>b & b>c &&", Parse().unescape("a&gt;b&nbsp;&amp;&nbsp;b>c &&"))
        self.assertEquals("&amp;&amp;", Parse().unescape("&amp;amp;&amp;amp;"))
        self.assertEquals("a>b & b>c &&", Parse().unescape("a&gt;b&nbsp;&amp;&nbsp;b>c &&"))

# removed in Fit 1.0 Java changes
##    def testUnformat(self):
##        self.assertEquals("ab",Parse().unformat("<font size=+1>a</font>b"))
##        self.assertEquals("ab",Parse().unformat("a<font size=+1>b</font>"))
##        self.assertEquals("a<b",Parse().unformat("a<b"))

    def testTypeAdapter(self):
        f = TestFixture()
        a = adapterOnField(f, 'sampleInt')
        a.set(a.parse("123456"))
        self.assertEquals(123456, f.sampleInt)
        self.assertEquals("-234567", str(a.parse("-234567")))
        a = adapterOnMethod(f, "pi")
# we do not currently support creating an adapter from a method declaration
#        a = adapterOnMethod(f, f.__class__.pi)
        self.assert_(abs(3.14159 - a.invoke()) < 0.00001)
        self.assertEquals(3.14159862, a.invoke())
        a = adapterOnField(f, 'sampleString')
        a.set(a.parse("xyzzy"))
        self.assertEquals('xyzzy', f.sampleString)
        a = adapterOnField(f, 'sampleFloat')
        a.set(a.parse("6.02e23"))
        # not sure what the 1e17 is supposed to be here. If it's the epsilon,
        #  the Python version of xUnit does not support it. We can get a
        #  similar effect by inserting a .precision into _typeDict.
        self.assertEquals(6.02e23, f.sampleFloat) #, 1e17
        # the remaining tests in the September 2002 version were commented
        #  out because the type adapter strategy didn't support lists. The
        #  current strategy does.

    def testTypeAdapter2(self):
        # only the phrases that aren't included in the first test
        f = TestFixture()
        a = adapterOnField(f, "sampleInteger")
        a.set(a.parse("54321"))
        self.assertEquals("54321", str(f.sampleInteger))

# This phrase will never work on Python, since Python does not have a
#  single character type.
##        a = adapterOnField(f, "ch")
##        a.set(a.parse("abc"))
##        self.assertEquals('a', f.ch)
        
        a = adapterOnField(f, "name")
        a.set(a.parse("xyzzy"))
        self.assertEquals("xyzzy", f.name)
        
        a = adapterOnField(f, "sampleFloat")
        a.set(a.parse("6.02e23"))
        self.assertEquals(6.02e23, f.sampleFloat, 1e17);
                          
        a = adapterOnField(f, "sampleArray")
        a.set(a.parse("1,2,3"))
        self.assertEquals(1, f.sampleArray[0])
        self.assertEquals(2, f.sampleArray[1])
        self.assertEquals(3, f.sampleArray[2])
# following test doesn't work because I'm using the native str() 
#        self.assertEquals("1, 2, 3", a.toString(f.sampleArray))
        self.assertEquals("[1, 2, 3]", a.toString(f.sampleArray))

        self.assertEquals(a.equals([1,2,3], f.sampleArray), 1)

# we do not currently have a generic date adapter.
#        a = TypeAdapterOnField(f, "sampleDate")
#        date = Date(49,4,26)
#        a.set(a.parse(DateFormat.getDateInstance().format(date)))
#        self.assertEquals(date, f.sampleDate)
                          
        a = adapterOnField(f, "sampleByte")
        a.set(a.parse("123"))
        self.assertEquals(123, f.sampleByte)
        a = adapterOnField(f, "sampleShort")
        a.set(a.parse("12345"))
        self.assertEquals(12345, f.sampleShort)

    def assertBooleanTypeAdapterParses(self, f, booleanString, assertedValue):
        booleanAdapter = adapterOnField(f, "sampleBoolean")
        result = booleanAdapter.parse(booleanString)
        assert result == assertedValue

    def testBooleanTypeAdapter(self):
        f = TestFixture()
        self.assertBooleanTypeAdapterParses(f, "true", True)
        self.assertBooleanTypeAdapterParses(f, "yes", True)
        self.assertBooleanTypeAdapterParses(f, "y", True)
        self.assertBooleanTypeAdapterParses(f, "+", True)
        self.assertBooleanTypeAdapterParses(f, "1", True)
        self.assertBooleanTypeAdapterParses(f, "True", True)
        self.assertBooleanTypeAdapterParses(f, "YES", True)
        self.assertBooleanTypeAdapterParses(f, "Y", True)

        self.assertBooleanTypeAdapterParses(f, "N", False)
        self.assertBooleanTypeAdapterParses(f, "No", False)
        self.assertBooleanTypeAdapterParses(f, "false", False)
        self.assertBooleanTypeAdapterParses(f, "0", False)
        self.assertBooleanTypeAdapterParses(f, "-", False)
# !!! Strong disagreement about the proper definition of "False."
#     I don't believe it's anything that isn't True.
#     That may be logically correct, but it's not good UI design.
#        self.assertBooleanTypeAdapterParses(f, "whatever", False)

##    def testNullAndBlankStrings(self):
##        fixture = TestFixture()
##        assertNull(fixture.parse("null", String.class))
##        assertEquals("", fixture.parse("blank", String.class))
##
##        TypeAdapter adapter = new TypeAdapter()
##        assertEquals("null", adapter.toString((String)null))
##        assertEquals("blank", adapter.toString(""))

    def testScientificDouble(self):
        pi = 3.141592865
        assert ScientificDouble.valueOf("3.14").equals(pi)
        assert ScientificDouble.valueOf("3.142").equals(pi) # original 3.141 wrong!
        assert ScientificDouble.valueOf("3.1416").equals(pi) # original 3.1415 wrong!
        assert ScientificDouble.valueOf("3.14159").equals(pi)
        assert ScientificDouble.valueOf("3.141592865").equals(pi)
        assert ScientificDouble.valueOf("3.140").equals(pi) == 0
        assert ScientificDouble.valueOf("3.144").equals(pi) == 0
        assert ScientificDouble.valueOf("3.1414").equals(pi) == 0
        assert ScientificDouble.valueOf("3.141592863").equals(pi) == 0
        av = 6.02e23
        assert ScientificDouble.valueOf("6.0e23").equals(av)

    def testEscape(self):
        junk = "!@#$%^*()_-+={|[]\\:\";',./?`"
        self.assertEquals(junk, Fixture().escape(junk))
        self.assertEquals("", Fixture().escape(""))
        self.assertEquals("&lt;", Fixture().escape("<"))
        self.assertEquals("&lt;&lt;", Fixture().escape("<<"))
        self.assertEquals("x&lt;", Fixture().escape("x<"))
        self.assertEquals("&amp;", Fixture().escape("&"))
        self.assertEquals("&lt;&amp;&lt;", Fixture().escape("<&<"))
        self.assertEquals("&amp;&lt;&amp;", Fixture().escape("&<&"))
        self.assertEquals("a &lt; b &amp;&amp; c &lt; d", Fixture().escape("a < b && c < d"))

    def testFixtureArguments(self):
        prefix = "<table><tr><td>fit.Fixture</td>"
        suffix = "</tr></table>"
        f = Fixture()

        table = Parse(prefix + "<td>1</td>" + suffix)
        f.getArgsForTable(table)
        args = f.getArgs()
        self.assertEquals(1, len(args))
        self.assertEquals("1", args[0])

        table = Parse(prefix + "" + suffix)
        f.getArgsForTable(table)
        args = f.getArgs()
        self.assertEquals(0, len(args))

        table = Parse(prefix + "<td>1</td><td>2</td>" + suffix)
        f.getArgsForTable(table)
        args = f.getArgs()
        self.assertEquals(2, len(args))
        self.assertEquals("1", args[0])
        self.assertEquals("2", args[1])

##    def testRuns(self):
##        self.runFIT("arithmetic", 40, 8, 0, 1)
###        self.runFIT("arithmetic", 37, 10, 0, 2) # see comments for differences
##        self.runFIT("CalculatorExample", 75, 8, 0, 1)
###        self.runFIT("CalculatorExample", 75, 9, 0, 0) # floating divide by zero
##        self.runFIT("MusicExample", 95, 0, 0, 0)

##    def runFIT(self, file, right, wrong, ignores, exceptions):
##        input = self.read("fat/Documents/"+file+".html")
##        fixture = Fixture()
##        try:
##            fixture.loadFixtureRenamesFromFile("FixtureRenames.txt")
##        except:
##            print "exception trying to load FixtureRenames.txt"
##        if input.find("<wiki>") != -1:
##            tags = ("wiki", "table", "tr", "td")
##        else:
##            tags = ("table", "tr", "td")
##        tables = Parse(input, tags)
##        fixture.doTables(tables)
##        output = open("fat/Reports/"+file+".html", "wt")
##        output.write(str(tables))
##        output.close()
##        self.assertEquals(right, fixture.counts.right, file+" right")
##        self.assertEquals(wrong, fixture.counts.wrong, file+" wrong")
##        self.assertEquals(ignores, fixture.counts.ignores, file+" ignores")
##        self.assertEquals(exceptions, fixture.counts.exceptions, file+" exceptions")

##    def read(self, inputName):
##        fileObj = open(inputName, "rt")
##        chars = fileObj.read()
##        fileObj.close()
##        return chars

class TestFixture(ColumnFixture): ## used in testTypeAdapter
     _typeDict = {"sampleByte": "Int",
                  "sampleShort": "Int", 
                  "sampleInt": "Int",
                  "sampleInteger": "Int",
                  "sampleFloat": "Float",
                  "sampleBoolean": "Boolean",
                  "pi": "Float",
                  "ch": "String",
                  "name": "String",
                  "sampleArray": "List",
                  "sampleArray.scalarType": "Int",
                  "sampleString": "String",
                  "sampleList": "List",
                  "sampleList.scalarType": "Int",
                  "sampleDate": "String",
                 }
     sampleByte = 0
     sampleShort = 0
     sampleInt = 0
     sampleInteger = 0
     sampleFloat = 0.0
     sampleBoolean = 0
     def pi(self): return 3.14159862
     ch = ""
     name = ""
     sampleArray = []
     sampleString = ''
     sampleList = []
     sampleDate = ''

def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(FrameworkTest))
    return suite

def main():
    unittest.TextTestRunner().run(test_suite())

if __name__ == '__main__':
    main()
