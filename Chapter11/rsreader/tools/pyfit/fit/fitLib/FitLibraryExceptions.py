# FitLibraryExceptions; combined exceptions classes from FitLibrary
#legalStuff rm03-05 jr05
# Original version Contains code developed by Rick Mugridge.
# University of Auckland, NZ. Copyright 2003-2005 Rick Mugridge.
# Released under the terms of the General Public License (GPL), Release 2.1 or later
# See license.txt for terms and disclaimer of all warrenties and liability.
# changes Copyright 2005 John H. Roth Jr.
# Last updated for Release 0.8a1
#endLegalStuff

# These are actually the error classes from Fitnesse! I'm
# renaming the module as FitNesseExceptions, but keeping
# this version until I've got all the FitLibrary files updated.

# Thrown when there are errors within Fit itself, such as an unexpected short row.
# Gives a sensible error message and avoids a stack dump being provided.

# !!! There is a serious integration error with these exceptions (except
#     for IgnoredException! In order to work, they need to be referenced
#     by class identity in Fixture.exception (just the name won't work.)
#     However, that puts a dependency in Fixture on FitLibrary, which is
#     the wrong direction.

#     Accordingly, these exceptions are being phased out in favor of
#     FitException. FitException has keys that are the same as the
#     exception names.

__pychecker__ = 'no-classattr' # args

class FitFailureException(Exception):
    def getMessage(self):
        return self.args

class AmbiguousNameFailureException(FitFailureException):
    def __init__(self, name):
        FitFailureException.__init__(self, '"%s" is ambiguous' % name)

class ExtraCellsFailureException(FitFailureException):
    def __init__(self):
        FitFailureException.__init__(self, "Extra table cells")

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

