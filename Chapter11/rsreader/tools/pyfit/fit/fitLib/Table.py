# Table support module for Fit Library
#legalStuff rm04 jr05
# Original version Contains code developed by Rick Mugridge.
# University of Auckland, NZ. Copyright 2004 Rick Mugridge.
# Released under the terms of the General Public License (GPL), Release 2.1 or later
# See license.txt for terms and disclaimer of all warrenties and liability.
# changes Copyright 2005 John H. Roth Jr.
# Last updated for Release 0.8a1
#endLegalStuff

import sys
import types
from fit.FitException import FitException
from fit.Parse import Parse
from fit.Utilities import em

# marker interface
class TableInterface(object):
    def toTable(self): pass
    def toString(self): pass

class TableTypeAdapter(object):
    fitAdapterProtocol = "CellAccess"

    def parse(self, aCell):
        if isinstance(aCell, Parse):
            if aCell.parts:
                return Table(aCell.parts)
            raise FitException, ("MissingTable")
        if isinstance(aCell, types.StringTypes):
            if aCell.body.lower().find("<table") != -1:
                return Table(aCell)
        raise FitException, ("MissingTable")

    def toString(self, aTable, aCell):
        if not isinstance(aTable, TableInterface):
            return "null"
        if not isinstance(aCell, Parse):
            raise FitException, ("CellAccessMissingCell")
        aCell.body = ""
        aCell.parts = aTable._parse
        return aTable.toString()

    def equals(self, aCell, aTable):
        if aCell is None:
            return aTable is None
        if not isinstance(aCell, Parse):
            return False
        if not isinstance(aTable, Table):
            return False
        return aCell.parts == aTable._parse

class Table(TableInterface):
    _parse = None # Parse

    def __init__(self, parse):
        if isinstance(parse, types.StringTypes):
            self._parse = Parse(parse)
        elif isinstance(parse, Parse):
            self._parse = parse

    def tableAt(self, i, j, k):
        at = self._parse.at(i, j, k).parts
        return Table(at)

    def stringAt(self, i, j, k):
        p2 = self._parse.at(i, j, k)
        if p2.parts or not p2.body:
            return "null"
        return p2.text()

    def toTable(self):
        return self

    def parseTable(parse):
        return Table(parse)
    parseTable = staticmethod(parseTable)

    def equals(expected, actual):
        if expected is None:
            return actual is None
        return expected == actual
    equals = staticmethod(equals)

    def __eq__(self, other):
        if not isinstance(other, Table):
            return False
        return self._parse == other._parse

    def __ne__(self, other):
        if isinstance(other, Table):
            return False
        return self._parse != other._parse

    def toString(self):
        return self._parse.toString()

    def __str__(self):
        return str(self._parse)
