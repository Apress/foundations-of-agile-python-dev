# SetFixture from FitLibrary
#legalStuff rm04 jr05
# Original version Contains code developed by Rick Mugridge.
# University of Auckland, NZ. Copyright 2004 Rick Mugridge.
# Released under the terms of the General Public License (GPL), Release 2.1 or later
# See license.txt for terms and disclaimer of all warrenties and liability.
# changes Copyright 2005 John H. Roth Jr.
# Last updated for Release 0.8a1
#endLegalStuff

from fitLib.ArrayFixture import ArrayFixture
from fitLib.FitLibraryExceptions import ExtraCellsFailureException, \
     MissingCellsFailureException

#
# A more flexible alternative to RowFixture:
# o The collection may be provided as an array, Collection or Iterator
# o The column names may refer to properties of an element Object.
# o The elements don't have to be of related types. Where a column doesn't
#   apply to a particular element, the expected value must be blank.
# 
# For large sets, this is a more expensive algorithm than used in RowFixture.

class SetFixture(ArrayFixture):
    # Only real method in ArrayFixture that's overridden
    # may have to split out the ArrayFixture method, though.
    def doOneRow(self, row, adapters, actuals):
        if not actuals:
            self.missing(row)
            return

        rowLength = row.parts.size()
        if rowLength < len(adapters):
            raise MissingCellsFailureException()
        if rowLength > len(adapters):
            raise ExtraCellsFailureException()

        matchingActuals = actuals
        column = 0
        while column < len(adapters):
            matchingActuals = self._matchOnColumn(row, matchingActuals,
                                                  adapters, column)
            if not matchingActuals:
                self.missing(row)
                return
            if len(matchingActuals) == 1: # Got a match!
                self._foundMatch(matchingActuals, row, adapters, actuals)
                return
            column += 1
        
        # We ran out of columns. The number of actuals left ought to
        # be > 1, but we test anyway [grumph]
        if matchingActuals:
            self._foundMatch(matchingActuals, row, adapters, actuals)
            return

    def _foundMatch(self, matchingActuals, row, adapters, actuals):        
        theOne = matchingActuals[0]
        self.matchRow(row.parts, adapters, theOne)
        aIndex = actuals.index(theOne)
        del actuals[aIndex]
        return

    # Returns the subset of actuals that match on the given column of the row */
    def _matchOnColumn(self, row, actuals, adapters, column):
        results = []
        adapter, name, symrefs = adapters[column]
        cell = row.parts.at(column)
        text = cell.text()
        for objectOrDict in actuals:
            if adapter is None and cell.text() == "":
                results.append(objectOrDict)
            else:
                try:
                    if self._matches(text, adapter, name, objectOrDict): 
                        results.append(objectOrDict)
                except Exception:
                    pass
        return results

    def _matches(self, text, adapter, name, objectOrDict):
        hasKey, obj = self._getObj(name, objectOrDict)
        if not hasKey:
            return text == ""
        return adapter.stringEquals(text, obj)

            
