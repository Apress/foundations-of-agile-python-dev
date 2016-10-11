# CombinationFixture from  FitLibrary
#LegalNotices rm2005 pyjr2005
#endLegalNotices

from fit.FitException import FitException
from fit.Parse import Parse
from fit import TypeAdapter

from fitLib.CalculateFixture import CalculateFixture

class CombinationFixture(CalculateFixture):
    def __init__(self, sut=None):
        super(CombinationFixture, self).__init__(sut)
        self.topValues = []
        self.methodOK = False
        self.method = None # MethodTarget
    
    def bind(self, row):
        try:
            self.method = self.findMethod("combine", 2)
        except Exception, e:
            self.exception(row, e)
            return

        heads = row.more
        self.methodOK = True
        while heads is not None:
            try:
                self.topValues.append(None)
                obj = self.method.parameterAdapters[2].parse(heads)
                self.topValues[-1] = obj
            except Exception, e:
                self.exception(heads, e)
                self.methodOK = False
            heads = heads.more

    def doRow(self, row):
        cell = row.parts
        try:
            if cell is None: # factor cell is missing
                cell = Parse(tag="td", body="cell added")
                row.parts = cell
                raise FitException("MissingCellsFailureException")
            arg1 = self.method.parameterAdapters[1].parse(cell)
            cell = cell.more
            self._validateCellExists(cell)
            self._validateRowLength(cell, len(self.topValues))
            if self.methodOK is False:
                self.ignore(row)
                return
            i = 0
            while cell != None:
                result = self.method.invokeWithArgs([arg1, self.topValues[i]])
                self.method.checkResult(cell, result)
                cell = cell.more
                i += 1
        except Exception, e:
            self.exception(cell, e)
            self.methodOK = False

    def _validateCellExists(self, cell):
        if cell is None:
            raise FitException("MissingCellsFailureException")

    def _validateRowLength(self, firstCellInRow, rowLength):
        numCellsInRow = firstCellInRow.size()
        if numCellsInRow < rowLength:
            raise FitException("MissingCellsFailureException")
        if numCellsInRow > rowLength:
            raise FitException("ExtraCellsFailureException")

