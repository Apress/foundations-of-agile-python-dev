# test module for Fit Server
#legalStuff jr04-05
# Copyright 2004-2005 John H. Roth Jr.
# Released under the terms of the General Public License (GPL), Release 2.1 or later
# See license.txt for terms and disclaimer of all warrenties and liability.
# Last updated for Release 0.8a1
#endLegalStuff

import copy
import os
import sys
import types
import unittest as ut

from fit.Counts import Counts
from fitnesse import FitServerImplementation as fsi
from fit.InitEnvironment import FG, setupFitGlobalForTests
from fit.FitGlobal import FileSystemAdapter
from fit.Options import Options
from tests.RunnerTestCommon import VirtualFileSystem, MockFileObject
from tests.RunnerTestCommon import ioMock, ft2chunk1
from fit import SiteOptions
from fit.Utilities import em

try:
    False
except:
    True = 1
    False = 0

def makeFitServerTest():
    theSuite = ut.makeSuite(Test_FitServer, 'Test')
    theSuite.addTest(ut.makeSuite(TestPythonPath, 'should'))
    theSuite.addTest(ut.makeSuite(Test_TestRunnerInitialization, 'test'))
    theSuite.addTest(ut.makeSuite(Test_TestRunner, 'test'))
    theSuite.addTest(ut.makeSuite(TestStatsHandler, "test"))
    theSuite.addTest(ut.makeSuite(TestOutputFileHandling, "should"))
    theSuite.addTest(ut.makeSuite(SpecifyListOfFiles, "should"))
    return theSuite

