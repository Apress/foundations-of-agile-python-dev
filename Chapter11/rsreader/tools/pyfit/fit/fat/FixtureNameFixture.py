# FixtureNameFixture from FIT Acceptance Tests
# copyright 2004 Jim Shore
# copyright released under the GNU General Public license, version 2.0 or later.
# Translation to Python copyright 2005 John H. Roth Jr.

import re
from fit.ColumnFixture import ColumnFixture
from fit.Fixture import Fixture
from fit.Parse import Parse

class FixtureNameFixture(ColumnFixture):
    _typeDict = {"Table": "String",
                 }
    Table = ""

    _typeDict["FixtureName"] = "String"    
    def FixtureName(self):
        tableParse = self._GenerateTableParse(self.Table)
        print ("in FixtureNameFixture.FixtureName. "
               "input:\n'%s'\nresult:\n%s"
               % (self.Table, tableParse.toNodeList()))
#//      Fixture fixture = Fixture.
        
#//      return loadFixture(GenerateTableParse(Table).text()).toString();
#        return self._dumpTables(tableParse)
        return tableParse.parts.parts.text()

    #//***************

    def _dumpTables(self, table):
        result = ""
        separator = ""
        while table is not None:
            result += separator
            result += self._dumpRows(table.parts)
            separator = "\n----\n"
            table = table.more
        return result
    
    def _dumpRows(self, row):
        result = ""
        separator = ""
        while row is not None:
            result += separator
            result += self._dumpCells(row.parts)
            separator = "\n"
            row = row.more
        return result
    
    def _dumpCells(self, cell):
        result = ""
        separator = ""
        while cell is not None:
            result += separator
            result += "[%s]" % cell.text()
            separator = " "
            cell = cell.more
        return result

    #//***************

    _typeDict["ValidFixture"] = "String"
    def ValidFixture(self):
        return "not implemented"

    _typeDict["Error"] = "String"
    def Error(self):
        return "not implemented"
    
    def _GenerateTableParse(self, table):
        rows = table.split("\n")
        return Parse(tag="table", parts=self._GenerateRowParses(rows, 0))

    matcher = re.compile(r"\[(.*?)\]")
    def _GenerateRowParses(self, rows, rowIndex):
        if rowIndex >= len(rows):
            return None
        matchArray = self.matcher.findall(rows[rowIndex]) # is this what I want?
        cells = []
        for match in matchArray:
            cells.append(match)
        return Parse(tag="tr",parts=self._GenerateCellParses(cells, 0),
                         more=self._GenerateRowParses(rows, rowIndex+1))

    def _GenerateCellParses(self, cells, cellIndex):
        if cellIndex >= len(cells):
            return None
        return Parse(tag="td", body=cells[cellIndex],
                     more=self._GenerateCellParses(cells, cellIndex + 1))

