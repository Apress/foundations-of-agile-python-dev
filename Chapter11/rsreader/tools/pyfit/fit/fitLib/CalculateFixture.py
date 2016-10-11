# CalculateFixture from FitLibrary
# Developed by Rick Mugridge
# copyrinht 2004 Rick Mugridge, University of Auckland, NZ
# Released under the terms of the GNU General Public License version 2 or later.
# Translation to Python Copyright 2005 John H. Roth Jr.

try:
    False
except:
    False = 0
    True = 1

from fit.FitException import FitException
from fit.Utilities import em
##from fitLib.FitLibraryExceptions import MissingRowFailureException, \
##     VoidMethodFitFailureException
##from fitLib import ExtendedCamelCase
from fitLib.DoFixture import DoFixture

# A fixture similar to ColumnFixture, except that:
# o It separates the given and calculated columns by an empty column
# o It doesn't treat any strings as special by default
# o Special strings can be defined for repeats and exception-expected.
# o A single method call is made for each expected column, rather than
#   using public instance variables for the givens, as with ColumnFixture.
#   With the header row:
#       |g1 |g2 ||e1 |e2 |
#       |1.1|1.2||2.3|0.1|
#   Each row will lead to a call of the following methods with two (given)
#   double arguments:
#       e1G1G2() and e2G1G2()
# o As with DoFixture, a systemUnderTest (SUT) may be associated with the fixture
#   and any method calls not available on the fixture are called on the SUT.
# 
# See the FixtureFixture specifications for examples

class CalculateFixture(DoFixture):
    argCount = -1
    targets = []
    boundOK = False
    methods = 0
    repeatString = None
    exceptionString = None

    def __init__(self, sut=None):
        DoFixture.__init__(self, sut)
    
#    /** Defines the String that signifies that the value in the row above is
#     *  to be used again. Eg, it could be set to "" or to '"".

    def setRepeatString(self, repeat):
        self.repeatString = repeat

#    /** Defines the String that signifies that no result is expected;
#     *  instead an exception is.

    def setExceptionString(self, exceptionString):
        self.exceptionString = exceptionString;

    def doRows(self, rows):
        if rows == None:
            raise FitException("MissingRowFailureException")
        self.bind(rows.parts)
        DoFixture.doRows(self, rows.more)

    def bind(self, row):
        heads = row
        phase = 0 # 0: given 1: boundary 2: calculated 3: boundary 4: notes
        cellNumber = -1
        self.rowLength = heads.size()
        argNames = ""
        i = 0
        while heads != None:
            name = heads.text()
            cellNumber += 1
            try:
                if name == "":
                    if phase in (0, 2):
                        phase += 1

                elif phase in (1, 2):
                    if phase == 1:
                        phase = 2
                        self.argCount = cellNumber - 1
                        self.targets = []
                    methodName = self.camel(name+argNames, kind="extended")
                    target = self.findMethod(methodName, self.argCount)
                    if target.getReturnType() is None:
                        raise FitException(
                            "VoidMethodFitFailureException", methodName)
                    self.targets.append(target)
                    self.methods += 1
                    target.setRepeatAndExceptionString(self.repeatString,
                                                       self.exceptionString);
                elif phase == 0:
                    argNames += " " + name
            except Exception, e:
                self.exception(heads, e)
                return
            i += 1
            heads = heads.more

        if self.methods == 0:
            self.exception(row, FitException("NoCalculatedColumns"))
        self.boundOK = True

    def doRow(self, row):
        if not self.boundOK:
            self.ignore(row.parts)
            return

        if row.parts.size() != self.rowLength:
            self.exception(row.parts,
                           FitException("RowSBxWide", self.rowLength))
            return

        expectedCell = row.parts.at(self.argCount + 1)
        for theTarget in self.targets:
            theTarget.invokeAndCheck(row.parts, expectedCell)
            expectedCell = expectedCell.more
