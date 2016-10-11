"""
Test fixture for table parameters.
Copyright 2004, John H. Roth Jr.
Released under the terms of the GNU General Public License version 2 or later.
"""

from fit.Fixture import Fixture

class ParmTest(Fixture):

##    def doRows(self, rows):
##        Fixture.doRows(self, rows)

    def doCell(self, cell, column):
        if column == 0: return
        if column <= len(self.getArgs()):
            if cell.text() == self.getArgs()[column - 1]:
                self.right(cell)
            else:
                self.wrong(cell, self.getArgs()[column - 1])
        else:
            self.ignore(cell)


        
