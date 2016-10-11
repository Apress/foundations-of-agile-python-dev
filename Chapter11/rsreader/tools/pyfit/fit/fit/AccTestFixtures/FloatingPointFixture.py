# Floating Point Extensions acceptance test fixtures
#LegalStuff jr5
#endLegalStuff

from fit.ColumnFixture import ColumnFixture
from fit.Utilities import em

class FloatingPointFixture(ColumnFixture):
    _typeDict = {"given": "Float",
                 "given.columnType": "given",
                 "given.checkType": "eer",
                 "result.renameTo": "given",
                 "result.columnType": "result",
                 "notes.columnType": "comment",
                 }

    def doTable(self, tables):
        args = self.getArgs()
        if len(args) > 0:
            self._typeDict["given.checkType"] = args[0]
        super(FloatingPointFixture, self).doTable(tables)
        
    given = 1.0

