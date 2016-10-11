# TextToHtmlFixture from Fit 1.1 Specification Tests
# Copyright 2005 Jim Shore
# Translation to Python copyright 2005 John H. Roth Jr.

import re
from fit.ColumnFixture import ColumnFixture
from fit.Fixture import Fixture

class TextToHtmlFixture(ColumnFixture):
    _typeDict = {}
    _typeDict["Text"] = "String"
    Text = ""

    _typeDict["HTML"] = "String"
    def HTML(self):
        Text = self.unescapeAscii(self.Text)
        return Fixture.escape(self, Text)

    def unescapeAscii(self, text):
        text = re.sub(r"\\n", "\n", re.sub(r"\\r", "\r", text))
        return text
    
    def GenerateOutput(self, parse):
        return parse.toString()

