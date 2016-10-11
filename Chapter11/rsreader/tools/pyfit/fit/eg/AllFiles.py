# Copyright (c) 2002 Cunningham & Cunningham, Inc.
# Released under the terms of the GNU General Public License version 2 or later.
# Converted to Python 2003/07/27 by John Roth


from fit.Fixture import Fixture, Counts
from fit.ColumnFixture import ColumnFixture
from fit.Parse import Parse
import os
import os.path
import glob
import time

class AllFiles(Fixture):

    # !!! note that overloaded doRow(row, files) has been renamed doRowFiles
    def doRow(self, row):
        cell = row.leaf()
        files = self.expand(cell.text())
        if len(files) > 0:
            self.doRowFiles(row, files)
        else:
            self.ignore(cell)
            self.info(cell, " no match")

    # since I couldn't follow the logic, and since Python has a
    # perfectly usable implmenetation of Unix style shell filename
    # expansion, I used it. This is way more functionality than the
    # Java version, but so be it...
    
    def expand(self, pattern):
        return glob.glob(pattern)

    # overload of doRow.
    def doRowFiles(self, row, files):
        self.doFiles(row, files)

    def doFiles(self, row, files):
        for fileName in files:
            cells = self.td(fileName, self.td("", None))
            row.more = self.tr(cells, row.more)
            row = row.more
            fixture = Fixture()
            self.run(fileName, fixture, cells)
            self.summarize(fixture, fileName)

    runCount = 0 # !!! (unused?) static class variable

    def run(self, path, fixture, cells):
        if self.pushAndCheck(path):
            self.ignore(cells)
            self.info(cells, "recursive")
            return
        try:
            theTest = self.read(path)
            if theTest.find("<wiki>") >= 0:
                tags=["wiki", "table", "tr", "td"]
            else:
                tags=["table", "tr", "td"]
            tables = Parse(text=theTest, tags=tags)
            fixture.doTables(tables)
            self.info(cells.more, fixture.counts.toString())
            if fixture.counts.wrong == 0 and fixture.counts.exceptions == 0:
                self.right(cells.more)
            else:
                self.wrong(cells.more)
                cells.more.addToBody(tables.footnote())
        except Exception, e:
            self.exception(cells, e)
        self.pop(path)

    fileStack = []

    def pushAndCheck(self, path):
        newPath = os.path.abspath(path)
        if newPath in self.fileStack:
            return 1
        else:
            self.fileStack.append(newPath)
            return 0

    def pop(self, path):
        newPath = os.path.abspath(path)
        i = self.fileStack.index(newPath)
        del self.fileStack[i]

    def summarize(self, fixture, path):
        fixture.summary["input file"] = os.path.abspath(path)
        fixture.summary["input update"] = time.ctime(os.path.getmtime(path))
        runCounts = self.summary.get("counts run")
        if not runCounts:
            runCounts = Counts()
            self.summary["counts run"] = runCounts
        runCounts.tally(fixture.counts)

    def read(self, fileName):
        inFile = open(fileName, "rt")
        theTest = inFile.read()
        inFile.close()
        return theTest

    def tr(self, cells, more):
        return Parse(tag="tr", body=None, parts=cells, more=more)

    def td(self, text, more):
        return Parse(tag="td", body=self.info(text), more=more)


class Expand(ColumnFixture):
    
    _typeDict = {"path": "String",
                 "expansion": "String"}
    
    path = ""

    def __init__(self):
        self.fixture = AllFiles()
    
    def expansion(self):
        files = self.fixture.expand(self.path)
        aList = [os.path.basename(x) for x in files]
        return ",".join(aList)

"""

    // Self Test ////////////////////////////////

    public static class Expand extends ColumnFixture {

        public String path;
        AllFiles fixture = new AllFiles();

        public String[] expansion() {
            List files = fixture.expand(path);
            String[] result = new String[files.size()];
            for (int i=0; i<result.length; i++) {
                result[i] = ((File)files.get(i)).getName();
            }
            return result;
        }
    }

"""    



