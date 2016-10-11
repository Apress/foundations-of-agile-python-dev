# Invoke all batch unit tests, not including FitLibrary
#LegalStuff jr04-06
# Copyright 2004-2006 John H. Roth Jr.
# Released under the terms of the General Public License (GPL), Release 2.1 or later
# See license.txt for terms and disclaimer of all warrenties and liability.
# Last updated for Release 0.8a1
#endLegalStuff

import os
##pathList = "\n".join(sys.path)
##print "Path List:\n%s" % pathList

import unittest

from tests import ActionFixtureTest
from tests import CellHandlerTest
from tests import CheckTest
from tests import ColumnFixtureTest
from tests import ColumnFixtureTestFixtureTest
from tests import FitExceptionTest
from tests import FitServerTest
from tests import FixtureTest
from tests import FixtureLoaderTest
from tests import FrameworkTest
from tests import MiscTest
from tests import OptionsTest
from tests import ParseTest
from tests import RowFixtureTest
from tests import RunnerImplementationTest
from tests import taProtocolTest
from tests import TypeAdapterTest
from tests import VariationsTest

def makeAllTests():
    theSuite = CellHandlerTest.makeCellHandlerTest()
    theSuite.addTests((
        ActionFixtureTest.makeActionFixtureTest(),
        CheckTest.makeCheckTest(),
        ColumnFixtureTest.makeColumnFixtureTest(),
        ColumnFixtureTestFixtureTest.makeColumnFixtureTestFixtureTest(),
        FitExceptionTest.makeFitExceptionTest(),
        FitServerTest.makeFitServerTest(),
        FixtureTest.makeFixtureTest(),
        FixtureLoaderTest.makeFixtureLoaderTest(),
        FrameworkTest.test_suite(),
        MiscTest.makeMiscTest(),
        OptionsTest.makeOptionsTest(),
        ParseTest.makeParseTest(),
        RowFixtureTest.makeRowFixtureTest(),
        RunnerImplementationTest.makeRunnerImplementationTest(),
        TypeAdapterTest.makeTypeAdapterTest(),
        taProtocolTest.makeProtocolTest(),
        VariationsTest.makeVariationsTest(),
        ))
    return theSuite

if __name__ == '__main__':
    print "current directory: '%s'" % os.getcwd()
    unittest.main(defaultTest='makeAllTests')