class Test_FitServer(ut.TestCase):
    def setUp(self):
        print '%s %s' % (self.id(), self.shortDescription())
        setupFitGlobalForTests("FitNesseOnline")
        if isinstance(fsi.conMsg, types.StringTypes):
            em("conMsg corrupt. %s" % fsi.conMsg)
        self.savePythonPath = copy.copy(sys.path)
        self.saveNet = fsi.net
        fsi.netIn = fsi.netOut = fsi.net = ioMock()
        self.saveMsg = fsi.conMsg
        fsi.conMsg = fsi.TestMsgWriter()
        self.fits = fsi.FitServer()

    def tearDown(self):
        sys.path[:] = self.savePythonPath
        fsi.conMsg.logToStdout(self.id())
        fsi.conMsg = self.saveMsg
        fsi.netIn = fsi.netOut = fsi.net = self.saveNet
        setupFitGlobalForTests("FitNesseOnline")

    args1 = ["fit/FitServer.py",
             "aPathExpression",
             "localhost",
             "8080",
             "314159616",
             ]

    def Test_args1(self):
        fits = self.fits
        io = fsi.net
        assert fits.args(self.args1), "invoke args"
        assert fits.options.verbose is False, "test verbose flag"
        assert io.host == "localhost", "test host name"
        assert io.port == 8080, "test port number"
        assert io.socketToken == 314159616, "Test socket token"

    args2 = ["fit/FitServer.py",
             "aPathExpression",
             "localhost",
             "8080",
             "314159616",
             "an extra parameter"]

    def Test_args2(self):
        fits = self.fits
        assert fits.args(self.args2) is False

    args3 = ["fit/FitServer.py",
             "+v",
             "the pathless path",
             "remotehost",
             "9090",
             "217",
             ]

    def Test_args3(self):
        fits = self.fits
        io = fsi.net
        result = fits.args(self.args3)
        print "after arg processing. verbose: '%s'" % fits.options.verbose
        assert result
        assert fits.options.verbose
        assert io.host == "remotehost"
        assert io.port == 9090
        assert io.socketToken == 217

    args4 = ["fit/FitServer.py",
             "-w",
             "aPathExpression",
             "localhost",
             "8080",
             "314159616"
             ]

    def Test_args4(self):
        fits = self.fits
        assert fits.args(self.args4) is False

    args5 = ["fit/FitServer.py",
             "+v",
             "localhost",
             "8O8O",
             "314159616"
             ]

    def TestIntEditErrorMessage(self):
        fits = self.fits
        assert fits.args(self.args5) is False
        msgs = "\n".join(fsi.conMsg.msgs)
        assert msgs.find("'Port Number' must be an integer") != -1

    def TestBadArgsInRun(self):
        fits = self.fits
        fsi.net.inputList = self.fulltest1
        result = fits.run(self.args5)
        print "-------------- output list ----------------"
        print "\n".join(fsi.net.outputList)
        assert result is False

    ft1chunk1 = ("TestProcess1\n<html><head><title>fubar</title></head>"
                 "<body><table><tr><td>fit.PrimitiveFixture</td></tr></table>"
                 "</body></html>\r\n"
                 )

    fulltest1 = ["0000000000",
                 "%010i" % len(ft1chunk1),
                 ft1chunk1,
                 "0000000000"
                 ]

    def Test_process1(self):
        fits = self.fits
        fsi.net.inputList = self.fulltest1
        result = fits.run(self.args3)
        print "fits.run(arg3): %s" % result
        print "-------------- output list ----------------"
        print "\n".join(fsi.net.outputList)
        assert result == 0

    def TestIOErrorOnOutputHandler(self):
        fits = self.fits
        fsi.net.inputList = self.fulltest1
        fsi.net.setErrorOnWrite(1)
        try:
            result = fits.run(self.args3)
        except IOError:
            pass
        except:
            raise
        print "fits.run(arg3): %s" % result
        print "-------------- output list ----------------"
        print "\n".join(fsi.net.outputList)
        assert result == 0

    def TestIOErrorOnOutputHandler2(self):
        fits = self.fits
        fsi.net.inputList = self.fulltest1
        fsi.net.setErrorOnWrite(5)
        try:
            result = fits.run(self.args3)
        except IOError:
            pass
        except:
            raise
        print "fits.run(arg3): %s" % result
        print "-------------- output list ----------------"
        print "\n".join(fsi.net.outputList)
        assert result == 0


    ftMalformedHTML = ("MalformedHTML\n<html><head><title>fubar</title></head>"
                 "<body><table>\r\n"
                 )

    fullMalformedHTML = ["0000000000",
                 "%010i" % len(ftMalformedHTML),
                 ftMalformedHTML,
                 "0000000000"
                 ]

    def TestDocumentWithMalformedHTML(self):
        fits = self.fits
        fsi.net.inputList = self.fullMalformedHTML
        result = fits.run(self.args3)
        print "fits.run(arg3): %s" % result
        print "-------------- output list ----------------"
        print "\n".join(fsi.net.outputList)
        assert result != 0

    fullTruncatedProtocolHeader = ["0000000000",
                 "0098765" 
                 ]

    def TestDocumentWithTruncatedProtocolHeader(self):
        fits = self.fits
        fsi.net.inputList = self.fullTruncatedProtocolHeader
        result = fits.run(self.args3)
        print "fits.run(arg3): %s" % result
        print "-------------- output list ----------------"
        print "\n".join(fsi.net.outputList)
        assert result != 0

    ftInvalidConnectionMsg = "Invalid Connection Test Message"

    fullInvalidConnection = [
                 "%010i" % len(ftInvalidConnectionMsg),
                 ftInvalidConnectionMsg,
                 "0000000000"
                 ]

    def TestInvalidConnection(self):
        fits = self.fits
        fsi.net.inputList = self.fullInvalidConnection
        try:
            result = fits.run(self.args3)
        except SystemExit, e:
            result = e.args
        except:
            raise
        print "fits.run(arg3): %s" % result
        print "-------------- output list ----------------"
        print "\n".join(fsi.net.outputList)
        assert result != 0


    ftNoReturn = ("<html><head><title>fubar</title></head>"
                 "<body><table><tr><td>fit.PrimitiveFixture</td></tr></table>"
                 "</body></html>"
                 )

    fullNoReturn = ["0000000000",
                 "%010i" % len(ftNoReturn),
                 ftNoReturn,
                 "0000000000"
                 ]

    def TestDocumentWithNoReturn(self):
        fits = self.fits
        fsi.net.inputList = self.fullNoReturn
        result = fits.run(self.args3)
        print "fits.run(arg3): %s" % result
        print "-------------- output list ----------------"
        print "\n".join(fsi.net.outputList)
        assert result != 0

    ft2chunk1head = ("""TestProcess2\n
<!doctype html public "-//w3c//dtd html 4.0 transitional//en">
<html>
<head>
   <meta http-equiv="Content-Type" content="text/html; charset=iso-8859-1">
   <meta name="Author" content="Ward Cunningham">
   <meta name="GENERATOR" content="Mozilla/4.5 [en]C-CCK-MCD compaq  (Win98; U) [Netscape]">
   <title>Arithmetic</title>
</head>
<body>
""")

    ft2chunk1body = ft2chunk1head + ft2chunk1
    fulltest2 = ["0000000000",
                 "%010i" % len(ft2chunk1body),
                 ft2chunk1body,
                 "0000000000",
                 ]

    def Test_process2(self):
        fits = self.fits
        fsi.net.inputList = self.fulltest2
        result = fits.run(self.args3)
        print "-------------- output list ----------------"
        print "\n".join(fsi.net.outputList)
        assert result == 10 # 9 wrong, 1 exception

    ft2Doc1 = ("Two Doucments 1\n"
               "<html><head><title>Two Documents 1</title></head>"
               "<body><table><tr><td>fit.PrimitiveFixture</td></tr></table>"
               "</body></html>\r\n"
               )

    ft2Doc2 = ("Two Documents 2\n"
               "<html><head><title>Two Documents 2</title></head>"
               "<body><table><tr><td>fit.PrimitiveFixture</td></tr></table>"
               "</body></html>\r\n"
               )

    full2Docs = ["0000000000",
                 "%010i" % len(ft2Doc1),
                 ft2Doc1,
                 "%010i" % len(ft2Doc2),
                 ft2Doc2,
                 "0000000000",
                 ]

    def Test2Documents(self):
        fits = self.fits
        fsi.net.inputList = self.full2Docs
        result = fits.run(self.args3)
        print "fits.run(arg3): %s" % result
        print "-------------- output list ----------------"
        print "\n".join(fsi.net.outputList)
        assert result == 0

