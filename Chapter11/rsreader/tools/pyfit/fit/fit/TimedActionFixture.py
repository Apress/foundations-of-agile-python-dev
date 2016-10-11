# Copyright (c) 2002 Cunningham & Cunningham, Inc.
# Released under the terms of the GNU General Public License version 2 or later.
# Converted to Python 2003/07/24 by John Roth

from fit.ActionFixture import ActionFixture
import time
from Parse import Parse

class TimedActionFixture(ActionFixture):

    ####### Traversal ////////////////////////////////

    def doTable(self, table): # extend the label row
        ActionFixture.doTable(self, table)
        table.parts.parts.last().more = self.td("time")
        table.parts.parts.last().more = self.td("split")

    def doCells(self, cells):
        start = self.time()
        ActionFixture.doCells(self, cells)
        split = self.time() - start
        cells.last().more = self.td(time.strftime("%H:%M:%S", time.localtime(start)))
        if split < 1.0:
            text = "&nbsp;"
        else:
            text = "%.1f" % (split,) # express to tenths of a second
        cells.last().more = self.td(text)

    ########## Utility ##########

    # intended to be overridden by simulator
    def time(self):
        return time.time()

    def td(self, body):
        return Parse(tag = "td", body = self.info(body))

