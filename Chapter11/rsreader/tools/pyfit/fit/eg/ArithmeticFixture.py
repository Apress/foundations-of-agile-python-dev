"""
Python translation of fit..
which is copyright (c) 2002 Cunningham & Cunningham, Inc.
Released under the terms of the GNU General Public License version 2 or later.
"""

from fit.PrimitiveFixture import PrimitiveFixture

class ArithmeticFixture(PrimitiveFixture):
    x=0L
    y=0L

    def doRows(self,rows):
        # skip column heads
        PrimitiveFixture.doRows(self,rows.more)

    def doCell(self, cell, column):
        if   column == 0: self.x = int(self.parseLong(cell))
        elif column == 1: self.y = int(self.parseLong(cell))
        elif column == 2: self.check(cell, self.x+self.y)
        elif column == 3: self.check(cell, self.x-self.y)
        elif column == 4: self.check(cell, self.x*self.y)
        elif column == 5: self.check(cell, self.x/self.y)
        elif column == 6: pass
        else: self.ignore(cell)

    def check(self, cell, value):
        strValue = str(value)
        if cell.body == strValue:
            self.right(cell)
        else:
            self.wrong(cell, strValue)

        