class TestPythonPath(ut.TestCase):
    def setUp(self):
        print '%s %s' % (self.id(), self.shortDescription())
        setupFitGlobalForTests("FitNesseOnline")
        self.savePath = copy.copy(sys.path)
        self.fits = fsi.ServerBase()
        self.options = Options(["fubar"], SiteOptions.FitServer.parmDict)
        self.saveNet = fsi.net
        fsi.netIn = fsi.netOut = fsi.net = ioMock()
        self.saveMsg = fsi.conMsg
        fsi.conMsg = fsi.TestMsgWriter()

    def tearDown(self):
        sys.path[:] = self.savePath
        fsi.conMsg.logToStdout(self.id())
        fsi.conMsg = self.saveMsg
        fsi.netIn = fsi.netOut = fsi.net = self.saveNet
        setupFitGlobalForTests("FitNesseOnline")

    def _buildPathStringForTest(self, aList):
        return os.pathsep.join(aList)

    def shouldDiscardJavaStuff(self):
        fits = self.fits
        opts = self.options
        expected = "aDirectory"
        path, rename = fits.extractPythonPath(
            self._buildPathStringForTest(["classes", "foo.jar",
                                          "spam.txt", expected]), opts)
#            "classes;foo.jar;spam.txt;aDirectory", opts)
        assert path == [expected]
        assert rename == "spam.txt"

    def shouldAcceptSym(self):
        fits = self.fits
        opts = self.options
        path, rename = fits.extractPythonPath(
            self._buildPathStringForTest(["sym.sam.sym", "foo.bar.sym",
                                          "spam.eggs.sym"]), opts)
  #          "sym.sam.sym;foo.bar.sym;spam.eggs.sym", opts)
        assert opts.runLevelSymbols == ["sym.sam", "foo.bar", "spam.eggs"]

    def shouldAcceptDiagOpts(self):
        fits = self.fits
        opts = self.options
        path, rename = fits.extractPythonPath(
              self._buildPathStringForTest(["sym.True", "foo.False",
                                          "spam.z"]), opts)
#          "sym.True;foo.False;spam.z", opts)
        assert opts.diagnosticOptions == ["sym.True", "foo.False", "spam.z"]

    def shouldAcceptSpecificationLevel(self):
        fits = self.fits
        opts = self.options
        path, rename = fits.extractPythonPath(
            "fubar.std", opts)
        assert opts.standardsLevel == "fubar"        

    def shouldAcceptApplicationConfiguration(self):
        fits = self.fits
        opts = self.options
        path, rename = fits.extractPythonPath(
            self._buildPathStringForTest(["aparm.parm", "app.py",
                                          "bparm.parm"]), opts)
