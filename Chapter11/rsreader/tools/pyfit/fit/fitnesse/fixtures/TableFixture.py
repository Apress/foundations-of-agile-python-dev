# Table Fixture from FitNesse
#LegalStuff om02-05 jr05
# Original Java version copyright 2002-2005 by Object Mentor, Inc.
# Released under the terms of the General Public License (GPL), Release 2.1 or later
# See license.txt for terms and disclaimer of all warrenties and liability.
# changes Copyright 2005 John H. Roth Jr.
# Last updated for Release 0.8a1
#endLegalStuff

# This provides services for tables that break the fetters of the
# strict row and column orientation of the standard fixtures, or the
# command orientation of DoFixture and ActionFixture.

# This is the Bureaucracy Fixture - it lets you put in forms the way
# every business on the planet expects to see them, and process them
# they way you're used to.

from fit.Fixture import Fixture
from fit.FitException import FitException

class TableFixture(Fixture):
    def doRows(self, rows):
        self.firstRow = rows
        if rows is None:
            raise FitException("noRows")
        self.doStaticTable(rows.size())

    def getCell(self, row, column):
        return self.firstRow.at(row, column)

    def getText(self, row, column):
        return self.firstRow.at(row, column).text()

    def getRow(self, row):
        return self.firstRow.at(row)

    def doStaticTable(self, unused='numRows'):
        raise Exception("Error in fixture. Virtual method must be overridden.")
                                

