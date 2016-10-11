# SequenceFixture from FitLibrary
# Developed by Rick Mugridge
# copyright 2004 Rick Mugridge, University of Auckland, NZ
# Released under the terms of the GNU General Public License version 2 or later.
# Translation to Python copyright 2005 John H. Roth Jr.

# Exactly the same as DoFixture, except that actions don't have
# keywords in every second cell.

from fitLib.DoFixture import DoFixture
from fitLib import ExtendedCamelCase

class SequenceFixture(DoFixture):
    def findMethodByActionName(self, cells, args):
        actionName = cells.text()
        return self.findMethod(ExtendedCamelCase.camel(actionName), args)
