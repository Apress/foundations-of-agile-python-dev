# Common routines for Python FIT test cases
#LegalStuff jr05
# Copyright 2005 John H. Roth Jr.
# Released under the terms of the General Public License (GPL), Release 2.1 or later
# See license.txt for terms and disclaimer of all warrenties and liability.
# Last updated for Release 0.8a1
#endLegalStuff

import unittest
from fit.FitException import FitException
from fit import FitGlobal as FG

class FitTestCommon(unittest.TestCase):
    def _checkFitException(self, callable, parms, expected):
        try:
            callable(*parms)
            self.fail("No Exception Raised")
        except FitException, e:
            if e.args[0] == expected:
                return
            result = e.getMeaningfulMessage()
            if result[2] == expected:
                return
            self.fail("unexpected message in exception: '%s'" % result[2])
            return

    def _installApplicationExit(self, classObj):
        FG.RunAppConfigModule = classObj
        FG.RunAppConfig = classObj()
        FG.appConfigModule = classObj
        FG.appConfig = classObj()

