#legalNotices t$ jhr5 GPL
#endLegalNotices

# fixtures for acceptance tests for label mapping

from fit.ColumnFixture import ColumnFixture

class LabelMappingFixture(ColumnFixture):
    _typeDict = {".display": "on",
                 ".markup": "off",
                 "camel_": "String",
                 "camel.columnType": "result",
                 "camel.renameTo": "camel_",
                 "extendedCamel": "String",
                 "extendedCamel.columnType": "result",
                 "gracefulNames": "String",
                 "gracefulNames.columnType": "result",
                 "label": "String",
                 "label.columnType": "given",
                 "notes.columnType": "comment",
                 }

    label = ""
    
    def camel_(self):
        return super(LabelMappingFixture, self).camel(self.label, "camel")

    def gracefulNames(self):
        return super(LabelMappingFixture, self).camel(self.label, "gracefulNames")

    def extendedCamel(self):
        return super(LabelMappingFixture, self).camel(self.label, "extended")
    