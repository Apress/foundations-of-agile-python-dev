# SucceedConstraint subclass of ConstraintFixture
#LegalNotices rm2005 jrpy2005
#endLegalNotices

from fitLib.ConstraintFixture import ConstraintFixture

class SucceedConstraint(ConstraintFixture):
    _typeDict = {"aB.types": ["Boolean", "Int", "Int"],
                 "bC.types": ["Boolean", "Int", "Int"],
                 }

    def aB(self, a, b):
        return a < b

    def bC(self, b, c):
        return b + c
