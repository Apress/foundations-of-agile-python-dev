# Check Configuration Fixture
# Copyright 2005 John H. Roth Jr.
# Released under the terms of the GNU General Public License, version 2.0 or later

# Verify the configuration for tests that require a specific configuration
# to run.

from fit import FitGlobal
from fit.Fixture import Fixture
from fit.Utilities import em

class CheckConfiguration(Fixture):
    def doRow(self, cells):
        cellList = self._makeListFromRow(cells)
        try:
            self._checkRow(cellList)
        except Exception, e:
            self.exception(cellList[0], e)

    def _makeListFromRow(self, row):
        cellList = []
        cells = row.parts
        while cells:
            cellList.append(cells)
            cells = cells.more
        return cellList

    def _checkRow(self, cellList):
        text1 = cellList[0].text()
        checker = self.checkDict.get(text1)
        if checker is None:
            raise Exception("Unknown service name")
        checker(self, cellList[1:])

    def checkOptions(self, cellList):
        self.checkObjectReference(cellList, FitGlobal.Options)

    def checkRunOptions(self, cellList):
        self.checkObjectReference(cellList, FitGlobal.RunOptions)

    def checkObjectReference(self, cellList, theObj = None):
        if len(cellList) != 2:
            raise Exception, "Wrong number of cells in row."
        attr = cellList[0].text()
        actual = getattr(theObj, attr, None)
        if actual is None:
            self.exception(cellList[0], "Attribute name doesn't exist")
            return
        self.checkResult(cellList[1], str(actual))
        return

    def checkEnvironment(self, cellList):
        self.checkScalar(cellList, FitGlobal.Environment)

    def checkScalar(self, cellList, theObj = None):
        if len(cellList) != 1:
            raise Exception, "Wrong number of cells in row."
        self.checkResult(cellList[0], str(theObj))
        return

    def checkResult(self, cell, actual):    
        expected = cell.text()
        if str(actual) != expected:
            self.wrong(cell, actual)
        else:
            self.right(cell)
        return

    checkDict = {
        "Options": checkOptions,
        "RunOptions": checkRunOptions,
        "Environment": checkEnvironment,
        }
        
        