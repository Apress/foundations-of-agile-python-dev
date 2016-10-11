# FixtureWithNoNullaryConstructor from FitLibrary Acceptance Tests
#legalStuff rm04 jr05
# Original version Contains code developed by Rick Mugridge.
# University of Auckland, NZ. Copyright 2004 Rick Mugridge.
# Released under the terms of the General Public License (GPL), Release 2.1 or later
# See license.txt for terms and disclaimer of all warrenties and liability.
# changes Copyright 2005 John H. Roth Jr.
# Last updated for Release 0.8a1
#endLegalStuff

from fit.Fixture import Fixture

# Fixture does not allow parameters
# "No Nullary constructor" is a javaism.
# The expected result is an exception

class FixtureWithNoNullaryConstructor(Fixture):
    def __init__(self, i):
        __pychecker__ = 'no-override'
        Fixture.__init__(self, i)
