# Copyright (c) 2002 Cunningham & Cunningham, Inc.
# Released under the terms of the GNU General Public License version 2 or later.
# Converted to Python 2003/07/27 by John Roth

from eg.AllFiles import AllFiles

class AllCombinations(AllFiles):
    lists = []
    row = None
    caseNumber = 1

    def __init__(self):
        AllFiles.__init__(self)
        self.caseNumber = 1
        self.lists = []
        self.row = None

    def doTable(self, table):
        self.row = table.parts.last()
        AllFiles.doTable(self, table)
        self.combinations()

    def doRowFiles(self, unused, files):
        self.lists.append(files)

    def combinations(self):
        newList= [None] * len(self.lists)
        self.comboRecursion(0, newList)

    def comboRecursion(self, index, combination):
        if index == len(self.lists):
            self.doCase(combination)
        else:
            files = self.lists[index]
            for aFile in files:
                combination[index] = aFile
                self.comboRecursion(index+1, combination)

    def doCase(self, combination):
        number = self.tr(self.td("#%s" % (self.caseNumber,), None), None)
        self.caseNumber += 1
        number.leaf().addToTag(" colspan=2")
        self.row.last().more = number
        AllFiles.doRowFiles(self, number, combination)
