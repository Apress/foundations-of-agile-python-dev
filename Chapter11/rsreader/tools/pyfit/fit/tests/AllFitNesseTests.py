# Invoke all batch unit tests, not including FitLibrary or FitServer
# copyright 2004 John H. Roth Jr. Licensed under the GNU General Public License, v2.
# See license.txt for details, and for the disclaimer of liability and warrenty.

import os
import sys
pathList = "\n".join(sys.path)
print "Path List:\n%s" % pathList

import unittest
from tests import FitServerTest

try:
    False
except:
    True = 1
    False = 0

def makeAllTests():
    theSuite = FitServerTest.makeFitServerTest()
    return theSuite

if __name__ == '__main__':
    print "current directory: '%s'" % os.getcwd()
    unittest.main(defaultTest='makeAllTests')
