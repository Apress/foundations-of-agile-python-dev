# PrimeNumberRowFixture from Fitnesse Acceptance Tests
# copyright 2003, 2004 ObjectMentor, Inc.
# released under the terms of the GNU General Public License, version 2 or later
# Python translation copyright 2005 John H. Roth Jr.

from fit.RowFixture import RowFixture

class PrimeData:
    _typeDict = {"prime": "Int"}
    prime = 0
    def __init__(self, prime):
        self.prime = prime

class PrimeNumberRowFixture(RowFixture):
    def query(self):
        return [PrimeData(11),
                PrimeData(5),
                PrimeData(3),
                PrimeData(7),
                PrimeData(2),
                ]

    def getTargetClass(self):
        return PrimeData
