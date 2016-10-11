# Complex Add Fixture for TestArraysInColumnFixture Acceptance Test
# Copyright 2004 John H. Roth Jr.
# Released under GNU Public License v2. See License.txt for general disclaimer
# of liability and warrentys.

from fit.ColumnFixture import ColumnFixture

class ComplexAddFixture(ColumnFixture):
    _typeDict = {
        "a": "List",
        "a.ScalarType": "Int",
        "b": "List",
        "b.ScalarType": "Int",
        "sum": "List",
        "sum.ScalarType": "Int",
        }
    a = [0, 0]
    b = [0, 0]
    def sum(self):
        return [self.a[0] + self.b[0], self.a[1] + self.b[1]]