# FlowFixtureFixture from FitLibrary
# Developed by Rick Mugridge
# Copyright 2004 Rick Mugridge, University of Auckland, NZ
# Released under the terms of the GNU General Public License version 2 or later.
# Translation to Python copyright 2005 John H. Roth Jr.

# A fixture for testing fixtures in flow style.
# It is in flow style itself because it overrides the method interpretTables(),
# which is called in the revised fit.Fixture.

# Warning - Depreciated in favor of SpecifyFixture.

from fit.Counts import Counts
from fit.Fixture import Fixture, NullFixtureListener
from fit.Parse import Parse
from fitLib.FixtureFixture import FixtureFixture

class FlowFixtureFixture(FixtureFixture):
    def interpretTables(self, tables):
        embeddedTables = self.makeEmbeddedTables(tables)
        fixture = Fixture()
        self.injectDependenciesIntoFixture(fixture, tables)
        fixture.counts = Counts()
#        fixture.counts = self.embeddedCounts
        fixture.summary = self.embeddedSummary
        fixture.listener = NullFixtureListener()
        fixture.doTables(embeddedTables)
        self.checkMarkingsOfTables(tables, embeddedTables)
        self.signalTables(tables)

    def checkMarkingsOfTables(self, tables, embeddedTables):
        self.checkRowMarkings(tables.parts.more)
        tables = tables.more
        embeddedTables = embeddedTables.more
        while tables is not None:
            self.checkMarkingOfRows(tables.parts, embeddedTables.parts)
            tables = tables.more
            embeddedTables = embeddedTables.more

    def checkMarkingOfRows(self, outerRows, innerRows):
        if self.splicedInAddedRows(outerRows, innerRows):
            self.checkRowMarkings(outerRows)
        else:
            self.showActualRowsAtBottom(outerRows, innerRows)

    def makeEmbeddedTables(self, tables):
        allEmbeddedTables = Parse(tag="table", body="")
        embeddedTables = allEmbeddedTables
        rowsAfterFirst = tables.parts.more
        if rowsAfterFirst is not None:
            # Handle rest of first table as a separate table:
            embeddedTables = self.addTable(embeddedTables, rowsAfterFirst)
        tables = tables.more
        while tables is not None:
            embeddedTables = self.addTable(embeddedTables, tables.parts)
            tables = tables.more
        return allEmbeddedTables.more

    def addTable(self, embeddedTables, rows):
        embeddedTables.more = self.makeEmbeddedRows(rows)
        return embeddedTables.more

    def makeEmbeddedRows(self, rows):
        allEmbeddedRows = Parse(tag="tr")
        embeddedRow = allEmbeddedRows
        while rows is not None:
            cells = rows.parts
            if (not cells.text() == "report" and cells.more is not None and
                not cells.text().startswith("I")):
                embeddedRow.more = Parse(tag="tr", parts=cells.more) #drop first column
                embeddedRow = embeddedRow.more
            rows = rows.more
        return Parse(tag="table", parts=allEmbeddedRows.more)

    def signalTables(self, tables):
        while tables is not None:
            self.listener.tableFinished(tables)
            tables = tables.more
        self.listener.tablesFinished(self.counts)
