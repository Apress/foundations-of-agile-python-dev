# FitNesseExceptions; combined exceptions classes from FitNesse version
#  of Fit
# copyright 2003-2005 Object Mentor
# Released under the terms of the GNU General Public License version 2 or later.
# Translation to Python copyright 2005 John H. Roth Jr.

# Thrown when there are errors within Fit itself, such as an unexpected short row.
# Gives a sensible error message and avoids a stack dump being provided.

# NOTE - FitFailureException is used in TypeAdapter in exception clauses.
#  it isn't used anywhere else in core fit modules. It might be used in
#  FitLibrary and in FitNesse itself, though. None of the other classes are
#  used in the core Fit modules.

class FitFailureException(Exception):
    def getMessage(self):
        __pychecker__ = "no-classattr" # args
        return self.args

class AmbiguousNameFailureException(FitFailureException):
    def __init__(self, name):
        FitFailureException.__init__(self, '"%s" is ambiguous' % name)

class ExtraCellsFailureException(FitFailureException):
    def __init__(self):
        FitFailureException.__init__(self, "Extra table cells")

# use ParseException in Parse module instead
##class FitParseException(FitFailureException):
##    def __init__(self):
##        FitFailureException.__init__(self, str, i)

class MissingCellsFailureException(FitFailureException):
    def __init__(self):
        FitFailureException.__init__(self, "Missing table cells")

class MissingRowFailureException(FitFailureException):
    def __init__(self):
        FitFailureException.__init__(self, "Missing row")

class NoSuchFieldFailureException(FitFailureException):
    def __init__(self, name):
        FitFailureException.__init__(self,
                                     "Could not find field: %s." % name)

class VoidMethodFitFailureException(FitFailureException):
    def __init__(self, name):
        FitFailureException.__init__(self, "method %s is void" % name)

# ------------ Exceptions not derived from FitFailureException ---------

class IgnoredException(Exception):
    pass

