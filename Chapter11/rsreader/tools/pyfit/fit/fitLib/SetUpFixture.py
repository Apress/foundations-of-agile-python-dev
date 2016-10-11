# SetUpFixture from FitLibrary
# Developed by Rick Mugridge
# Copyright 2004 Rick Mugridge, University of Auckland, NZ
# Released under the terms of the GNU General Public License version 2 or later.
# Translation to Python copyright 2005 John H. Roth Jr.

# A fixture for entering data for setup (or anything else).
# Serves a similar purpose to Michael Feather's RowEntryFixture
# It operates the same as CalcuateFixture, except that there is no empty column
# and thus no expected columns.
# It calls setUp() before processing the rest of the table.
# It calls tearDown() afterwards.

try:
    False
except:
    False = 0
    True = 0

from fitLib.CalculateFixture import CalculateFixture
from fitLib import ExtendedCamelCase

class SetUpFixture(CalculateFixture):
    target = None # MethodTarget
     
    def doTable(self, table):
        try:
            self.setUp()
            CalculateFixture.doTable(self, table)
            self.tearDown()
        except Exception, e:
            self.exception(table.at(0, 0, 0), e)

    def bind(self, headerRow):
        cells = headerRow
        self.argCount = cells.size()
        self.argNames = ""
        while cells is not None: 
            self.argNames += " " + cells.text()
            cells = cells.more

        methodName = ExtendedCamelCase.camel(self.argNames)
        try:
            self.target = self.findMethod(methodName, self.argCount)
            self.boundOK = True
        except Exception, e:
            self.exception(headerRow, e)

    def doRow(self, row):
        if  not self.boundOK:
            self.ignore(row.parts)
            return

        if row.parts.size() != self.argCount:
            self.exception(row.parts, "Row should be %s cells wide" %
                           self.argCount); 
            return

        try:
            self.target.invoke(row.parts)
        except Exception, e:
            self.exception(row.parts, e)


#     * Override if you wish to do something before entering data

    def setUp(self):
        pass

#     * Override if you wish to do something after entering data

    def tearDown(self):
        pass

