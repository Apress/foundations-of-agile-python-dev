# FailConstraint subclass of ConstraintFixture
#LegalNotices rm2005 jrpy2005
#endLegalNotices

from fitLib.ConstraintFixture import ConstraintFixture

class FailConstraint(ConstraintFixture):
    _typeDict = {"bA.types": ["Boolean", "Int", "Int"],
                 }

    def __init__(self):
        super(FailConstraint, self).__init__(expected=False)

    def bA(self, b, a):
        return a < b

