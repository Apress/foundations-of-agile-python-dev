# FixtureNameFixture from Fit 1.1 Specification Tests
# Copyright 2005 Jim Shore
# Released under the terms of the GNU General Public License, version 2.0 or above
# Python translation copyright 2005 John H. Roth Jr.

import re
from fit.ColumnFixture import ColumnFixture
from fit.Parse import Parse

class FixtureNameFixture(ColumnFixture):
    _typeDict = {"Table": "String",
                 "FixtureName": "String",
                 }
    Table = ""
    
    def FixtureName(self):
        tableParse = self._GenerateTableParse(self.Table)
        result = self.fixtureName(tableParse).text() # seems to be a new Fixture method
        if result == "":
            return "(missing)"
        return result
    
    def _GenerateTableParse(self, table):
        rows = table.split("\n")
        return Parse(tag="table", parts=self._GenerateRowParses(rows, 0))

    def _GenerateRowParses(self, rows, rowIndex):
        if rowIndex >= len(rows):
            return None
        
        cells = re.split(r"\]\s*\[", rows[rowIndex])
        if len(cells) != 0:
            cells[0] = cells[0][1:]
            cells[-1] = cells[-1][:-1]
        
        return Parse(tag="tr", parts=self._GenerateCellParses(cells, 0),
                     more=self._GenerateRowParses(rows, rowIndex+1))

    def _GenerateCellParses(self, cells, cellIndex):
        if cellIndex >= len(cells):
            return None
        
        return Parse(tag="td", body=cells[cellIndex],
                     more=self._GenerateCellParses(cells, cellIndex + 1))




