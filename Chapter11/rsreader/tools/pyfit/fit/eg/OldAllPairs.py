# This fixture does the all pairs example, but it does it differently.
# some of the code Copyright (c) 2002 Cunningham & Cunningham, Inc.,
# released under the GUN General Public License version 2.
# Copyright 2003 John Roth, released under the GNU General Public License, version 2.

# The original Java fixture turned out to be much too large to
# work with. The algorithm seemed to be overkill for the problem,
# which was to produce all pairs of files in an input list of
# lists of files, such that both of the files in a pair couldn't
# come from the same list.

# Without the constraint, this is a real simple, even stupid,
# problem. If we call the first member of the pair Laurel, and
# the second one Hardy, and we have a list that starts with one
# and goes on up to whatever, we simply put Laurel on the first
# one, and start Hardy on up the list with the next one. Once
# Hardy runs off the end, we move Laurel up one, and start Hardy
# off again at the square immediately after Laurel. Stupid simple
# enough that even I can figure it out.

# The constraint complicates it slightly. Instead of starting
# Hardy off on the next square after Laurel, he has to start
# on the first square on the next block.

from eg.AllCombinations import AllCombinations
from eg.AllFiles import AllFiles

class AllPairs(AllCombinations):
    lists = []
    row = None
    caseNumber = 1

    def __init__(self):
        self.caseNumber = 1
        self.lists = []
        self.row = None

    def doTable(self, table):
        self.row = table.parts.last()
        AllFiles.doTable(self, table)
        self.generatePairs()

    def doRowFiles(self, unused, files):
        self.lists.append(files)

    def generatePairs(self):
        fileList, listList = self.flattenLists()
        i = 1
        while i < len(fileList):
            j = self.findNextBlock(i, listList)
            while j < len(fileList):
                self.doCase([fileList[i], fileList[j]])
                j += 1
            i += 1

    def flattenLists(self):
        listNumber = 0
        fileList = []
        listList = []
        for outerList in self.lists:
            for fileName in outerList:
                fileList.append(fileName)
                listList.append(listNumber)
            listNumber += 1
        return fileList, listList

    def findNextBlock(self, i, listList):
        if i >= len(listList):
            return i + 1
        iBlock = listList[i]
        j = i + 1
        while j < len(listList):
            if listList[j] != iBlock: break
            j += 1
        return j

##    def doCase(self, combination):
##        number = self.tr(self.td("#%s" % (self.caseNumber,), None), None)
##        self.caseNumber += 1
##        number.leaf().addToTag(" colspan=2")
##        self.row.last().more = number
##        AllFiles.doRowFiles(self, number, combination)    