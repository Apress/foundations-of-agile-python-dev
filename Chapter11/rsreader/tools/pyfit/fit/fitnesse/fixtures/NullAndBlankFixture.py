# NullAndBlankFixture from FitNesse acceptance tests
# copyright 2003, 2004 Object Mentor.
# Released under the terms of the GNU General Public License version 2 or later

from fit.ColumnFixture import ColumnFixture
from fit.TypeAdapter import TypeAdapter

class NoneTypeAdapter(TypeAdapter):
    def parse(self, a):
        return None
    def equals(self, a, b):
        return a is None and b is None

class NullAndBlankFixture(ColumnFixture):
    _typeDict = {"nullString": "String",
                 "blankString": "String",
                 "isNull": "Boolean",
                 "isBlank": "Boolean"
                 }
    _nullString = None
    def getNullString(self):
        return None
    def setNullString(self, aString):
        self._nullString = aString
    nullString = property(getNullString, setNullString)

    _blankString = ""
    def getBlankString(self):
        return ""
    def setBlankString(self, aString):
        self._blankString = aString
    blankString = property(getBlankString, setBlankString)

    def isNull(self):
        return self._nullString is None

    def isBlank(self):
        return len(self._blankString) == 0
