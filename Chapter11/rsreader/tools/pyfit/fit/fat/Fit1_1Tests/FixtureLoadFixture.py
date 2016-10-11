# FixtureLoadFixture from Fit 1.1 specification tests
# Copyright 2005 Jim Shore
# Released under the terms of the GNU General Public License, version 2.0 or above
# Python translation copyright 2005 John H. Roth Jr.

from fit.ColumnFixture import ColumnFixture
from fit.Fixture import Fixture

class FixtureLoadFixture(ColumnFixture):
    _typeDict = {"FixtureName": "String",
                 "LoadResult": "String",
                 "ErrorMessage": "String",
                 }

    FixtureName = ""

    def LoadResult(self):
        self._loadFixture()
        return "loaded"

    def _loadFixture(self):
        fixture = Fixture()
        fixture.loadFixture(self.FixtureName)
    
    def ErrorMessage(self):
        try:
            self._loadFixture()
            return "(none)"
        except Exception, e:
            return str(e)
        




