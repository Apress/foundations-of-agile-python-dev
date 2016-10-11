# Constraint Fixture from Fit Library
#LegalNotices rm2005 jrpy2005
#endLegalNotices

from fit.FitException import FitException
from fit.Parse import Parse
from fitLib.CalculateFixture import CalculateFixture

# This fixture is similar to CalculateFixture except that there is
# no result column: the method result must be a boolean of either
# True (the default) or False (set by the fixture)

class ConstraintFixture(CalculateFixture):
    def __init__(self, sut=None, expected=True):
        self.expected = expected
        self.methodOK = False
        super(ConstraintFixture, self).__init__(sut)

    def bind(self, row):
        heads = row
        self.argCount = heads.size()
        argNames = ""
        while heads is not None:
            argNames += (heads.text() + " ")
            heads = heads.more
        try:
            methodName = self.camel(argNames, kind = "extended")
            self.target = self.findMethod(methodName, self.argCount)
            if self.target.getReturnType() != "Boolean":
                raise FitException("BooleanMethodFitFailureException", methodName)
            self.target.setRepeatAndExceptionString(self.repeatString, # ???
                                               self.exceptionString)
            self.methodOK = True
        except Exception, e:
            self.exception(row, e)
            return

    def doRow(self, row):
        if self.methodOK is False:
            self.ignore(row)
            return
        if row.parts is None:
            row.parts = Parse(tag="tr", body="inserted cell")
            self.exception(row.parts,
                    FitException("MissingRowFailureException"))
            return
        if row.parts.size() != self.argCount:
            self.exception(row.parts, FitException("RowIsWrongLength"))
            return
        try:
            result = bool(self.target.invokeWithCells(row.parts))
            if result is self.expected:
                self.right(row)
            else:
                self.wrong(row)
        except Exception, e:
            self.exception(row.parts, e)

