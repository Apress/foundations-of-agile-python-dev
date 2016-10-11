# Table specification test fixture for Fit Library Specification Tests
# Developed by Rick Mugridge
# Copyright 2005 Rick Mugridge, University of Auckland, NZ
# Released under the terms of the GNU General Public License, versiion 2 or later
# Translation to Python copyright 2005, John H. Roth Jr.

from fitLib.DoFixture import DoFixture
from fitLib.Table import Table, TableTypeAdapter
#from fit.Parse import Parse

class DoTable(DoFixture):
    _typeDict = {}

    _typeDict["firstCellStringValue.types"] = ["String", TableTypeAdapter]    
    def firstCellStringValue(self, table):
        return table.stringAt(0,0,0)

    _typeDict["firstCellValue.types"] = [TableTypeAdapter, TableTypeAdapter]
    def firstCellValue(self, table):
        return table.tableAt(0,0,0)

    _typeDict["aTable.types"] = [TableTypeAdapter]
    def aTable(self):
        return Table("<html><table><tr><td>one</td><td>two</td><td>three</td></tr></table></html>")

    _typeDict["nullTable.types"] = [TableTypeAdapter]
    def nullTable(self):
        return None
