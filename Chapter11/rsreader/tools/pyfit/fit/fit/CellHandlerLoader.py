# Cell Handler Loader
# Copyright 2005 John H. Roth Jr.
# Released under the terms of the GNU General Public License, v2 or later

from fit.Parse import Parse, ParseException
from fit.Fixture import Fixture
import fit.TypeAdapter as TypeAdapter

class CellHandlerLoader(Fixture):
    def doCells(self, firstCell):
        text = firstCell.text()
        name = self.camel(text).lower()
        if name == "clear":
            TypeAdapter.clearCellHandlerList()
        elif name == "loaddefaults":
            TypeAdapter.restoreDefaultCellHandlerList()
        elif name == "load":
            secondCell = firstCell.more
            handlerName = secondCell.text()
            result = TypeAdapter.addOptionalHandlerToList(handlerName)
            if result is False:
                self.wrong(secondCell, "name not found")
            else:
                self.right(secondCell)
            # TODO - load a class from a module
            # TODO - spec test for this error
        elif name == "remove":
            secondCell = firstCell.more
            handlerName = secondCell.text()
            result = TypeAdapter.removeHandlerFromList(handlerName)
            if result is False:
                self.wrong(secondCell, "name not found")
            else:
                self.right(secondCell)

            
            