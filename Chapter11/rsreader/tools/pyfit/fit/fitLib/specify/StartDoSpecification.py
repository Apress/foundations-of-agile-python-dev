# StartDoSpecification from Acceptance Tests for FitLibrary
#legalStuff rm04 jr05-06
# Original version Contains code developed by Rick Mugridge.
# University of Auckland, NZ. Copyright 2004 Rick Mugridge.
# Released under the terms of the General Public License (GPL), Release 2.1 or later
# See license.txt for terms and disclaimer of all warrenties and liability.
# changes Copyright 2005-2006 John H. Roth Jr.
# Last updated for Release 0.8a1
#endLegalStuff

# This seems to be the starting point for DoFixture Specification tests.
# It's included in a SetUp.html file that should get inserted at the start
# of all of the other files.

from fit.Fixture import Fixture
from fitLib.specify.SystemUnderTest import SystemUnderTest

class StartDoSpecification(Fixture):
    SUT = None

    def __init__(self):
        Fixture.__init__(self)
        self.SUT = SystemUnderTest()

