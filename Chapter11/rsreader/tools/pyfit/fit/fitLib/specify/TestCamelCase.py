# TestCamelCase from Acceptance Tests for FitLibrary
# Original program by Rick Mugridge
# copyright 2004 Rick Mugridge, University of Auckland, NZ
# Released under the terms of the GNU General Public License version 2 or later.
# Translation to Python copyright 2005, John H. Roth Jr.

from fitLib.CalculateFixture import CalculateFixture
from fitLib import ExtendedCamelCase 

class TestCamelCase(CalculateFixture):
    _typeDict = {"identifierName.types": ["String", "String"]}
    def identifierName(self, name):
        return ExtendedCamelCase.camel(name)
