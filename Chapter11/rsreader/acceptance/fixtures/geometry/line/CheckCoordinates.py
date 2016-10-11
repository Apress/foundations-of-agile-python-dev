"""
Python translation of fit..
which is copyright (c) 2002 Cunningham & Cunningham, Inc.
Released under the terms of the GNU General Public License version 2 or later.
"""

from fit.ColumnFixture import ColumnFixture

class CheckCoordinates(ColumnFixture):
    _typeDict={
        "slope": "Float",
        "x": "Float",
        "intercept": "Float",
        "y": "Float",
        }
    slope = 0.0
    x = 0.0
    intercept = 0.0
    def y(self):
        return self.slope * self.x
#        return self.slope * self.x + self.intercept

