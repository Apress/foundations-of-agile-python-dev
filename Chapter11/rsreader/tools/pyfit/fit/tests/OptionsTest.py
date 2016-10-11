# unit tests for Options Parser.
#legalStuff jr05
# Copyright 2005 John H. Roth Jr.
# Released under the terms of the General Public License (GPL), Release 2.1 or later
# See license.txt for terms and disclaimer of all warrenties and liability.
# Last updated for Release 0.8a1
#endLegalStuff

import sys

import unittest
from fit.Options import Options
from fit.Parse import Parse
from fit import SiteOptions
from fit.Utilities import em

__pychecker__ = "no-objattrs"

try:
    False
except:
    True = 1
    False = 0

def makeOptionsTest():
    theSuite = unittest.makeSuite(Test_OptionsInstantiation, 'test')
    theSuite.addTest(unittest.makeSuite(TestOptions, 'test'))
    return theSuite

class Test_OptionsInstantiation(unittest.TestCase):
    def setUp(self):
        print '%s %s' % (self.id(), self.shortDescription())

    def testInstantiation(self):
        optList = ["FileRunner.py", "-a", "+bc"]
        optTable = {"a": ("bx", "saveOption")}
        unused = Options(optList, optTable)

class TestOptions(unittest.TestCase):
    def setUp(self):
        print '%s %s' % (self.id(), self.shortDescription())

    optList1 = ["TestRunner.py", "-v"]
##    optxxxTable1 = {"v": ["bx", "verbose"],
##                 "s": ["bx", "doSetUp"],
##                 "d": ["eo", "defaultEncoding"],
##                 "i": ["fo", "inputFile"],
##                 "o": ["fo", "inputDirectory"],
##                 "r": ["bx", "recursive"],
##                 "q": ["bx", "quietMode"],
##                 "a": ["fo", "appConfigurationModule"],
##                 "b": ["lo", "appConfigurationParms"],
##                 }

##    fitNesseOpts = {"e": ("bo", "onlyError"),
##                 "f": ("bo", "useFormattingOptions"),
##                 "h": ("bo", "HTMLOutput"),
##                 "o": ("fo", "outputDir"),
##                 "p": ("po", "pythonPath"),
##                 "r": ("bo", "rawOutput"),
##                 "v": ("bo", "verbose"),
##                 "x": ("bo", "stats"),
##                 }

    def testOneSwitchOff(self):
        optList = ["TestRunner.py", "-v"]
        obj = Options(optList, SiteOptions.TestRunner.parmDict)
        self.obj = obj
        assert obj.verbose is False
        assert obj.isValid

    def testOneSwitchOn(self):
        optList = ["TestRunner.py", "+v"]
        obj = Options(optList, SiteOptions.TestRunner.parmDict)
        self.obj = obj
        assert obj.verbose is True
        assert obj.isValid
        
    def testTwoSwitchesOn(self):
        optList = ["TestRunner.py", "+xv"]
        obj = Options(optList, SiteOptions.TestRunner.parmDict)
        self.obj = obj
        assert obj.verbose is True
        assert obj.stats is True
        assert obj.isValid
        assert len(obj.vMsgs) == 2
        assert len(obj.eMsgs) == 0

    def testTwoListItems(self):
        optList = ["TestRunner.py", "+x", "-v"]
        obj = Options(optList, SiteOptions.TestRunner.parmDict)
        self.obj = obj
        assert obj.verbose is False
        assert obj.stats is True
        assert obj.isValid
        assert len(obj.vMsgs) == 2
        assert len(obj.eMsgs) == 0

    def testFourListItems(self):
        optList = ["FolderRunner.py", "-v", "+q", "yt", "-r", "+v"]
        obj = Options(optList, SiteOptions.BatchBase.parmDict)
        self.obj = obj
        assert obj.verbose is True
        assert obj.recursive is False
        assert obj.quietMode == "yt"
        assert obj.isValid
        assert len(obj.vMsgs) == 4
        assert len(obj.eMsgs) == 0

    def testInvalidConsoleMode(self):
        optList = ["FolderRunner.py", "+q", "xx"]
        obj = Options(optList, SiteOptions.BatchBase.parmDict)
        self.obj = obj
        assert not obj.quietMode == "yn"
        assert not obj.isValid

    def testAddNewOptions(self):
        optList = ["FolderRunner.py", "-v", "+q", "et", "-r", "+v"]
        obj = Options(optList, SiteOptions.BatchBase.parmDict)
        self.obj = obj
        assert obj.recursive is False
        obj.addNewOptions(["", "+r"])
        assert obj.verbose is True
        assert obj.recursive is True
        assert obj.quietMode == "et"
        assert obj.isValid
        assert len(obj.vMsgs) == 5
        assert len(obj.eMsgs) == 0

    def testInvalidEncodingOption(self):
        optList = ["FileRunner.py", "+d", "enigma"]
        obj = Options(optList, SiteOptions.BatchBase.parmDict)
        self.obj = obj
        assert not obj.isValid
        assert obj.defaultEncoding == ""

    def testPositionalParameters(self):        
        optList = ["TestRunner.py", "-v", "great file"]
        obj = Options(optList, SiteOptions.TestRunner.parmDict)
        self.obj = obj
        assert obj.isValid
        assert len(obj.posParms) == 1
        assert obj.posParms[0] == "great file"

    def testOptionError(self):
        optList = ["TestRunner.py", "-$"]
        obj = Options(optList, SiteOptions.TestRunner.parmDict)
        self.obj = obj
        assert not obj.isValid
        assert len(obj.eMsgs) == 1
        assert obj.eMsgs[0].startswith("Parameter $ not recognized")

    def testApplicationConfigurationParms(self):
        optList = ["FileRunner.py", "-a", "AppModule.py",
                   "-b", "foo", "-v", "+b", "bar"]
        obj = Options(optList, SiteOptions.BatchBase.parmDict)
        print dir(obj)
        self.obj = obj
        assert obj.appConfigurationModule == "AppModule.py"
        assert obj.appConfigurationParms == ["foo", "bar"]
        assert obj.verbose is False

    def testInvalidRunner(self):
        optList = ["NotARunner.py", "-a", "AppModule.py",
                   "-b", "foo", "-v", "+b", "bar"]
        obj = Options(optList, SiteOptions.BatchBase.parmDict)
        print dir(obj)
        self.obj = obj
        assert obj.appConfigurationModule == "AppModule.py"
        assert obj.appConfigurationParms == ["foo", "bar"]
        assert obj.verbose is False

    def tearDown(self):
        obj = self.obj
        print SiteOptions.BatchBase.parmDict.keys()
        print SiteOptions.TestRunner.parmDict.keys()
        if not obj.eMsgs and not obj.vMsgs:
            print "--- No messages ---"
        else:
            if obj.eMsgs:
                print "------ Error Messages  ------"
                for msg in obj.eMsgs:
                    print msg
            if obj.vMsgs:
                print "---- Validation Messages ----"
                for msg in obj.vMsgs:
                    print msg

if __name__ == '__main__':
    unittest.main(defaultTest='makeOptionsTest')
