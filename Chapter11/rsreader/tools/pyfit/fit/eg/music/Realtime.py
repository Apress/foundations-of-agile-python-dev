# Copyright (c) 2002 Cunningham & Cunningham, Inc.
# Released under the terms of the GNU General Public License version 2 or later.
# Converted to Python 2003/07/24 by John Roth

from fit.TimedActionFixture import TimedActionFixture
from fit.ActionFixture import ActionFixture
import Simulator

class Realtime(TimedActionFixture):

    # overrides time() in TimedActionFixture
    def time(self):
        return Simulator.time / 1000.0

# !!! method names that can be called as actions have to have an
#     "_" character because of a hack needed because of a poorly
#     chosen method overload in the Java version.

    def pause_(self):
        seconds = float(self.cells.more.text())
        Simulator.delay(seconds)

    def await_(self):
        self.system("wait", self.cells.more)

    def fail_(self):
        self.system("fail", self.cells.more)

    def enter_(self):
        Simulator.delay(0.8)
        TimedActionFixture.enter_(self)

    def press_(self):
        Simulator.delay(1.2)
        TimedActionFixture.press_(self)
        
    def system(self, prefix, cell):
        functionName = self.camel(prefix + " " + cell.text()) # create method name
        try:
            getattr(Simulator, functionName)()
        except LookupError, e: # XXX probably a more specific error...
            self.exception(cell, e)