#            "aparm.parm;app.py;bparm.parm", opts)
        assert opts.appConfigurationModule == "app.py"
        assert opts.appConfigurationParms == ["aparm", "bparm"]

class Test_TestRunnerInitialization(ut.TestCase):
    def setUp(self):
        print '%s %s' % (self.id(), self.shortDescription())
        setupFitGlobalForTests("FitNesseBatch")
        self.saveMsg = fsi.conMsg
        fsi.conMsg = fsi.TestMsgWriter()

    def tearDown(self):
        fsi.conMsg.logToStdout(self.id())
        fsi.conMsg = self.saveMsg
        setupFitGlobalForTests("FitNesseBatch")

    def _joinPath(self, *parts):
        return os.path.join(*parts)

    def testInstantiation(self):
        fsi.TestRunner()

    def testParms1(self):
        trun = fsi.TestRunner()
        assert trun.args(["TestRunner.py",
                          "+v",
                          "localhost",
                          "8080",
                          "AGreatTestPage"])
        self._checkParmSettings(trun, True, None, False, False, False, None)
        
    def testParms2(self):
        trun = fsi.TestRunner()
        assert trun.args(["TestRunner.py", "+vr",
                          "-o", self._joinPath("fat", "Reports"),
                          "localhost",
                          "8080",
                          "AGreatTestPage"])
        self._checkParmSettings(trun, True, None, True, True, True, None)

    def testInvalidParms(self):
        trun = fsi.TestRunner()
        assert not trun.args(["TestRunner.py", "+vrw",
                          "-o", self._joinPath("fat", "Reports"),
                          "localhost",
                          "8080",
                          "AGreatTestPage"])

    def testTooManyPosParms(self):
        trun = fsi.TestRunner()
        assert not trun.args(["TestRunner.py", "+vr",
                          "-o", self._joinPath("fat", "Reports"),
                          "localhost",
                          "8080",
                          "AGreatTestPage",
                          "An Extra Parm"])

    def testTooFewPosParms(self):
        trun = fsi.TestRunner()
        assert not trun.args(["TestRunner.py", "+vr",
                          "-o", self._joinPath("fat", "Reports"),
                          "localhost",
                          "8080",])

    def _checkParmSettings(self, trun, v, unused, r, h, o, dummy):
        assert trun.options.verbose is v
        assert trun.options.rawOutput is r
        assert trun.options.HTMLOutput is h, (
            "expected: %s actual: %s" % (h, trun.options.HTMLOutput))
        assert (trun.options.outputDir != "" )is o

class Test_TestRunner(ut.TestCase):
    def setUp(self):
        print '%s %s' % (self.id(), self.shortDescription())
        setupFitGlobalForTests("FitNesseBatch")
        self.savePath = copy.copy(sys.path)
        self.saveMsg = fsi.conMsg
        fsi.conMsg = fsi.TestMsgWriter()
        self.trun = fsi.TestRunner()
        fsi.netIn = fsi.netOut = fsi.net = ioMock()
        FG.fsa = VirtualFileSystem()
        FG.fsa._addDirectories("tests/testout")

    def tearDown(self):
        sys.path[:] = self.savePath
        fsi.conMsg.logToStdout(self.id())
        fsi.conMsg = self.saveMsg
        fsi.netIn = fsi.netOut = fsi.net = fsi.FitNesseNetworkInterface()
        FG.fsa = FileSystemAdapter()
        setupFitGlobalForTests("FitNesseBatch")

    ft1chunk1 = ("A Great Test Page\n"
                 "<table><tr><td>fit.PrimitiveFixture</td></tr></table>"
                 "\r\n"
                 )

    fulltest1 = ["0000000000",
                 "%010i" % len(ft1chunk1),
                 ft1chunk1,
                 "0000000000"
                 ]

    args3 = ["foo/bar/TestRunner.py",
             "-vr",
             "-o",
             "tests/testout",
             "+p", "fubar",
             "localhost",
             "8080",
             "AGreatTestPage"]    

    def test_process1(self):
        trun = self.trun
        fsi.netIn.inputList = self.fulltest1
        result = trun.run(self.args3)
        print "-------------- output list ----------------"
        print "\n".join(fsi.netOut.outputList)
        assert result

