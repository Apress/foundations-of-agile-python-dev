# This fixture does the all pairs example, but it does it differently.
# some of the code Copyright (c) 2002 Cunningham & Cunningham, Inc.,
# released under the GUN General Public License version 2.
# Copyright 2003 John Roth, released under the GNU General Public License, version 2.

# The original Java fixture turned out to be much too large to
# work with. The algorithm seemed to be overkill for the problem,
# which was to produce a minimal set of the output from
# AllCombinations such that each pair of files is represented
# the least number of times. In other words, the ideal output
# is that there is only one case in the set where any given
# pair of files occurs.

# This is a much simpler approach to the problem. On the first
# pass, we generate the same output as AllCombinations, but we
# put it into a list.

# Then we repetitively evaluate the list, looking for entries
# that have N unique pairs of files: m * (m-1) / 2. On each pass
# through the list, we reduce N by one. We also remove entries
# where all pairs have already been generated. The algorithm
# ends when the list is empty.

# While this approach isn't minimal (the naive theoretical
# minimum for the example data is 9 cases) it crams all
# 26 pairs into 11 cases, while the original algorithm manages
# to put them into 16 cases! (And no, I didn't do any kind
# of theoretical study of the matter. I just implemented the
# simplest algorithm I could imagine that would produce the
# desired output.)

# On the other hand, while I can't comment on the time
# complexity of the original algorithm (outside of pointing
# out all of those double loops) this one is on the wrong
# side of O(n*n) in the number of categories. It may well
# be faster, though.

from eg.AllCombinations import AllCombinations
from eg.AllFiles import AllFiles

class AllPairs(AllCombinations):

    def __init__(self):
        AllCombinations.__init__(self) # ??? should this be AllFiles.__init__ ???
        self.caseList = []
        self.pairs = {}
        self.caseNumber = 1
        self.lists = []
        self.row = None

    #
    # generate cases
    #
    
    def doTable(self, table):
        __pychecker__ = 'no-local'
        self.row = table.parts.last()
        AllFiles.doTable(self, table)
        self.combinations()
        for aCase in self.caseList:
            self.generate()

    def doCase(self, combination): # overrides AllCombinations
        newList = [] # make sure we've got a unique list each time!!!
        newList[:] = combination[:]
        self.caseList.append(newList)

    #
    # generate output
    #

    def generate(self):
        numPairsWanted = len(self.lists) * (len(self.lists) - 1) / 2
        if numPairsWanted > 1:
            while numPairsWanted > 0 and len(self.caseList) > 0:
                i = 0
                while i < len(self.caseList):
                    numUngeneratedPairs = self.evaluateCase(self.caseList[i])
                    if numUngeneratedPairs == 0:
                        del self.caseList[i]
                    elif numUngeneratedPairs >= numPairsWanted:
                        self.addToPairTable(self.caseList[i])
                        AllCombinations.doCase(self, self.caseList[i])
                        del self.caseList[i]
                    else:
                        i += 1
                numPairsWanted -= 1
        else:
            for case in self.caseList:
                AllCombinations.doCase(self, case)
        self.summary["total pairs"] = "%s" % len(self.pairs)

    def factorial(self, number):
        return reduce(lambda x, y: x * y, range(1, number + 1))

    def evaluateCase(self, fileList):
        numUngeneratedPairs = 0
        for i in range(len(fileList)-1):
            for j in range(i+1, len(fileList)):
                key = fileList[i] + "*" + fileList[j]
                isPresent = self.pairs.get(key)
                if isPresent == None:
                    numUngeneratedPairs += 1
        return numUngeneratedPairs

    def addToPairTable(self, fileList):    
        for i in range(len(fileList)-1):
            for j in range(i+1, len(fileList)):
                key = fileList[i] + "*" + fileList[j]
                numOccurances = self.pairs.get(key, 0)
                self.pairs[key] = numOccurances + 1
