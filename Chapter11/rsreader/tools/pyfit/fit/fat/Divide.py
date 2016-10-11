# Copyright (c) 2002 Cunningham & Cunningham, Inc.
# Released under the terms of the GNU General Public License version 2 or later.
# conversion to Python copyright (c) 2004 John H. Roth Jr.

from fit.ColumnFixture import ColumnFixture

class Divide(ColumnFixture):
    _typeDict = {
        "x": "Int",
        "y": "Int",
        "divide": "Int"
        }
    x = 0
    y = 0
    def divide(self):
        return self.x / self.y
