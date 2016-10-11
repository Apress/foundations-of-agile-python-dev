# SubsetFixture from FitLibrary
# Developed by Rick Mugridge
# Copyright 2004 Rick Mugridge, University of Auckland, NZ
# Released under the terms of the GNU General Public License version 2 or later.
# Translation to Python copyright 2005 John H. Roth Jr.

from fitLib.SetFixture import SetFixture

# Like SetFixture, except that it ignores any surplus, unmatched elements in the
# actual collection. That is, the table specifies an expected subset.

class SubsetFixture(SetFixture):
    def showSurplus(self, last):
        pass
