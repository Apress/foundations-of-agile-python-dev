# DocumentParseFixture from Fit1.1 Specification Tests
# Copyright 2005 Jim Shore
# Released under the terms of the GNU General Public License, version 2.0 or higher
# Translation to Python copyright 2005 John H. Roth Jr.

from fit.ColumnFixture import ColumnFixture
from fit.Parse import Parse


class DocumentParseFixture(ColumnFixture):
    _typeDict = {"HTML": "String",
                 "Note": "String",
                 "Output": "String",
                 "Structure": "String"
                 }

    HTML = ""
    Note = "" # not functional
    
    def Output(self):
        return self._GenerateOutput(Parse(self.HTML))

    def Structure(self):
        return self._dumpTables(Parse(self.HTML))
    
    def _GenerateOutput(self, parse):
        return parse.toString()
        
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
            result += "[" + cell.body + "]"
            separator = " "
            cell = cell.more
        return result
