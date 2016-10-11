# Cell Handler Inspector
#legalStuff jr05
# Copyright 2005 John H. Roth Jr.
# Released under the terms of the General Public License (GPL), Release 2.1 or later
# See license.txt for terms and disclaimer of all warrenties and liability.
# Last updated for Release 0.8a1
#endLegalStuff

from fit.Parse import Parse
from fit.Fixture import Fixture
import fit.TypeAdapter as TypeAdapter

class CellHandlerInspector(Fixture):
    def doTable(self, table):
        handlerList = TypeAdapter.getCurrentCellHandlerList()
        lastrow = table.parts
        for handler in handlerList:
            lastrow.more = Parse(tag="tr",
                    parts=Parse(tag="td", body=handler.__class__.__name__))
            lastrow = lastrow.more