# full test # 2

    ft2chunk1head = "Another Fine Test\n"

    ft2chunk1all = ft2chunk1head + ft2chunk1

    fulltest2 = ["0000000000",
                 "%010i" % len(ft2chunk1all),
                 ft2chunk1all,
                 "0000000000",
                 ]

    args4 = ["TestRunner.py",
             "-vrh",
             "-o", "tests/testout",
             "+p", "fubar",
             "localhost",
             "8080",
             "AnotherGreatTestPage"]    


    def test_process2(self):
        trun = self.trun
        fsi.netIn.inputList = self.fulltest2
        result = trun.run(self.args4)
        print "-------------- output list ----------------"
        print "\n".join(fsi.netOut.outputList)
        assert result

    ft2Doc1 = ("Two Doucments 1\n"
               "<html><head><title>Two Documents 1</title></head>"
               "<body><table><tr><td>fit.PrimitiveFixture</td></tr></table>"
               "</body></html>\r\n"
               )

    ft2Doc2 = ("Two Documents 2\n"
               "<html><head><title>Two Documents 2</title></head>"
               "<body><table><tr><td>fit.PrimitiveFixture</td></tr></table>"
               "</body></html>\r\n"
               )

    full2Docs = ["0000000000",
                 "%010i" % len(ft2Doc1),
                 ft2Doc1,
                 "%010i" % len(ft2Doc2),
                 ft2Doc2,
                 "0000000000",
                 ]

    def test2Documents(self):
        trun = self.trun
        fsi.netIn.inputList = self.full2Docs
        result = trun.run(self.args3)
        print "trun.run(arg3): %s" % result
        print "-------------- output list ----------------"
        print "\n".join(fsi.netOut.outputList)
        assert result

    fpServerParms = "fubar;shazoom.true"

    fullServerParms = ["0000000000",
                 "%010i" % len(fpServerParms), fpServerParms,
                 "%010i" % len(ft2Doc1), ft2Doc1,
                 "%010i" % len(ft2Doc2), ft2Doc2,
                 "0000000000",
                 ]

    args5 = ["foo/bar/TestRunner.py",
             "+v",
             "-rp",
             "-o",
             "tests/testout",
             "localhost",
             "8080",
             "AGreatTestPage"]

    def testParmsFromServer(self):
        trun = self.trun
        fsi.netIn.inputList = self.full2Docs
        result = trun.run(self.args5)
        print "trun.run(arg5): %s" % result
        print "-------------- output list ----------------"
        print "\n".join(fsi.netOut.outputList)
        assert result

class TestStatsHandler(ut.TestCase):
##    def setUp(self):
##        print '%s %s' % (self.id(), self.shortDescription())
##        self.saveMsg = fsi.conMsg
##        fsi.conMsg = fsi.TestMsgWriter()
##
##    def tearDown(self):
##        fsi.conMsg.logToStdout(self.id())
##        fsi.conMsg = self.saveMsg

    def testInstantiation(self):
        obj = fsi.StatsHandler("outputDir", "SuiteName", "localhost", 80)
        assert obj._outDir == "outputDir"
        assert obj._suiteName == "SuiteName"

    def testEndOfPage(self):
        obj = fsi.StatsHandler("outputDir", "SuiteName", "localhost", 80)
        obj.endOfATest("pageTitle", Counts(), {})
        assert len(obj._pageList) == 1
        assert obj._pageList[0][0] == "pageTitle"

    def testTwoEndsOfPage(self):
        obj = fsi.StatsHandler("outputDir", "SuiteName", "localhost", 80)
        obj.endOfATest("pageTitle", Counts(), {})
        obj.endOfATest("secondPage", Counts(), {})
        assert len(obj._pageList) == 2
        assert obj._pageList[0][0] == "pageTitle"
        assert obj._pageList[1][0] == "secondPage"

    def testGeneratedXML(self):
        obj = fsi.StatsHandler("outputDir", "SuiteName", "localhost", 80)
        obj.endOfATest("pageTitle", Counts(5, 0, 0, 0), {"fee": "fi"})
        obj.endOfATest("secondPage", Counts(6, 2, 0, 0), {"fo": "fum"})
        text = obj.endOfAllTests()
        assert text.startswith('<?xml version="1.0"?>')
        assert text.count("<right>") == 3
        print text

