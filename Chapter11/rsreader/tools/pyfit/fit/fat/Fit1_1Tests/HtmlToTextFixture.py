# HtmlToTextFixture from Fit 1.1 Specification Tests
# Copyright 2005 Jim Shore
# Released under the terms of the GNU General Public License, v2 or later
# Translation to Python copyright 2005, John H. Roth Jr.

import re
from fit.ColumnFixture import ColumnFixture
from fit.Parse import Parse

class HtmlToTextFixture(ColumnFixture):
    _typeDict = {"HTML": "String",
                 "Text": "String",
                 }
    HTML = ""
    
    def Text(self):
        HTML = re.sub(r"\\u00a0", u"\u00a0", self.HTML)
        return self._escapeAscii(Parse.htmlToText(HTML))

    def _escapeAscii(self, text):
        text = re.sub(r"\x0a", r"\\n", text)
        text = re.sub(r"\x0d", r"\\r", text)
        text = re.sub(r"\xa0", r"\\u00a0", text)
        return text
