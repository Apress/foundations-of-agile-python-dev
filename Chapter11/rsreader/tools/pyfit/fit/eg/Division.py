"""
Python translation of fit..
which is copyright (c) 2002 Cunningham & Cunningham, Inc.
Released under the terms of the GNU General Public License version 2 or later.
"""

from fit.ColumnFixture import ColumnFixture

class Division(ColumnFixture):
    _typeDict={
        "numerator": "Float",
        "denominator": "Float",
        "quotient": "Float",
        "quotient.charBounds": "99",
        }
    numerator = 0.0
    denominator = 0.0
    def quotient(self):
        return self.numerator / self.denominator
