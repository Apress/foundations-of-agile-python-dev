#Grid Fixture from Fit Library
# Developed by Rick Mugridge
# Copyright 2005 Rick Mugridge, University of Auckland, NZ
# Released under the Terms of the GNU General Public License, version 2.0 or later
# Python translation copyright 2005 John H. Roth Jr.

# checks the values in a table against the values in a 2 dimensional
# array implementedd as a list of lists.

try:
    False
except:
    False = 0
    True = 1

from fit.Fixture import Fixture
from fit.Parse import Parse
from fit import TypeAdapter

class GridFixture(Fixture):
    _grid = None
    _typeAdapter = None

    def __init__(self, grid=None, typeDict=None):
        if grid is not None:
            self.setGrid(grid)
        if typeDict is not None:
            self.setTypeAdapter(typeDict)

    def setGrid(self, grid):
        self._grid = grid

    def setTypeAdapter(self, typeDict):
        for key in typeDict.keys():
            parts = key.split(".")
            break
        self._typeAdapter = TypeAdapter.on(self, parts[0], typeDict)

    def doTable(self, table):
        if not len(self._grid) and table.parts.more is None:
            self.right(table.parts)
        elif not self._rowsMatch(self._grid, table.parts):
            self._addActualRows(table.parts, self._grid)

    def _rowsMatch(self, aList, aRow):
        matched = True
        for i in range(len(aList)):
            if aRow.more is None:
                matched = False
                break
            aRow = aRow.more
            if not self._cellsMatch(aList[i], aRow.parts):
                matched = False
        return self._markWrong(aRow.more, matched)

    def _cellsMatch(self, aList, allCells):
        cells = allCells
        matched = True
        for i in range(len(aList)):
            if not self._cellMatches(aList[i], cells):
                matched = False
            if cells.more is None and i < len(aList) - 1:
                matched = False
                break
            cells = cells.more
        return self._markWrong(cells, matched)

    def _cellMatches(self, actual, cell):
        if cell.parts is not None or not cell.body:
            return False
        matches = False
        try:
            matches = self._typeAdapter.equals(cell, actual)
            if matches:
                self.right(cell)
            else:
                self.wrong(cell, self._typeAdapter.toString(actual))
        except Exception, e:
            self.exception(cell, e)
        return matches

##    /** Add extra cells to expected, if necessary.

    def _markWrong(self, cells, matched):
        while cells:
            matched = False
            self.wrong(cells)
            cells = cells.more
        return matched;
    
    def _addActualRows(self, rows, actual):
        cols = 0
        lastRow = rows
        while rows:
            lastRow = rows
            cols = max(cols, lastRow.size())
            rows = rows.more
        for i in range(len(actual)):
            cols = max(cols, len(actual[i]))
        lastRow.more = Parse(tag="tr", parts=Parse(
                    tag="td colspan=%s" % cols, body="<i>Actuals:</i>"))
        lastRow = lastRow.more
        for i in range(len(actual)):
            lastRow.more = self._makeRowWithTr(actual[i])
            lastRow = lastRow.more

    def _makeRowWithTr(self, actuals):
        return Parse(tag="tr", parts=self._makeCellsWithTd(actuals))

    def _makeCellsWithTd(self, actuals):
        if not len(actuals):
            aCell = Parse(tag="tr")
            self.exception(aCell, "Actuals Row Empty")
            return aCell
        rows = Parse(tag="td")
        row = rows
        for i in range(len(actuals)):
            row.more = self._makeCell(actuals[i])
            row = row.more
        return rows.more

    def _makeCell(self, anObject):
        aCell = Parse(tag="td")
        try:
            aCell.body = self._typeAdapter.toString(anObject, aCell)
        except Exception, e:
            self.exception(aCell, e)
        return aCell 
        

