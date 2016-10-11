# FixtureFixture from FitLibrary
#legalStuff rm05 jr05
# Original version Contains code developed by Rick Mugridge.
# University of Auckland, NZ. Copyright 2005 Rick Mugridge.
# Released under the terms of the General Public License (GPL), Release 2.1 or later
# See license.txt for terms and disclaimer of all warrenties and liability.
# changes Copyright 2005 John H. Roth Jr.
# Last updated for Release 0.8a1
#endLegalStuff
# !!! Depreciated !!! in favor of SpecifyFixture

# A fixture for testing fixtures. Checks that the markings for each cell in a row are correct.
# Checks that expected row insertions have occurred correctly and that no other insertions have occurred.

import time
from fit.Fixture import Fixture, Counts, RunTime
from fit.Parse import Parse
from fitLib.FitLibraryExceptions import FitFailureException, \
     IgnoredException

try:
    False
except:
    True = 1
    False = 0

REPORT = "report"
INSERT_ROW = "I"


class FixtureFixture(Fixture):
    # Static
    embeddedCounts = Counts() # ???
    embeddedSummary = {
        "run date": time.ctime(time.time()),
        "run elapsed time": RunTime(),
        }
    # default instance variables
    embeddedRow = None
    embeddedTable = None

    def doTable(self, table):
        try:
            Fixture.doTable(self, table)
        except FitFailureException, ex:
            self.failure(table.at(0, 0, 0), ex.getMessage())
        except IgnoredException:
            pass
        except Exception, ex:
            self.exception(table.at(0,0,0), ex)

    def doRows(self, givenRows):
        rows = givenRows
        self.embeddedRow = self.getFirstEmbeddedRow(rows.parts)
        self.embeddedTable = Parse(tag="table", body="", parts=self.embeddedRow)
        rows = rows.more
        while rows is not None:
            self.doCells(rows.parts)
            rows = rows.more

        self.doEmbeddedTable(self.embeddedTable)
        if self.splicedInAddedRows(givenRows, self.embeddedTable.parts):
            self.checkMarkings(givenRows)
        else:
            self.showActualRowsAtBottom(givenRows, self.embeddedTable.parts)

    def showActualRowsAtBottom(self, givenRows, embeddedRows):
        rows = givenRows
        while rows.more is not None:
            rows = rows.more
        rows.more = Parse(tag="tr", body=None,
                          parts=Parse(tag="td", body="Actual Rows:"))
        rows = rows.more
        self.wrong(rows.parts)
        while embeddedRows is not None:
            rows.more = Parse(tag="tr", body=None,
                              parts=Parse(tag="td", body="",
                                          more=embeddedRows.parts))
            rows = rows.more
            embeddedRows = embeddedRows.more

    def splicedInAddedRows(self, outerRows, embeddedRows):
        while (outerRows is not None and embeddedRows is not None):
            if outerRows.parts.text().startswith(INSERT_ROW):
                if (outerRows.parts.more is not None and not
                    self.validRowValues(outerRows.parts.more,
                                        embeddedRows.parts)):
                    return False
                outerRows.parts.more = embeddedRows.parts
                embeddedRows = embeddedRows.more

            elif outerRows.parts.text() == REPORT:
                pass # Do nothing; it will be picked up on the next pass
            elif outerRows.parts.more is None:
                return False
            elif outerRows.parts.more == embeddedRows.parts: # They match, so OK
                embeddedRows = embeddedRows.more
            else: # Don't match, so wrong
                return False
            outerRows = outerRows.more

        while outerRows is not None and outerRows.parts.text() == REPORT:
            outerRows = outerRows.more
        if outerRows is not None or embeddedRows is not None:
            return False
        return True

    def validRowValues(self, expected, actual):
        while expected is not None and actual is not None:
            if expected.text() != "" and expected.text() != actual.text():
                return False
            expected = expected.more
            actual = actual.more

        return expected is None and actual is None

    def getFirstEmbeddedRow(self, cells):
        if cells is None:
            raise FitFailureException, "Embedded fixture is missing"
        if cells.text() == "fixture" and cells.more is not None:
            return Parse(tag="tr", body="", parts=cells.more)
        else:
            self.failure(cells, "Embedded fixture is missing")
            raise IgnoredException()

    def doCells(self, cells):
        if (cells.text() == REPORT or cells.more is None or
            cells.text().startswith(INSERT_ROW)):
            return
        newRow = Parse(tag="tr", body="", parts=cells.more)
        self.embeddedRow.more = newRow
        self.embeddedRow = newRow

    def doEmbeddedTable(self, tables):
        heading = tables.at(0, 0, 0)
        if heading is not None:
            try:
                fixture = self.loadFixture(heading.text())()
