#legalNotices t$ jhr5 GPL
#endLegalNotices

# fixtures for acceptance tests for extensions to the ColumnFixture.

from fit.ColumnFixture import ColumnFixture

class NoMarkup(ColumnFixture):
    _typeDict = {".display": "on",
                 ".markup": "off",
                 "a": "Int",
                 "a.columnType": "given",
                 "b": "Int",
                 "b.columnType": "given",
                 "c": "Int",
                 "c.columnType": "result",
                 "checkFromSaved.columnType": "checkSaved",
                 "checkFromSaved.renameTo": "c",
                 "displayB.columnType": "display",
                 "displayB.renameTo": "b",
                 "displayC.columnType": "display",
                 "displayC.renameTo": "c",
                 "getSavedValue.columnType": "displaySaved",
                 "itSAComment.columnType": "comment",
                 "saveA.columnType": "saveResult",
                 "saveA.renameTo": "a",
                 "saveB.columnType": "saveResult",
                 "saveB.renameTo": "b",
                 "saveC.columnType": "saveResult",
                 "saveC.renameTo": "c",
                 "storeSavedA.columnType": "storeSaved",
                 "storeSavedA.renameTo": "a",
                 
                 }

    a = 0
    b = 0
    def c(self):
        return self.a + self.b
