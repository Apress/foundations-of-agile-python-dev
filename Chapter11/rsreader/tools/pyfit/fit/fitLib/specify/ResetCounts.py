# ResetCounts from FitLibrary Acceptance Tests
#legalStuff rm04 jr05
# Original version Contains code developed by Rick Mugridge.
# University of Auckland, NZ. Copyright 2004 Rick Mugridge.
# Released under the terms of the General Public License (GPL), Release 2.1 or later
# See license.txt for terms and disclaimer of all warrenties and liability.
# changes Copyright 2005 John H. Roth Jr.
# Last updated for Release 0.8a1
#endLegalStuff

from fit.Fixture import Fixture

# Clear the counts for the inner fixtures to test fit.Summary.

class ResetCounts(Fixture):
    def doTable(self, unused='table'):
        self.counts.right = 0
        self.counts.wrong = 0
        self.counts.exceptions = 0
        self.counts.ignores = 0

