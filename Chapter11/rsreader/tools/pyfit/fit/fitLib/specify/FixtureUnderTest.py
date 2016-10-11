# FixtureUnderTest From FitLibrary
#legalStuff rm03 jr05
# Original version Contains code developed by Rick Mugridge.
# University of Auckland, NZ. Copyright 2003 Rick Mugridge.
# Released under the terms of the General Public License (GPL), Release 2.1 or later
# See license.txt for terms and disclaimer of all warrenties and liability.
# changes Copyright 2005 John H. Roth Jr.
# Last updated for Release 0.8a1
#endLegalStuff

from fit.Fixture import Fixture
from fit.Parse import Parse
import traceback, sys

class FixtureUnderTest(Fixture):
    row = None

    # test method - what's going wrong?
    def doTable(self, table):
        print "in doTable. table: '%s'" % table
        Fixture.doTable(self, table)
        
    def doRow(self, row):
        self.row = row
        Fixture.doRow(self, row)

    def doCells(self, cells):
        __pychecker__ = "maxrefs=10"
        try:
            name = cells.text()
            if name == "r": 
                self.right(cells) 
            elif name == ("w"): 
                self.wrong(cells) 
            elif name == ("i"): 
                self.ignore(cells) 
            elif name == ("e"): 
                # fake exception processing...
                self._fakeRuntimeException(cells)
#                cells.addToBody(self.cssDataClass.fit_stacktrace % "Fake stack trace")
#                cells.addToTag(self.cssDataClass.fit_error)
#                self.counts.exceptions += 1
##                self.exception(cells, new RuntimeException("test")) 
            elif name == ("-"):
                pass 
            elif name == ("rw"): 
                self.right(cells) 
                self.wrong(cells.more) 
            elif name == ("ri"): 
                self.right(cells) 
                self.ignore(cells.more) 
            elif name == ("iw"): 
                self.ignore(cells) 
                self.wrong(cells.more) 
            elif name == ("rwrwiwiee-"): 
                #... 
                self.right(cells)
                self.wrong(cells.more)
                self.right(cells.more.more)
                self.wrong(cells.more.more.more)
                self.ignore(cells.more.more.more.more)
                self.wrong(cells.more.more.more.more.more)
                self.ignore(cells.more.more.more.more.more.more)
                self._fakeRuntimeException(
                    cells.more.more.more.more.more.more.more)
                self._fakeRuntimeException(
                    cells.more.more.more.more.more.more.more.more)
            elif name == ("reports"): 
                cells.more.addToBody("reported") 
            elif name == ("wMsg"): 
                self.wrong(cells,"Message") 
            elif name == ("insertTwoRows"): 
                self.addRows() 
            else: 
                raise Exception("Action not known: " + name) 
        except Exception, ex: 
            print "in FixtureUnderTest exception handler"
            traceback.print_exc(None, sys.stdout)
            self.exception(cells, ex)

    def _fakeRuntimeException(self, cell):
        # FIXME there's no reason to _fake_ a runtime exception
        cell.error("Fake stack Trace")
        self.counts.exceptions += 1

    def addRows(self): 
        nextRow = self.row.more 
        self.row.more = Parse(tag="tr", body="", parts=self.newRows(), 
            more=Parse(tag="tr", body="", parts=self.newRows(), more=nextRow)) 

    def newRows(self): 
        result = Parse(tag="td", body="one", more=Parse(
            tag="td", body="two")) 
        self.right(result) 
        self.wrong(result.more) 
        return result 
