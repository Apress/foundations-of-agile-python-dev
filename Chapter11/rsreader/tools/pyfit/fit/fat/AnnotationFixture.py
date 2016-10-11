# AnnotationFixture from Fit Acceptance Tests
# copyright 2004 Jim Shore
# released under the GNU General Public License, version 2.0 or higher
# Translation to Python copyright 2005 John H. Roth Jr.

from fit.ColumnFixture import ColumnFixture
from fit.Fixture import Fixture
from fit.Parse import Parse

class AnnotationFixture(ColumnFixture):
    _typeDict = {"Type": "String",
                 "Text": "String",
                 "OriginalCell": "String",
                 }
    Type = ""
    Text = ""
    OriginalCell = "Text";

    _typeDict["Output"] = "String"    
    def Output(self):
        parse = Parse(tag="td", body=self.OriginalCell)
        hack = Fixture()
        
        if self.Type == "none":
            pass
        elif self.Type == "right":
            hack.right(parse)
        elif self.Type == "wrong":
            hack.wrong(parse, self.Text)
        elif self.Type == "error":
            return "not implemented"
        elif self.Type == "ignore":
            hack.ignore(parse)
        elif self.Type == "unchecked":
            return "not implemented"
        else:
            return "unknown type: " + self.Type
        return self._GenerateOutput(parse)
    
    # code smell note: copied from ParseFixture    
    def _GenerateOutput(self, parse):
        result = parse.toString()
        return result
