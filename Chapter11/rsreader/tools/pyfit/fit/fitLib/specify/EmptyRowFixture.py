# EmptyRowFixture from FitLibrary Acceptance Tests
# Developed by Rick Mugridge
# Copyright 2003 Rick Mugridge, University of Auckland, NZ
# Released under the terms of the GNU General Public License version 2 or later.
# Translation to Python copyright 2005 John H. Roth Jr.

from fit.RowFixture import RowFixture

class EmptyRowFixture(RowFixture):

    def query(self):
        return []

    def getTargetClass(self):
        return self