#            except ClassNotFoundException, ex:
#                self.failure(heading, ": Unknown Class");
            except Exception, e:
                self.exception(heading, e)
                return
            try:
                self.runFixture(tables, fixture)
            except Exception, e:
                self.exception(heading, e)

    def runFixture(self, tables, fixture):
        self.injectDependenciesIntoFixture(fixture, tables)
        fixture.counts = self.embeddedCounts
        fixture.summary = self.embeddedSummary
        fixture.doTable(tables)

    def failure(self, cell, message):
        self.wrong(cell)
        cell.addToBody(self.label(message))

    def checkMarkings(self, rows):
        self.checkRowMarkings(rows.more)

    def checkRowMarkings(self, rows):
        __pychecker__ = 'no-objattrs' # previousRow starts off None...
        previousRow = None
        while rows is not None:
            cells = rows.parts
            if cells.text() == INSERT_ROW:
                pass
            elif cells.text() == REPORT and previousRow is not None:
                if self.validReportValuesMarked(cells.more,
                                                previousRow.parts.more):
                    self.right(cells)
                else:
                    self.wrong(cells)
            else:
                result = self.cellMarkings(cells.more)
                if self.markingsEqual(self._removeInsertRowMarker(cells.text()), result):
                    self.right(cells)
                else:
                    self.wrong(cells, result)

            previousRow = rows
            rows = rows.more

    def _removeInsertRowMarker(self, text):
        if text.startswith(INSERT_ROW):
            return text[1:]
        return text

    def validReportValuesMarked(self, expected, actual):
        result = True
        while expected is not None and actual is not None:
            if expected.text() != "":
                if expected.text() == actual.text():
                    self.right(expected)
                else:
                    self.wrong(expected, actual.text())
                    result = False

            expected = expected.more
            actual = actual.more
        return result

    def cellMarkings(self, cells):
        result = ""
        while cells is not None:
            result += self._extractColorCode(cells)
            cells = cells.more
        return result

    def markingsEqual(self, expected, actual):
        if expected == actual:
            return True
        trimmedActual = actual
        while trimmedActual.endswith("-"):
            trimmedActual = trimmedActual[:-1] # ??? s/b -2 ???
            if expected == trimmedActual:
                return True
        return False

# replacement for Coloring test
# important! This assumes that the class tag was inserted by PyFit Fixture
    def _extractColorCode(self, cell):
        tag = cell.tag
        classStart = tag.find('class="')
        if classStart < 0:
            return "-"
        classStart += 7 # past the quote
        classEnd = tag.find('"', classStart)
        if classEnd < classStart:
            return "-" # s/b error for malformed tag
        colorName = tag[classStart:  classEnd]
        return self.colorMap.get(colorName, "-")

    colorMap = {
        "pass": "r",
        "fit_pass": "r",
        "fail": "w",
        "fit_fail": "w",
        "ignore": "i",
        "fit_ignore": "i",
        "fit_grey": "i",
        "error": "e",
        "fit_error": "e",
        "fit_stacktrace": "e",
        }
        
