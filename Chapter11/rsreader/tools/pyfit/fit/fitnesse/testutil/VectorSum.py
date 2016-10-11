# VectorSum from Fitnesse acceptance test utilities
# copyright 2003, 2004 object Mentor Inc.
# released under the terms of the GNU General Public License version 2 or later
# Translation to Python copyright 2005 John H. Roth Jr.

from fit.ColumnFixture import ColumnFixture

# note - Python has no Cartesian Vector class - I'm
# hacking it to make this specific test pass.

class VectorSum(ColumnFixture):
    _typeDict = {"v1": "Tuple",
                 "v1.ScalarType": "Int",
                 "v2": "Tuple",
                 "v2.ScalarType": "Int",
                 "sum": "Tuple",
                 "sum.ScalarType": "Int",
                 }

    v1 = (0, 0)
    v2 = (0, 0)
    def sum(self):
        return (self.v1[0] + self.v2[0], self.v1[1] + self.v2[1])
