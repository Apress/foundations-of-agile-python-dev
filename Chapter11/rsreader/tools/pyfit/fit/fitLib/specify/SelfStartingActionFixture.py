# SelfStartingActionFixture from FitLibrary
# Developed by Rick Mugridge, December 28, 2004
# Copyright 2004 by Rick Mugridge, University of Auckland, NZ
# Released under the terms of the GNU General Public License version 2 or later.
# Python translation copyright 2005, John H. Roth Jr.

from fit.ActionFixture import ActionFixture
from fit.Fixture import Fixture

class SelfStartingActionFixture(ActionFixture):
    def doTable(self, table):
        self.actor = self
        Fixture.doTable(self, table)


