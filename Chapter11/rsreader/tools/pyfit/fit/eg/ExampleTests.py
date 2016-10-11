# Copyright (c) 2002 Cunningham & Cunningham, Inc.
# Read license.txt in this directory.
# Converted to Python 2003/07/26 by John Roth


from fit.ColumnFixture import ColumnFixture
from fit.Fixture import Fixture, Counts
from fit.Parse import Parse


class ExampleTests(ColumnFixture):
    fileName = ""
    wiki = 0
    _typeDict = {"fileName": "String",
                 "file.renameTo": "fileName",
                 "wiki": "Boolean"}
        
    def __init__(self):
        ColumnFixture.__init__(self)
        self.fileName = ""
        self.wiki = 0
        self.input = ""
        self.tables = None
        self.fixture = None
        self.runCounts = Counts()
        self.footnote = None
        self.fileCell = None

    def run(self):
        newFileName = "fat/Documents/" + self.fileName
        inFile = open(newFileName, 'r')
        theTest = inFile.read()
        inFile.close()
        self.fixture = Fixture()
        self.footnote = None
        if self.wiki:
            self.tables = Parse(text=theTest, tags=("wiki", "table", "tr", "td"))
        else:
            self.tables = Parse(text=theTest, tags=("table", "tr", "td"))
        self.fixture.doTables(self.tables)
        self.runCounts.tally(self.fixture.counts)
        self.summary["counts run"] = self.runCounts

    _typeDict["right_"] = "Int"
    _typeDict["right.renameTo"] = "right_"
    def right_(self):
        self.run()
        return self.fixture.counts.right

    _typeDict["wrong_"] = "Int"
    _typeDict["wrong.renameTo"] = "wrong_"
    def wrong_(self):
        return self.fixture.counts.wrong

    _typeDict["ignores"] = "Int"
    def ignores(self):
        return self.fixture.counts.ignores

    _typeDict["exceptions"] = "Int"
    def exceptions(self):
        return self.fixture.counts.exceptions

    def doRow(self, row):
        self.fileCell = row.leaf()
        ColumnFixture.doRow(self, row)

    def wrong(self, cell, actual = None, escape=True):
#        super(ExampleTests, self)
        ColumnFixture.wrong(self, cell, actual = actual, escape = escape)
        if self.footnote == None:
            self.footnote = self.tables.footnote()
            self.fileCell.addToBody(self.footnote)
        
    

