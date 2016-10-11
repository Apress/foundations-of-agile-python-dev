# Copyright (c) 2002 Cunningham & Cunningham, Inc.
# Released under the terms of the GNU General Public License version 2 or later.
# Python version copyright (c) 2004 John H. Roth Jr.

from fit.ColumnFixture import ColumnFixture

class Frameworks(ColumnFixture):
    def __init__(self):
        ColumnFixture.__init__(self)
        try:
            self.getSymbol("Runscripts")
        except:
            self.setSymbol("Runscripts", {})

    _typeDict = {
        "language": "String",
        "page": "String",
        "runscript": "String",
        }

    language = ""
    page = ""
    runscript = ""

    def reset(self):
        self.language = self.page = self.runscript = None

    def execute(self):
        if self.language != None and self.runscript != None:
            scriptDict = self.getSymbol("Runscripts")
            scriptDict[self.language] = self.runscript
            
