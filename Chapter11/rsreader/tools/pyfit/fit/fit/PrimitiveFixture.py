"""
Python translation of fit..
which is copyright (c) 2002 Cunningham & Cunningham, Inc.
Released under the terms of the GNU General Public License version 2 or later.
Translation to Python copyright 2003 Simon Michael
Changes copyright 2003, 2004, John H. Roth Jr.
"""

# import string, re
from fit.Parse import Parse
from fit.Fixture import Fixture

class PrimitiveFixture(Fixture):

    ## format converters ########################

    def parseLong(self,cell):
        return long(cell.text())

    ## answer comparisons ######################

    def check(self, cell, value):
        if cell.body == repr(value):
            self.right(cell)
        else:
            self.wrong(cell, value)

#    def check (Parse cell, long value) {
#        if (parseLong(cell) == value) {
#			right(cell)
#		 else {
#            wrong(cell, Long.toString(value))
#
#    def check (Parse cell, double value) {
#        if (Double.parseDouble(cell.body) == value) {
#			right(cell)
#		 else {
#            wrong(cell, Double.toString(value))
        
    


