# Copyright (C) 2003 by Robert C. Martin and Micah D. Martin. All rights reserved.
# Released under the terms of the GNU General Public License version 2 or later.

from fit.Fixture import Fixture, Counts, RunTime
from fit.Parse import Parse
import os, sys, os.path

class RecursiveAllFiles(Fixture):
    def __init__(self):
        self.directory = ""
        self.filenames = []
        self.startingRow = None
        self.page = ""
        self.cwd = os.getcwd()
        print "in RecursiveAllFiles. cwd: '%s'" % (self.cwd,)

    def doTable(self, table):
        self.startingRow = table.parts
        row = self.startingRow.more
        self.startingRow.more = None
        self.startingRow.trailer = " " # Something wrong in Parse - shouldn't need to replace
        self.doRow(row)

    def doRow(self, row):
        self.directory = row.parts.text()
        self.page = row.parts.more.text()
        self.addFileNamesFrom("")
        self.filenames.sort()
        self.doFiles()

    def addFileNamesFrom(self, dirPath):
        newPath = os.path.join(self.directory, dirPath)
        children = os.listdir(newPath)
        for childFileName in children:
            if dirPath == "":
                filename = childFileName
            else:
                filename = os.path.join(dirPath, childFileName)
            # ??? This may not be what's needed for invocation from FitNesse
            longFileName = os.path.join(self.cwd, self.directory, filename)
            if os.path.isdir(longFileName):
                self.addFileNamesFrom(filename)
            else:
                self.filenames.append(filename)

    def getFilenames(self):
        return self.filenames

    def doFiles(self):
        row = self.startingRow
        for filename in self.filenames:
            path = os.path.join(self.directory, filename)
            cells = self.td(self.makeLinkTo(filename), self.td("", None))
            row.more = self.tr(cells, row.more)
            row = row.more
#            row = row.more = self.tr(cells, row.more)
            fixture = Fixture()
#            fixture = ErrorHandlingFixture() # embedded class
            self.run(path, fixture, cells)
            self.summarize(fixture)

    def makeLinkTo(self, filename):
        return ('<a href="/files/testResults/%s">%s</a>' %
                (filename, self.makeRelativePageName(filename)))
        
    def makeRelativePageName(self, filename):
        dottedFileName = filename.replace("/", ".")
        if len(self.page) > 0:
            if dottedFileName.startswith(self.page):
                dottedFileName = dottedFileName[len(self.page)+1:]
        if dottedFileName.endswith(".html"):
            dottedFileName = dottedFileName[:-5]
        return dottedFileName

    def run(self, path, fixture, cells):
        try:
            theTest = self.read(path)
            tables = Parse(theTest)
            fixture.doTables(tables)

            cells.more.addToBody(self.gray(str(fixture.counts)))
            if fixture.counts.wrong == 0 and fixture.counts.exceptions == 0:
                self.right(cells.more)
            else:
                self.wrong(cells.more)
            writer = open(path, "w") # ??? we're overwriting the input???
            writer.write(str(tables))
            writer.close()
        except Exception, e:
            self.exception(cells, e)

    def read(self, inputFileName):
        fileObj = open(inputFileName, "r")
        theTest = fileObj.read()
        fileObj.close()
        return theTest

    def summarize(self, fixture):
        totalString = "total counts"
        runCounts = self.summary.get(totalString)
        if not runCounts:
            runCounts = Counts()
        runCounts.tally(fixture.counts)
        self.summary[totalString] = runCounts

    def tr(self, cells, more):
        return Parse(tag="tr", body="", parts=cells, more=more)

    def td(self, text, more):
        return Parse(tag="td", body=self.gray(text), parts=None, more=more)

##class ErrorHandlingFixture(Fixture):
##
### I don't see the point of this, since it seems like an exact
### duplicate of the method in Fixture.
##    
##    def doTables(self, tables):
##        self.summary["run date"] = time.ctime(time.time())
##        self.summary["run elapsed time"] = RunTime()
##        while tables:
##            heading = tables.at(0, 0, 0)
##            if heading:
##                try:
##                    path = heading.text()
##                    clas = path.split('.')[-1]
##                    i = path.split('$')
##                    if len(i) == 1:
##                        exec 'import '+path
##                        exec 'fixture = '+path+'.'+clas+'()'
##                    else:
##                        exec "import %s" % (i[0],)
##                        exec "fixture = %s.%s()" % (i[0], i[1])
##                    fixture.counts = self.counts
##                    fixture.summary = self.summary
##                    fixture.doTable(tables)
##                except Exception, e:
##                    self.exception(heading, e)
##            tables = tables.more
    