class TestOutputFileHandling(ut.TestCase):
    def setUp(self):
        print '%s %s' % (self.id(), self.shortDescription())
        setupFitGlobalForTests("FitNesseBatch")
        self.savePath = copy.copy(sys.path)
        self.saveMsg = fsi.conMsg
        fsi.conMsg = fsi.TestMsgWriter()
        FG.fsa = VirtualFileSystem()
        FG.fsa._addDirectories("tests/testout")
        self.trun = fsi.TestRunner()
        fsi.netIn = fsi.netOut = fsi.net = ioMock()

    def tearDown(self):
        fsi.conMsg.logToStdout(self.id())
        fsi.conMsg = self.saveMsg
        FG.fsa = FileSystemAdapter()
        fsi.netIn = fsi.netOut = fsi.net = fsi.FitNesseNetworkInterface()
        sys.path[:] = self.savePath
        setupFitGlobalForTests("FitNesseBatch")

    ft1chunk1 = ("A Great Test Page\n"
                 "<table><tr><td>fit.PrimitiveFixture</td></tr></table>"
                 "\r\n"
                 )

    fulltest1 = ["0000000000",
                 "%010i" % len(ft1chunk1),
                 ft1chunk1,
                 "0000000000"
                 ]

    args4 = ["TestRunner.py",
             "+vrh",
             "-o", "tests/testout",
             "+p", "fubar",
             "localhost",
             "8080",
             "AnotherGreatTestPage"]    

    def shouldWriteHtml(self):
        trun = self.trun
        fsi.netIn.inputList = self.fulltest1
        result = trun.run(self.args4)
        print "-------------- output list ----------------"
        print "\n".join(fsi.netOut.outputList)
        assert len(FG.fsa.listdir("tests/testout")) == 3
        assert result

    args5 = ["TestRunner.py",
             "+vrh",
             "-o", "fie/fie/foe/fum",
             "+p", "fubar",
             "localhost",
             "8080",
             "AnotherGreatTestPage"]    

    def shouldErrorOnMissingDirectory(self):
        trun = self.trun
        fsi.netIn.inputList = self.fulltest1
        result = trun.run(self.args5)
        print "-------------- output list ----------------"
        print "\n".join(fsi.netOut.outputList)
        assert not result

class SpecifyListOfFiles(ut.TestCase):
    def setUp(self):
        print '%s %s' % (self.id(), self.shortDescription())
        setupFitGlobalForTests("FitNesseBatch")
        self.savePath = copy.copy(sys.path)
        self.saveMsg = fsi.conMsg
        fsi.conMsg = fsi.TestMsgWriter()
        FG.fsa = VirtualFileSystem()
        FG.fsa._addDirectories("tests/testout")
        self.trun = fsi.TestRunner()
        fsi.netIn = fsi.netOut = fsi.net = ioMock()
        FG.fsa._addFile("runlist1.txt", ["\n"])

    def tearDown(self):
#        fsi.conMsg.logToStderr(self.id())
        fsi.conMsg = self.saveMsg
        FG.fsa = FileSystemAdapter()
        fsi.netIn = fsi.netOut = fsi.net = fsi.FitNesseNetworkInterface()
        sys.path[:] = self.savePath
        setupFitGlobalForTests("FitNesseBatch")

    def shouldHave2PosParmsWhenListOption(self):
        trun = self.trun
        assert trun.args(["TestRunner.py",
             "+vrh",
             "-o", "tests/testout",
             "+p", "fubar",
             "+u", "runlist1.txt",
             "localhost",
             "8080"])

    def shouldComplainIfSpecifiedListDoesntExist(self):
        trun = self.trun
        assert not trun.args(["TestRunner.py",
             "+vh",
             "-o", "tests/testout",
             "+p", "fubar",
             "+u", "missingrunlist.txt",
             "localhost",
             "8080"])

if __name__ == '__main__':
    ut.main(defaultTest='makeFitServerTest')
