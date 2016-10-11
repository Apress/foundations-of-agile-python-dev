# SubetFixtureUnderTest from FitLibrary Specification Tests
# Developed by Rick Mugridge
# Copyright 2004 Rick Mugridge, University of Auckland, NZ
# Released under the terms of the GNU General Public License version 2 or later.
# Translation to Python copyright 2005 John H. Roth Jr.

from fitLib.SubsetFixture import SubsetFixture
from fitLib.specify.CamelRowFixtureUnderTest import CamelRowFixtureUnderTest

class SubsetFixtureUnderTest(SubsetFixture):
    def __init__(self):
        super(SubsetFixtureUnderTest, self).__init__(
            CamelRowFixtureUnderTest().query())

    def getTargetClass(self):
        return CamelRowFixtureUnderTest
