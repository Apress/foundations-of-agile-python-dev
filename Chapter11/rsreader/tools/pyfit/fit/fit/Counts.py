# Counts from core Fit
#LegalStuff cc02 sm02 om03-05 js04-05 jr03-05
# Original Java version Copyright 2002 Cunningham and Cunningham, Inc.
# Released under the terms of the General Public License (GPL), Release 2.1 or later
# See license.txt for terms and disclaimer of all warrenties and liability.
# Original translation to Python Copyright 2002 Simon Michael
# Contains changes copyright 2003-2005 by Object Mentor, Inc.
# Some code copyright 2004-2005 Jim Shore
# changes Copyright 2003-2005 John H. Roth Jr.
# Last updated for Release 0.8a1
#endLegalStuff

import re
import types
from fit.Utilities import FitEnum

try:
    False
except: #pragma: no cover
    True = 1
    False = 0

class Count(FitEnum):
    _numList = ("right", "wrong", "ignore", "exception")
    _strTable = {"rig": 0, "wro": 1, "ign": 2, "exc": 3}

class Counts(object):
    countsPattern = re.compile(r"(\d+)[^,]*, (\d+)[^,]*, (\d+)[^,]*, (\d+)[^,]*")
    def __init__(self, right = 0, wrong = 0, ignored = 0, exceptions = 0):
        self.countType = "SingleTest"
        if isinstance(right, types.StringTypes):
            matcher = self.countsPattern.search(right)
            if matcher is None:
                raise Exception, "invalid parameters to Counts"
            self.right = int(matcher.group(1))
            self.wrong = int(matcher.group(2))
            self.ignores = int(matcher.group(3))
            self.exceptions = int(matcher.group(4))
        else:
            self.right = right
            self.wrong = wrong
            self.ignores = ignored
            self.exceptions = exceptions

    def toString(self):
        return str(self)

    def tally(self, source):
        self.right += source.right
        self.wrong += source.wrong
        self.ignores += source.ignores
        self.exceptions += source.exceptions

    def __iadd__(self, other):
        if isinstance(other, Count):
            self.tabulateCount(other)
        else:
            self.tally(other)
        return self

    def tabulateCount(self, count):
        kind = str(count)
        if kind == "right": self.right += 1
        elif kind == "wrong": self.wrong += 1
        elif kind == "ignore": self.ignores += 1
        elif kind == "exception": self.exceptions += 1
        else:
            raise TypeError, "Count Enumeration expected"

    def __str__(self):
        return ("%s right, %s wrong, %s ignored, %s exceptions" %
                (self.right, self.wrong, self.ignores, self.exceptions))

    def __eq__(self, o):
        if isinstance(o, types.StringTypes):
            o = Counts(o)
        elif not isinstance(o, Counts):
            return NotImplemented
        return (self.right == o.right and
                self.wrong == o.wrong and
                self.ignores == o.ignores and
                self.exceptions == o.exceptions)

    def __ne__(self, o):
        return not self.__eq__(o)

    def totalCounts(self):
        return self.right + self.wrong + self.ignores + self.exceptions

    def isError(self):
        return self.numErrors()  > 0

    def numErrors(self):
        return self.wrong + self.exceptions

    def equals(self, o):
        return self == o

    def summarize(self, c):
        # I consider exceptions worse than wrongs, so I put
        # that count first.
        self.countType = "Summary"
        if c.exceptions > 0:
            self.exceptions += 1
        elif c.wrong > 0:
            self.wrong += 1
        elif c.ignores > 0 and c.right == 0:
            self.ignores += 1
        else:
            self.right += 1
    tallyPageCounts = summarize

    def isSummaryCount(self):
        return self.countType == "Summary"

##    # moved here from PageResult.
##    # note that this is a javaism - should have simply eliminated it.
##    # DEPRECIATED
##    def parse(countString):
##        return Count(countString)
##    parse = staticmethod(parse)
        
