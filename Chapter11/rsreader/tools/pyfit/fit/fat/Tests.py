# Copyright (c) 2002 Cunningham & Cunningham, Inc.
#legalStuff cc02 sm02 jr04
# Original Java version Copyright 2002 Cunningham and Cunningham, Inc.
# Released under the terms of the General Public License (GPL), Release 2.1 or later
# See license.txt for terms and disclaimer of all warrenties and liability.
# Original translation to Python Copyright 2002 Simon Michael
# changes Copyright 2004 John H. Roth Jr.
# Last updated for Release 0.8a1
#endLegalStuff

# This version does not reference network resources; it presumes
# it will run in batch mode on a single workstation.

from fit.Counts import Counts
from fit.Fixture import Fixture
from fit.Parse import Parse
import os
import os.path


class Tests(Fixture):

    heads = None # Parse
    page = None # String

    def doRows(self, rows):
        self.heads = rows.parts
        Fixture.doRows(self, rows.more)

    def doCell(self, cell, column):
        if column == 0:
            self.page = cell.text()
        else:
            language = self.heads.at(column).text()
            runscript = self.getSymbol("Runscripts").get(language)
            self.performTest(cell, runscript, self.page)

    def performTest(self, cell, runscript, page):
        if ((runscript is None or runscript == "null") or page.startswith("?")):
            self.ignore(cell)
            return
        try:
            fileName = cell.text()
            testResult = self.get(fileName)
            if testResult.find("<wiki>") >= 0:
                data = Parse(testResult, ("wiki", "td")).parts
            else:
                data = Parse(testResult, ("td",))
            c = self.count(data)
                               
            message = self.anchor("  %s/%s/%s&nbsp;" %
                                  (c.right, c.wrong, c.exceptions), fileName)

            cell.addToBody(message);
            if c.right > 0 and c.wrong == 0 and c.exceptions == 0:
                self.right(cell)
            else: 
                self.wrong(cell)
                cell.addToBody(data.footnote()); # XXX see note about footnotes.
        except Exception, e:
            if str(e).find("Can't find tag: td") >= 0:
                cell.addToBody("Can't parse <a href=\"" + testResult + "\">page</a>")
                self.ignore(cell)
            else:
                self.exception(cell, e)

    def anchor(self, body, link):
        return "&nbsp;<a href=\"" + link + "\">" + body + "</a>";


    # XXX !!! rewrite for file access...
    # This presumes that the current directory is the fit directory.
    def get(self, url):
        testFile = open(r"Documents/%s" % url, "rt")
        testData = testFile.read()
        testFile.close()
        if testData.find("<wiki>") >= 0:
            runner = "WikiRunner.py"
        else:
            runner = "FileRunner.py"
        cmd = r'python %s "Documents\%s" "Reports\%s"' % (
            runner, url, url)
        os.system(cmd)
        testFile = open("Reports/%s" % url, "rt")
        testData = testFile.read()
        testFile.close()
        return testData

    def count(self, data):
        counts = Counts()
        while (data != None):
            if   data.tagIsRight():   counts.right += 1
            elif data.tagIsWrong():   counts.wrong += 1
            elif data.tagIsError():   counts.exceptions += 1
            elif data.tagIsIgnored(): counts.ignores += 1
            data = data.more
        return counts
