# OutputFixture from FIT Acceptance Tests
# copyright 2004 Jim Shore
# copyright released under the GNU General Public License, version 2.0 or above
# Translation to Python copyright 2005, John H. Roth Jr.

from fit.ColumnFixture import ColumnFixture
from fit.Parse import Parse
from fit.Fixture import Fixture

class OutputFixture(ColumnFixture):
    _typeDict = {"Text": "String"}
    Text = ""

    _typeDict["CellOutput"] = "String"
    def CellOutput(self):
        cell = Parse(tag="td")
        cell.leader = ""
        cell.body = Fixture.escape(self, self._unescape(self.Text))
        return self._GenerateOutput(cell)

    def _unescape(self, text): 
        text = text.replace(ur"\n", "\n")
        text = text.replace(ur"\r", "\r")
        return text
    
    def _GenerateOutput(self, parse):
        result = parse.toString()
        return result
