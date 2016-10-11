# Specify Tests for Combination Fixture
#LegalNotices jhr2005
#endLegalNotices

from fitLib.CombinationFixture import CombinationFixture

class TimesCombination(CombinationFixture):
    _typeDict = {"combine.types": ["Int", "Int", "Int"]}
    def combine(self, a, b):
        return a * b

class DirectCombination(TimesCombination):
    _typeDict = {"combine.types": ["Int", "Int", "Int"]}
    def __init__(self):
        super(DirectCombination, self).__init__(sut=TimesCombination())