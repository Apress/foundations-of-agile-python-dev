# ActionFixture, from core FIT
#LegalStuff cc02 sm02 jr03-05
# Original Java version Copyright 2002 Cunningham and Cunningham, Inc.
# Released under the terms of the General Public License (GPL), Release 2.1 or later
# See license.txt for terms and disclaimer of all warrenties and liability.
# Original translation to Python Copyright 2002 Simon Michael
# changes Copyright 2003-2005 John H. Roth Jr.
# Last updated for Release 0.8a1
#endLegalStuff

"""
Python translation of fit..
which is copyright (c) 2002 Cunningham & Cunningham, Inc.
Released under the terms of the GNU General Public License version 2 or later.
"""

# import re
import time
from fit.FitException import FitException, raiseIf, raiseIfNone
from fit.Fixture import Fixture
from fit.Parse import Parse
from fit.TypeAdapter import on as TypeAdapter

class ActionFixture(Fixture):
    cells = None
    actor = None

    ## Traversal ################################

    def doCells(self, cells):
        self.cells = cells
        command = cells.text()
        method = getattr(self, command+"_", None)
        if method is None:
            self.exception(cells, FitException("InvalidCommand", command))
            return 
        try:
            method()
        except Exception, e:
            self.exception(cells, e)
        
    ## Actions ##################################

    def getAdapter(self, cell):
        raiseIfNone(cell, "missingMethodNameCell")
        methodName = self.camel(cell.text())
        raiseIf(methodName == "", "missingMethodName")
        raiseIfNone(self.actor, "missingActor")
        try:
            adapter = TypeAdapter(self.actor, methodName)
        except Exception, ex:
            self.exception(cell, ex)
            raise FitException("IgnoreException")
        return adapter

    def start_(self):
        methodNameCell = self.cells.more
        raiseIfNone(methodNameCell, "missingActorNameCell")
        path = methodNameCell.text()
        raiseIf(path == "", "ActionStart")
        # ??? must be a fixture. Why?
        try:
            theClass = self.loadFixture(path)
            ActionFixture.actor = theClass()
        except Exception, e:
            self.exception(methodNameCell, e)

    def enter_(self):
        adapter = self.getAdapter(self.cells.more)
        raiseIfNone(self.cells.more.more, "missingDataCell")
        self.parseAndSet(self.cells.more.more, adapter)

    # !!! Methods using this routine need metadata as of 0.8
    #     Really need a way of declaring a parameterless method that
    #     returns None
    def press_(self):
        methodNameCell = self.cells.more
        adapter = self.getAdapter(methodNameCell)
        try:
            adapter.invoke()
##            self.right(methodNameCell) # makes acc test fail.
        except Exception, e:
            self.exception(methodNameCell, e)

    def check_(self):
        adapter = self.getAdapter(self.cells.more)
        raiseIfNone(self.cells.more.more, "missingDataCell")
        self.check(self.cells.more.more, adapter)
