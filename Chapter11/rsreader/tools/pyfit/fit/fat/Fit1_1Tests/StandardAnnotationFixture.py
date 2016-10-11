# Standard Annotation Fixture from Fit 1.1 Specification Tests
# copyright 2005 Jim Shore
# Translation to Python copyright 2005 John H. Roth Jr.

from fit.ColumnFixture import ColumnFixture
from fit.Fixture import Fixture
from fit.Parse import Parse

class StandardAnnotationFixture(ColumnFixture):
    _typeDict = {}
    _typeDict["OriginalHTML"] = "String"
    OriginalHTML = "Text"
    _typeDict["Annotation"] = "String"
    Annotation = ""
    _typeDict["Text"] = "String"
    Text = ""
    
    _typeDict["Output"] = "String"
    def Output(self):
        parse = Parse(self.OriginalHTML, ["td"])
        testbed = Fixture()
        
        if self.Annotation == "right": testbed.right(parse)
        if self.Annotation ==  "wrong": testbed.wrong(parse, self.Text)
        if self.Annotation == "error": testbed.error(parse, self.Text)
        if self.Annotation == "info": testbed.info(parse, self.Text) 
        if self.Annotation == "ignore": testbed.ignore(parse)
                
        return self.GenerateOutput(parse) 
    
    def doCell(self, cell, column):
        try:
            if column == 4:
                cell.body = self.RenderedOutput()
            else:
                super(StandardAnnotationFixture, self).doCell(cell, column)
                
        except Exception, e:
            self.exception(cell, e)

    _typeDict["RenderedOutput"] = "String"
    def RenderedOutput(self):
        return "<table border='1'><tr>" + self.Output() + "</tr></table>"       
    
    def GenerateOutput(self, parse):
        return parse.toString()
