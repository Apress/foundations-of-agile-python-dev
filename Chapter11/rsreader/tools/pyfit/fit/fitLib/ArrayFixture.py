# ArrayFixture from FitLibrary
#legalStuff rm04 jr05
# Original version Contains code developed by Rick Mugridge.
# University of Auckland, NZ. Copyright 2004 Rick Mugridge.
# Released under the terms of the General Public License (GPL), Release 2.1 or later
# See license.txt for terms and disclaimer of all warrenties and liability.
# changes Copyright 2005 John H. Roth Jr.
# Last updated for Release 0.8a1
#endLegalStuff

# A fixture like fit.RowFixture, except that the order of rows is important
# and properties are supported.
# The algorithm used for matching is very simple; a diff approach may be better.
# 
# o Instead of running over the actual elements, run over the bindings for those objects
# o Delete the bindings as they match
# o No need to set the targets because that's already done
# o Instead of build surplus from the remaining elements, do it from remaining bindings.
# o Handle the case where an element doesn't have a field,
#   in which case the expected should be empty
# o Take a Collection as an arg to the constructor
# 
# See the FixtureFixture specifications for examples

# When running under DoFixture, metadata is inserted into
# the ArrayFixture class object by MethodTarget.

try:
    False
except:
    False = 0
    True = 1

#import copy
import types
import sys
from fit.FitException import FitException
from fit.Parse import Parse
from fit.RowFixture import RowFixtureBase
from fit import TypeAdapter
from fit import taProtocol as taPro
from fitLib import ExtendedCamelCase

class ArrayFixture(RowFixtureBase):
    adapters = [] # (typeAdapters, fieldNames) from column headers and metadata
    usedField = [] # Boolean

    def camel(self, name, kind="extended"):
        kind = kind or "extended"
        return self.mapLabel(name, kind)

    def __init__(self, col=None, typeDict=None):
        super(ArrayFixture, self).__init__(col, typeDict)
        self.actuals = []
        self.adapters = []
        self.usedField = []
        self.typeDict = typeDict
    
    def doRows(self, rows):
        self.setActualCollection()
        if rows is None:
            raise FitException, "MissingRowFailureException" # column heads missing
        if not self.actuals and not rows.more:
            return
        if not self.actuals:
            rows = rows.more
            while rows is not None:
                self.missing(rows)
                rows = rows.more
            return
        try:
            self.adapters = self.bind(rows.parts)
#            self.adapters = self.bindLabels(rows.parts)

            last = rows.last()
            rows = rows.more
            while rows is not None:
                self.doOneRow(rows, self.adapters, self.actuals)
                rows = rows.more
        except Exception, e:
            self.exception(rows.leaf(), e)
            return
        
        self.showSurplus(last)

    def showSurplus(self, last):
        if self.actuals:
            last.more = self.buildSurplusRows(self.adapters, self.actuals)
            self.mark(last.more, "surplus")

    def doOneRow(self, row, adapters, actuals):
        if not actuals:
            self.missing(row)
            return

        rowLength = row.parts.size()
        if rowLength < len(adapters):
            raise FitException, "MissingCellsFailureException"
        if rowLength > len(adapters):
            raise FitException, "ExtraCellsFailureException"
        if actuals and self.matchRow(row.parts, adapters, actuals[0]):
            del actuals[0]
        else:
            self.missing(row)

    def missing(self, row):
        row.parts.addToBody(self.label("missing"))
        self.wrong(row.parts)

    def matchRow(self, cells, adapters, objectOrDict):
        matched = False
        for adapter, name, symbols in adapters:
            if adapter is None:
                if cells.text() == "":
                    self.right(cells)
                else:
                    self.wrong(cells, "")

            else:
                text = cells.text()
                hasKey, obj = self._getObj(name, objectOrDict)
                if not hasKey:
                    match = (text == "")
                    objString = None
                else:
                    match = adapter.stringEquals(cells, obj) # was text
                    objString = adapter.toString(obj)
                if match:
                    self.right(cells)
                elif matched:
                    self.wrong(cells, objString)
                else:
                    return False
                matched = True
            cells = cells.more
        return True

    def mark(self, rows, message):
        annotation = self.label(message)
        while rows is not None:
            self.wrong(rows.parts)
            rows.parts.addToBody(annotation)
            rows = rows.more

# Surplus is being built in the wrong order.
    def buildSurplusRows(self, adapters, actuals):
        root = Parse(tag="xx")
        next = root
        for objectOrDict in actuals:
            newRow = self.buildSurplusCells(adapters, objectOrDict)
            newRowCell = Parse(tag="tr", parts=newRow)
            next.more = newRowCell
            next = newRowCell
        return root.more

    def buildSurplusCells(self, adapters, objectOrDict):
        root = Parse(tag="xx")
        next = root
        for adapter, name, symbols in adapters:
            hasKey, obj = self._getObj(name, objectOrDict)
            cell = Parse(tag="td")
            if hasKey:
                cell.body = adapter.toString(obj)
            else:
                self.exception(cell, "attribute missing")
            next.more = cell
            next = cell
        return root.more
