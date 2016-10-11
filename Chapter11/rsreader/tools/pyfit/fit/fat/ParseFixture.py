# ParseFixture from Fit Acceptance Tests
# copyright 2004 Jim Shore
# copyright released under the General Public License (GPL) version 2.0 or later
# Translation to Python copyright 2005 John H. Roth Jr.

import re
from fit.ColumnFixture import ColumnFixture
from fit.Parse import Parse

# A fixture for discussing parsing. 
class ParseFixture(ColumnFixture):
    _typeDict = {"Html": "String",
                 "TableCell": "String",
                 "Entity": "String",
                 "Note": "String",
                 }
    Html = None
    TableCell = None
    Entity = None
    Note = None  # unused
    
    def GenerateParse(self):
        inputColumns = 0
        html = None
        if self.Html is not None:
            inputColumns += 1
            html = self.Html

        if self.TableCell is not None:
            inputColumns += 1
            html = "<table><tr>" + self.TableCell + "</tr></table>"

        if self.Entity is not None:
            inputColumns += 1
            html = "<table><tr><td>" + self.Entity + "</td></tr></table>"


        if inputColumns != 1:
            raise Exception, ("Exactly ONE of the following columns is"
                              " needed: 'Html', 'TableCell', or 'Entity'")

#        html = html.replaceAll("\\\\u00a0", "\u00a0")
        html = self.parseRE.sub(u"\u00a0", html)
        result = Parse(html)
        return result
    parseRE = re.compile(r"\\u00a0", re.I)

    _typeDict["Output"] = "String"
    def Output(self):
        return self.GenerateOutput(self.GenerateParse())
    # ???
    
    def GenerateOutput(self, parse):
        result = parse.toString()
        return result

    _typeDict["Parse"] = "String"    
    def Parse(self):
        print '---------------------- ParseFixture.Parse'
        parse = self.GenerateParse()
        text = self.dumpTables(parse)
        
        print "-- result tables '%s'" % self._xencode(text)
        print "-- result in hex '%s'" % self._xhex(text)
        return text

    def _xencode(self, aString):
        aString = aString.encode("Windows-1252", "replace")
        return aString

    def _xhex(self, aString):
        aString = aString.encode("Windows-1252", "replace")
        aString = aString.encode("hex_codec")
        return aString
    

    def dumpTables(self, table):
        result = ""
        separator = ""
        while table is not None:
            result += separator
            result += self.dumpRows(table.parts)
            separator = "\n----\n"
            table = table.more
        return result
    
    def dumpRows(self, row):
        result = ""
        separator = ""
        while row is not None:
            result += separator
            result += self.dumpCells(row.parts)
            separator = "\n"
            row = row.more
        return result
    
    def dumpCells(self, cell):
        result = ""
        separator = ""
        while cell is not None:
            result += separator
            result += "[" + self.escapeAscii(cell.text()) + "]"
            separator = " "
            cell = cell.more
        return result

    def escapeAscii(self, text):
        text = text.replace("\n", r"\n")
        text = text.replace("\r", r"\r")
        if type(text) == type(""):
            text = text.replace("\xa0", r"\u00a0")
        else:
            text = text.replace(u"\xa0", ur"\u00a0")
            
        return text
