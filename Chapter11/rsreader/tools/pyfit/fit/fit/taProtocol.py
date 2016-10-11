# Type Adapter Protocols for PyFit
# copyright 2005, John H. Roth Jr.
# Released under the terms of the GNU Public License, Version 2.
# See license.txt for conditions and exclusion of all warrenties.

import sys
import types
from fit.FitException import FitException
from fit.Parse import Parse
from fit.taTable import _isApplicationProtocol
from fit.Utilities import em

def getProtocolFor(typeAdapter):
    __pychecker__ = "no-returnvalues"
    if _isApplicationProtocol(typeAdapter):
        return ApplicationProtocol(typeAdapter)
    if not hasattr(typeAdapter, "fitAdapterProtocol"):
        return BasicProtocol(typeAdapter)
    if typeAdapter.fitAdapterProtocol == "Basic":
        return BasicProtocol(typeAdapter)
    if typeAdapter.fitAdapterProtocol == "EditedString":
        return EditedStringProtocol(typeAdapter)
    if typeAdapter.fitAdapterProtocol == "RawString":
        return RawStringProtocol(typeAdapter)
    if typeAdapter.fitAdapterProtocol == "CellAccess":
        return CellAccessProtocol(typeAdapter)
    raise FitException, ("UnknownProtocol", typeAdapter.fitAdapterProtocol)

class ProtocolBase(object):
    def __init__(self, typeAdapter):
        self.adapter = typeAdapter
        self.ta = typeAdapter

class BasicProtocol(ProtocolBase):
    protocolName = "Basic"        

    def parse(self, cell):
        if isinstance(cell, Parse):
            return self.ta.parse(cell.text())
        return self.ta.parse(cell)

    def equals(self, cell, obj):
        if isinstance(cell, Parse):
            return self.ta.equals(self.parse(cell.text()), obj)
        if isinstance(cell, types.StringTypes):
            return self.ta.equals(self.parse(cell), obj)
        return self.ta.equals(cell, obj)

    def toString(self, obj, cell=None):
        __pychecker__ = "no-argsused" # cell
        return self.ta.toString(obj)

class EditedStringProtocol(ProtocolBase):
    protocolName = "EditedString"        

    def parse(self, cell):
        if isinstance(cell, Parse):
            return self.ta.parse(cell.text())
        return self.ta.parse(cell)

    def equals(self, cell, obj):
        if isinstance(cell, Parse):
            return self.ta.equals(cell.text(), obj)
        if isinstance(cell, types.StringTypes):
            return self.ta.equals(cell, obj)
        return self.ta.equals(self.ta.toString(cell), obj)

    def toString(self, obj, cell=None):
        __pychecker__ = "no-argsused" # cell
        return self.ta.toString(obj)

class RawStringProtocol(ProtocolBase):
    protocolName = "RawString"        

    def parse(self, cell):
        if isinstance(cell, Parse):
            return self.ta.parse(cell.body)
        return self.ta.parse(cell)

    def equals(self, cell, obj):
        if isinstance(cell, Parse):
            return self.ta.equals(cell.body, obj)
        if isinstance(cell, types.StringTypes):
            return self.ta.equals(cell, obj)
        return self.ta.equals(self.ta.toString(cell), obj)

    def toString(self, obj, cell=None):
        __pychecker__ = "no-argsused" # cell
        return self.ta.toString(obj)

class CellAccessProtocol(ProtocolBase):
    protocolName = "CellAccess"

    def parse(self, cell):
        if isinstance(cell, Parse):
            return self.ta.parse(cell)
        raise FitException, ("CellAccessMissingCell",)

    def equals(self, cell, obj):
        if isinstance(cell, Parse):
            return self.ta.equals(cell, obj)
        raise FitException, ("CellAccessMissingCell",)

    def toString(self, obj, cell=None):
        if isinstance(cell, Parse):
            return self.ta.toString(obj, cell)
        raise FitException, ("CellAccessMissingCell",)

class ApplicationProtocol(ProtocolBase):
    protocolName = "ApplicationObject"        

    def parse(self, cell):
        if isinstance(cell, Parse):
            return self.ta(cell.text())
        return self.ta(cell)

    def equals(self, cell, other):
        if isinstance(cell, Parse):
            obj = self.ta(cell.text())
        elif isinstance(cell, types.StringTypes):
            obj = self.ta(cell)
        else:
            obj = cell
        return obj == other

    def toString(self, obj, cell=None):
        __pychecker__ = "no-argsused" # cell
        return str(obj)
