# Annotation Fixture from Fit 1.1 Specification tests
# Copyright 2005 Jim Shore
# Translation to Python copyright 2005 John H. Roth Jr.

import re
from fit.ColumnFixture import ColumnFixture
from fit.Parse import Parse

class AnnotationFixture(ColumnFixture):
    _typeDict = {}
    _typeDict["OriginalHTML"] = "String"
    OriginalHTML = None
    _typeDict["Row"] = "Int"
    Row = 0
    _typeDict["Column"] = "Int"
    Column = 0
   
    _typeDict["OverwriteCellBody"] = "String"
    OverwriteCellBody = None
    _typeDict["AddToCellBody"] = "String"
    AddToCellBody = None
   
    _typeDict["OverwriteCellTag"] = "String"
    OverwriteCellTag = None
    _typeDict["OverwriteEndCellTag"] = "String"
    OverwriteEndCellTag = None
    _typeDict["AddToCellTag"] = "String"
    AddToCellTag = None
   
    _typeDict["OverwriteRowTag"] = "String"
    OverwriteRowTag = None
    _typeDict["OverwriteEndRowTag"] = "String"
    OverwriteEndRowTag = None
    _typeDict["AddToRowTag"] = "String"
    AddToRowTag = None

    _typeDict["OverwriteTableTag"] = "String"
    OverwriteTableTag = None
    _typeDict["OverwriteEndTableTag"] = "String"
    OverwriteEndTableTag = None
    _typeDict["AddToTableTag"] = "String"
    AddToTableTag = None
    
    _typeDict["AddCellFollowing"] = "String"
    AddCellFollowing = None
    _typeDict["RemoveFollowingCell"] = "String"
    RemoveFollowingCell = None
    
    _typeDict["AddRowFollowing"] = "String"
    AddRowFollowing = None
    _typeDict["RemoveFollowingRow"] = "String"
    RemoveFollowingRow = None
    
    _typeDict["AddTableFollowing"] = "String"
    AddTableFollowing = None

    _typeDict["ResultingHTML"] = "String"
    def ResultingHTML(self):
        table = Parse(self.OriginalHTML)
        row = table.at(0, self.Row - 1)
        cell = row.at(0, self.Column - 1)
        
        if (self.OverwriteCellBody is not None):
            cell.body = self.OverwriteCellBody
        if (self.AddToCellBody is not None):
            cell.addToBody(self.AddToCellBody)
        
        if (self.OverwriteCellTag is not None):
            cell.tag = self.OverwriteCellTag
        if (self.OverwriteEndCellTag is not None):
            cell.end = self.OverwriteEndCellTag
        if (self.AddToCellTag is not None):
            cell.addToTag(self.stripDelimiters(self.AddToCellTag))
        
        if (self.OverwriteRowTag is not None):
            row.tag = self.OverwriteRowTag
        if (self.OverwriteEndRowTag is not None):
            row.end = self.OverwriteEndRowTag
        if (self.AddToRowTag is not None):
            row.addToTag(self.stripDelimiters(self.AddToRowTag))

        if (self.OverwriteTableTag is not None):
            table.tag = self.OverwriteTableTag
        if (self.OverwriteEndTableTag is not None):
            table.end = self.OverwriteEndTableTag
        if (self.AddToTableTag is not None):
            table.addToTag(self.stripDelimiters(self.AddToTableTag))

        if (self.AddCellFollowing is not None):
            self.addParse(cell, self.AddCellFollowing, ["td"])
        if (self.RemoveFollowingCell is not None):
            self.removeParse(cell)
                
        if (self.AddRowFollowing is not None):
            self.addParse(row, self.AddRowFollowing, ["tr", "td"])
        if (self.RemoveFollowingRow is not None):
            self.removeParse(row)
        
        if (self.AddTableFollowing is not None):
            self.addParse(table, self.AddTableFollowing,
                          ["table", "tr", "td"])

        return self.GenerateOutput(table)

    def addParse(self, parse, newString, tags):
        newParse = Parse(newString, tags)
        newParse.more = parse.more
        newParse.trailer = parse.trailer
        parse.more = newParse
        parse.trailer = None # ??? S/b ""

    def removeParse(self, parse):
        parse.trailer = parse.more.trailer
        parse.more = parse.more.more
    
    def stripDelimiters(self, s):
        return re.sub(r"^\[", "", re.sub(r"]$", "", s))
    
    def GenerateOutput(self, document):
        return document.toString().strip()
