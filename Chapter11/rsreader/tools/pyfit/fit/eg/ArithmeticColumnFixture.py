"""
Python translation of fit..
which is copyright (c) 2002 Cunningham & Cunningham, Inc.
Released under the terms of the GNU General Public License version 2 or later.
"""

from fit.ColumnFixture import ColumnFixture
import math

class ArithmeticColumnFixture(ColumnFixture):
    def toRadians(self, x): return x * math.pi / 180.0
    x = 0
    y = 0
    def plus(self): return self.x + self.y
    def minus(self): return self.x - self.y
    def times(self): return self.x * self.y
    def divide(self): return self.x / self.y
    def floating(self): return float(self.x) / float(self.y)
    def sin(self): return math.sin(self.toRadians(self.x)) # let's see what the parameters are...
    def cos(self): return math.cos(self.toRadians(self.x))
    _typeDict = {"x": "Int",
                 "y": "Int",
                 "plus": "Int",
                 "minus": "Int",
                 "times": "Int",
                 "divide": "Int",
                 "floating": "Float",
                 "sin": "Float",
                 "sin.precision": 4,
                 "cos": "Float",
                 "cos.precision": 4}
