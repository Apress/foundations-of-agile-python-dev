# Table Parse Fixture from Fit 1.1 specification tests
# Copyright 2005 Jim Shore
# Released under the terms of the GNU General Public License, version 2.0 or later
# Translation to Python copyright 2005 John H. Roth Jr.

from fit.ColumnFixture import ColumnFixture
from fit.Parse import Parse

class TableParseFixture(ColumnFixture):
    _typeDict = {"HTML": "String",
                "Row": "Integer",
                "Column": "Integer",
                "CellBody": "String",
                "CellTag": "String",
                "RowTag": "String",
                "TableTag": "String"
                }
    
    HTML = ""
    Row = 0
    Column = 0
    
    def CellBody(self):
        return self._cell().body
    
    def CellTag(self):
        return self._cell().tag
    
    def RowTag(self):
        return self._row().tag
    
    def TableTag(self):
        return self._table().tag
        
    def _table(self):
        return Parse(self.HTML)
    
    def _row(self):
        return self._table().at(0, self.Row - 1)
    
    def _cell(self):
        return self._row().at(0, self.Column - 1)
