# unit tests for RunnerImplementation.
#legalStuff jr05
# Copyright 2005 John H. Roth Jr.
# Released under the terms of the General Public License (GPL), Release 2.1 or later
# See license.txt for terms and disclaimer of all warrenties and liability.
# Last updated for Release 0.8a1
#endLegalStuff

import os, os.path
import sys
import types
from unittest import makeSuite, TestCase, main

from fit.Counts import Counts
from fit.InitEnvironment import FG, clearFitGlobalForTests
from fit.FixtureLoader import FixtureLoader
from fit.Options import Options
from fit import RunnerImplementation as hi
from fit.Parse import Parse
from tests.RunnerTestCommon import VirtualFileSystem, MockFileObject, \
     applicationExitClass, DummyApplicationExit
from fit.SiteOptions import BatchBase
from fit.Utilities import em

try:
    False
except: #pragma: no cover
    True = 1
    False = 0

def makeRunnerImplementationTest():
    theSuite = makeSuite(TestRunnerImplementationInstantiation, 'test')
    theSuite.addTests([makeSuite(TestRunner, 'test'),
                makeSuite(TestStatsHandler, 'should'),
                makeSuite(TestConsoleTotals, 'should'),
                makeSuite(TestAllFilesInDirectory, 'test'),
                makeSuite(ExamplesForListOfFiles, 'exampleOf'),
                makeSuite(TestHTMLRunner, 'should'),
                makeSuite(TestDirectoryRunner, 'should'),
                ])
    return theSuite

class ConsoleMessageHandlerMock(hi.ConsoleMessageHandler):
    def __init__(self):
        super(ConsoleMessageHandlerMock, self).__init__()
        self.errMsgList = []

    def err(self, msg):        
        if msg[-1] != "\n":
            msg += "\n"
        self.errMsgList.append(msg)

    def printStdErrMsgs(self):
        if len(self.errMsgList) == 0:
            print "----------- no msgs on stderr -----------------"
            return
        print "---------------- msgs from stderr -----------------"
        for msg in self.errMsgList:
            print msg.rstrip()
        print "---------------- end of messages ------------------"

class TestRunnerImplementationInstantiation(TestCase):
    def setUp(self):
        print '%s %s' % (self.id(), self.shortDescription())
        hi.conMsg = ConsoleMessageHandlerMock()
        hi.FileRunner.InjectedSetUpTearDownFileHandler = (
            hi.SetUpTearDownFileHandler)

    def testInstantiation(self):
        unused = hi.FileRunner()

    def tearDown(self):
        hi.conMsg.printStdErrMsgs()
        hi.conMsg = hi.ConsoleMessageHandler()        

class TestRunner(TestCase):
    def setUp(self):
        print '%s %s' % (self.id(), self.shortDescription())
        FixtureLoader.clearFixtureRenameTable()
        hi.conMsg = ConsoleMessageHandlerMock()
        hi.FileRunner.InjectedSetUpTearDownFileHandler = (
            hi.SetUpTearDownFileHandler)
        clearFitGlobalForTests("Batch")
        FG.fsa = VirtualFileSystem()
        FG.fsa._addDirectories("fat/Documents", "fat/Reports")
        FG.fsa._addFile("fat/Documents/BinaryChop.html",
                 ["<html><head><title>A Test File</title></head><body>",
                  "<h1><center>A Test File</center></h1>",
                  "<table>",
                  "<tr><td>fit.Summary</td></tr>",
                  "</table></body></html>\n"
                  ])
        FG.fsa._addFile("fat/Documents/ListOfFiles.txt",
            ["not an example of a list of files!"])
        self.obj = hi.FileRunner()

    def tearDown(self):
        hi.conMsg.printStdErrMsgs()
        hi.conMsg = hi.ConsoleMessageHandler()
        FG.fsa = FG.FileSystemAdapter()
        clearFitGlobalForTests("Batch")
        FixtureLoader.clearFixtureRenameTable()

    fakeParms1 = ["FileRunner.py",
                  "fat/Documents/BinaryChop.html",
                  "fat/Reports/BinaryChop.html"
                  ]

    def testParameterParsing(self):
        obj = self.obj
        result = obj.parms(self.fakeParms1)
        assert result, "result of obj.parms(self.fakeparms1)"
        inFileExpect = os.path.join("fat", "Documents", "BinaryChop.html")
        assert obj.inFile.endswith(inFileExpect), (
            "inFile expected: %s is %s" % (inFileExpect, obj.inFile))
        assert obj.outDir.endswith(os.path.join("fat", "Reports",
                                                     "BinaryChop.html"))

    invalidParms = ["FileRunner.py",
                    "+w",
                    "fat/Documents/BinaryChop.html",
                    "fat/Reports/BinaryChop.html"
                    ]

    def testInvalidParms(self):
        obj = self.obj
        result = obj.parms(self.invalidParms)
        assert not result, "result of obj.parms(self.invalidParms)"

    validFitSpecificationLevel = ["FileRunner.py",
                    "+l", "1.1",
                    "fat/Documents/BinaryChop.html",
                    "fat/Reports/BinaryChop.html"
                    ]

    def testValidFitSpecificationLevel(self):
        obj = self.obj
        result = obj.parms(self.validFitSpecificationLevel)
        msgs = "".join(hi.conMsg.errMsgList)
        assert result, ("result of obj.parms("
                        "self.validFitSpecificationLevel)")
        assert msgs.find("Standards level must be 1.1") == -1
        assert FG.SpecificationLevel == "1.1"

    invalidFitSpecificationLevel = ["FileRunner.py",
                    "+l", "2.0",
                    "fat/Documents/BinaryChop.html",
                    "fat/Reports/BinaryChop.html"
                    ]

    def testInvalidFitSpecificationLevel(self):
        obj = self.obj
        result = obj.parms(self.invalidFitSpecificationLevel)
        msgs = "".join(hi.conMsg.errMsgList)
        assert result, ("result of obj.parms("
                        "self.invalidFitSpecificationLevel)")
        assert msgs.find("Standards level must be 1.1") > -1
        assert FG.SpecificationLevel == "1.1"
        
    def testDiagnosticOptions(self):
        obj = self.obj
        unused = obj.parms(["FileRunner.py",
                    "+z", "foo.true", "+z", "bar.false", "+z", "bent.t.z",
                    "+z", "fum",
                    "fat/Documents/BinaryChop.html",
                    "fat/Reports/BinaryChop.html"
                    ])
#        msgs = "".join(hi.conMsg.errMsgList)
        assert FG.RunDiagnosticOptions["foo"]
        assert not FG.RunDiagnosticOptions["bar"]
        assert FG.RunDiagnosticOptions["bent"]
        assert FG.RunDiagnosticOptions["fum"]
        assert len(FG.RunDiagnosticOptions) == 4

    def testRunLevelSymbols(self):
        obj = self.obj
        unused = obj.parms(["FileRunner.py",
                    "+t", "foo.true", "+t", "bar", "+t", "bent.t.sym",
                    "fat/Documents/BinaryChop.html",
                    "fat/Reports/BinaryChop.html"
                    ])
#        msgs = "".join(hi.conMsg.errMsgList)
        assert FG.RunLevelSymbols["foo"] == "true"
        assert FG.RunLevelSymbols["bar"] is None
        assert FG.RunLevelSymbols["bent"] == "t"
        assert len(FG.RunLevelSymbols) == 3

    invalidCSS = ["FileRunner.py",
                    "+c", "+e",
                    "fat/Documents/BinaryChop.html",
                    "fat/Reports/BinaryChop.html"
                    ]

    def testInvalidCSS(self):
        obj = self.obj
        result = obj.parms(self.invalidCSS)
        msgs = "".join(hi.conMsg.errMsgList)
        assert result, ("result of obj.parms("
                        "self.invalidCSS)")
        assert not obj.options.useCSS
        assert msgs.find("Standards mode requested. CSS output suppressed") > -1

    def testInputNotAFile(self):
        obj = self.obj
        result = obj.parms(["FileRunner.py",
                          "fat/Documents/NotAnAcceptanceTest.html",
                          "fat/Reports/NotAnAcceptanceTest.html"]
                         )
        assert not result

    def testOutputDirectoryDoesNotExistForInputFile(self):
        obj = self.obj
        result = obj.parms(["FileRunner.py",
                          "fat/Documents/BinaryChop.html",
                          "fubar/NotAnAcceptanceTest.html"]
                         )
        assert not result

    def testOutputDirectoryDoesNotExistForInputDirectory(self):
        obj = self.obj
        result = obj.parms(["FileRunner.py",
                          "fat/Documents",
                          "fubar/NotAnAcceptanceTest.html"]
                         )
        assert not result

    def testOutputDirectoryDoesNotExistForListOfFiles(self):
        obj = self.obj
        result = obj.parms(["FileRunner.py",
                          "fat/Documents/ListOfFiles.txt",
                          "fubar/NotAnAcceptanceTest.html"]
                         )
        assert not result

    def testErrorOnTooManyPositionalParameters(self):
        obj = self.obj
        result = obj.parms(["FileRunner.py",
                          "fat/Documents/BinaryChop.html",
                          "fubar/NotAnAcceptanceTest.html",
                          "snafu/anotherFile",
                          "yetAnotherParameter"]
                         )
        assert not result

    def testErrorOnTooFewPositionalParameters(self):
        obj = self.obj
        result = obj.parms(["FileRunner.py",
                          "fat/Documents/BinaryChop.html",])
        assert not result

    def testErrorIfOutputForSingleFileIsNotAFile(self):        
        obj = self.obj
        result = obj.parms(["FileRunner.py",
                          "fat/Documents/BinaryChop.html",
                          "fat/Reports"])
        assert not result


    fakeParms_v = ["FileRunner.py",
                   "+v",
                   "fat/Documents/BinaryChop.html",
                   "fat/Reports/BinaryChop.html"
                   ]

    def testVerboseOption(self):
        obj = self.obj
        result = obj.parms(self.fakeParms_v)
        assert result
        assert obj.options.verbose

    def testParseInput(self):
        obj = self.obj
        assert obj.parms(self.fakeParms_v)
        obj.run()
        newFile = FG.fsa._findFile("fat/Reports/BinaryChop.html")
        text = "".join(newFile[1])
        print "file out: \n%s" % text
        assert text.find("fit.Summary") != -1

    def testParseError(self):
        obj = self.obj
        assert obj.parms(self.fakeParms_v)
        FG.fsa._addFile("fat/Documents/BinaryChop.html",
            ["<table ref=1>"
                        "<table ref=2><tr><td>input</td></tr></table>"
                        "<table ref=3><tr><td>fit.Comment</td></tr></table>"
                        "\n"])
        obj.run()
        msgs = "".join(hi.conMsg.errMsgList)
        assert msgs.find("ParseException") > -1        

    def testWikiTag(self):
        obj = self.obj
        assert obj.parms(self.fakeParms_v)
        FG.fsa._addFile("fat/Documents/BinaryChop.html",
            ["<table ref=1><wiki>"
                        "<table ref=2><tr><td>input</td></tr></table>"
                        "<table ref=3><tr><td>fit.Comment</td></tr></table>"
                        "</wiki></table>\n"])
        obj.run()
        newFile = FG.fsa._findFile("fat/Reports/BinaryChop.html")
        text = "".join(newFile[1])
        print "file out: \n%s" % text
        assert text.find("fit.Comment") != -1

    def testParseOutput(self):
        obj = self.obj
        assert obj.parms(self.fakeParms_v)
        obj.run()
        newFile = FG.fsa._findFile("fat/Reports/BinaryChop.html")
        print "output file: '%s'" % (newFile,)

    def testThatOutputFileCreated(self):
        obj = self.obj
        assert obj.parms(self.fakeParms_v)
        obj.run()
        newFile = FG.fsa._findFile("fat/Reports/BinaryChop.html")
        print "output file: '%s'" % (newFile,)

    def testCreatingFileInUTF8Format(self):
        obj = self.obj
        assert obj.parms(["FileRunner.py",
                   "+v", "+o", "utf-8",
                   "fat/Documents/BinaryChop.html",
                   "fat/Reports/BinaryChop.html"])
        obj.run()
        newFile = FG.fsa._findFile("fat/Reports/BinaryChop.html")
        text = "".join(newFile[1])
        print "output file: '%s'" % (newFile,)
        assert text.find("charset=utf-8") > -1

    def testInvokingFit(self):
        obj = self.obj
        assert obj.parms(self.fakeParms_v)
        obj.run()
        newFile = FG.fsa._findFile("fat/Reports/BinaryChop.html")
        print "output file: '%s'" % (newFile,)

    def testListOfFilesAndRenameFileShouldBeInvalid(self):
        obj = self.obj
        assert not obj.parms(["FileRunner.py",
                              "+v",
                              "fat/Documents/ListOfFiles.txt",
                              "fat/Reports",
                              "fat/RenamesFile.txt",
                              ])
        msgs = "".join(hi.conMsg.errMsgList)
        assert msgs.find("Rename File not allowed for list of files option") > -1

    fakeParms_vs = ["FileRunner.py",
                  "+vs",
                  "fat/Documents/BinaryChop.html",
                  "fat/Reports/BinaryChop.html"
                  ]

    def testSetUpTearDown(self):
        obj = self.obj
        assert obj.parms(self.fakeParms_vs)
        FG.fsa._addFile("fat/Documents/SetUp.html",
                        ["<html><head><title>first</title></head><body>",
                         "<table><tr><td>input</td></tr></table>",
                         "<table><tr><td>input2</td></tr></table>",
                         "</BODY></HTML>"])
        FG.fsa._addFile("fat/Documents/TearDown.html",
                       ["<html><head><title>last</title></head><body>",
                        "<table><tr><td>input3</td></tr></table>",
                        "<table><tr><td>input4</td></tr></table>",
                        "</BODY></HTML>"])
        FG.fsa._addFile("fat/Documents/BinaryChop.html",
            ["<table><tr><td>middle</td></tr></table>\n"])
        obj.run()

        newFile = FG.fsa._findFile("fat/Reports/BinaryChop.html")
        text = "".join(newFile[1])
        print "file out: \n%s" % text
        assert text.find("first") != -1

    def testMockFileOutput(self):        
        obj = self.obj
        assert obj.parms(self.fakeParms_vs)
        FG.fsa._addFile("fat/Documents/SetUp.html",
                        ["<html><head><title>first</title></head><body>",
                         "<table><tr><td>input</td></tr></table>",
                         "<table><tr><td>input2</td></tr></table>",
                         "</BODY></HTML>"])
        FG.fsa._addFile("fat/Documents/TearDown.html",
                       ["<html><head><title>last</title></head><body>",
                        "<table><tr><td>input3</td></tr></table>",
                        "<table><tr><td>input4</td></tr></table>",
                        "</BODY></HTML>"])
        FG.fsa._addFile("fat/Documents/BinaryChop.html",
            ["<table><tr><td>middle</td></tr></table>\n"])
        obj.run()

    def testDefaultFixtureRenames(self):        
        obj = self.obj
        FG.fsa._addFile("fat/Documents/FixtureRenames.txt",
                        ["foo: bar\n"])
        assert obj.parms("FileRunner.py +vs fat/Documents/BinaryChop.html"
                         " fat/Reports/BinaryChop.html".split())
        assert FixtureLoader._fixtureRenameTable.get("foo")

    def testFixtureRenamesOnCommand(self):        
        obj = self.obj
        assert obj.parms(self.fakeParms_vs)
        FG.fsa._addFile("fat/Documents/NewRenames.txt",
                        ["foo: bar\n"])
        assert obj.parms("FileRunner.py +vs"
                         " fat/Documents/BinaryChop.html"
                         " fat/Reports/BinaryChop.html"
                         " fat/Documents/NewRenames.txt".split())
        assert FixtureLoader._fixtureRenameTable.get("foo")

    def testInvalidFixtureRenamesOnCommand(self):        
        obj = self.obj
        assert obj.parms("FolderRunner.py +vx"
                         " fat/Documents/BinaryChop.html"
                         " fat/Reports/BinaryChop.html".split())
        msgs = "".join(hi.conMsg.errMsgList)
        assert msgs.find("Cannot collect stats on single file") > -1

    def testLoadingApplicationConfigurationModule(self):        
        obj = self.obj
        applicationExitClass["test1"] = DummyApplicationExit
        result = obj.parms("FolderRunner.py +v"
                         " +a tests.RunnerTestCommon"
                         " fat/Documents/BinaryChop.html"
                         " fat/Reports/BinaryChop.html".split())
        assert result
        assert isinstance(FG.RunAppConfig, DummyApplicationExit)

    def testErrorInLoadingApplicationConfigurationModule(self):        
        obj = self.obj
        applicationExitClass["test1"] = DummyApplicationExit
        result = obj.parms("FolderRunner.py +v"
                         " +a tests.RunnerTestNotThere"
                         " fat/Documents/BinaryChop.html"
                         " fat/Reports/BinaryChop.html".split())
        assert not result
        msgs = "".join(hi.conMsg.errMsgList)
        assert msgs.find("Error loading application configuration module"
                         " tests.RunnerTestNotThere") > -1

class TestStatsHandler(TestCase):
    def setUp(self):
        print '%s %s' % (self.id(), self.shortDescription())
        hi.conMsg = ConsoleMessageHandlerMock()
        hi.stats = hi.StatProxy()

    def shouldCreateStatXML1(self):
        stats = hi.stats
        stats.init("foo.bar")
        stats.reportStats("larry/moe/curly", Counts(8, 10, 5, 4),
                          {"a": "foo", "b": "bar"})
        stats.reportStats("Laurel/Hardy", Counts(4, 6), {"23": "skidoo"})
        statStr = str(stats)
        arrowCount = statStr.count("<")
        assert arrowCount == 5 + 2*4 + 2*16 + 3*2

    def shouldCreateStatsForSuppressedRun(self):
        stats = hi.stats
        stats.init("foo.bar")
        stats.reportStats("larry/moe/curly", None, 
                          {"a": "foo", "b": "bar"})
        stats.reportStats("Laurel/Hardy", Counts(4, 6), {"23": "skidoo"})
        statStr = str(stats)
        arrowCount = statStr.count("<")
        assert arrowCount == 5 + 2*4 + 2*6 + 1*10 + 3*2

    # XXX need test to actually write to output - or at least to the vfs

    def shouldReturnMessageFromDummyCollector(self):
        assert str(hi.stats) == "Null Stat Collector!"

    def tearDown(self):
        hi.conMsg.printStdErrMsgs()
        hi.conMsg = hi.ConsoleMessageHandler()
        hi.stats = hi.StatProxy()

class TestConsoleTotals(TestCase):
    def setUp(self):
        print '%s %s' % (self.id(), self.shortDescription())        
        hi.conMsg = ConsoleMessageHandlerMock()

    def tearDown(self):
        hi.conMsg.printStdErrMsgs()
        hi.conMsg = hi.ConsoleMessageHandler()

    def shouldWriteOneLineForSingleTest(self):
        conspec = (["vi- T",
                    "iio ynlf yn",
                    "rio spam; 8,6,5,7",
                    "ti- 8,6,5,7",])
        self._driveConsole(conspec)
        self._checkConMsgs(conspec)

    def shouldDosomethingForTwoTestsFromADirectory(self):
        conspec = (["vi- T",
                    "iio ytdf yt",
                    "rio spam; 8,6,5,7",
                    "rio ham; 5",
                    "tio 1,0,0,1",])
        self._driveConsole(conspec)
        self._checkConMsgs(conspec)

    def shouldChangeFolderToSummaryTotalsForSingleDirectory(self):
        conspec = (["vi- T",
                    "iio yfdf yt",
                    "rio spam; 8,6,5,7",
                    "rio ham; 5",
                    "tio 1,0,0,1",])
        self._driveConsole(conspec)
        self._checkConMsgs(conspec)

    def shouldSuppressFileMessagesIfRequested(self):
        conspec = (["vi- T",
                    "iio nfdf nt",
                    "ri- spam; 8,6,5,7",
                    "ri- ham; 5",
                    "tio 1,0,0,1",])
        self._driveConsole(conspec)
        self._checkConMsgs(conspec)

    def shouldSuppressNonErrorsWithErrorOnly(self): 
        conspec = (["vi- T",
                    "iio efdt ef",
                    "ri- foo/bar/ham; 5",
                    "d-o bar",
                    "rio foo/bar/spam; 8,6,5,7",
                    "e-o 1,0,0,1",
                    "tio 1,0,0,1",])
        self._driveConsole(conspec)
        self._checkConMsgs(conspec)

    def shouldPrintTotalsWhenErrorLinePrinted(self): 
        conspec = (["vi- T",
                    "iio efdt ef",
                    "ri- foo/bar/ham; 5",
                    "d-o bar",
                    "rio foo/bar/spam; 8,6,5,7",
                    "e-o 1,0,0,1",
                    "ri- larry/moe/curly; 1",
                    "tio 2,0,0,1",])
        self._driveConsole(conspec)
        self._checkConMsgs(conspec)

    def shouldSuppressDirectoryIfNoErrorsWithErrorOnly(self): 
        conspec = (["vi- T",
                    "iio efdt ef",
                    "ri- ham; 5",
                    "tio 1",])
        self._driveConsole(conspec)
        self._checkConMsgs(conspec)

    def shouldWriteFolderHeaders(self): 
        conspec = (["vi- T",
                    "iio tfdt tf",
                    "d-o bar",
                    "rio foo/bar/ham; 5",
                    "e-o 1",
                    "tio 1",])
        self._driveConsole(conspec)
        self._checkConMsgs(conspec)

    def shouldSuppressFileMessageIfNoCountsAndErrorOnly(self):
        conspec = (["vi- T",
                    "iio efdf et",
                    "ri- ham; 5",
                    "ri- spam; None",
                    "tio 1,0,1,0",])
        self._driveConsole(conspec)
        self._checkConMsgs(conspec)

    def shouldReportSuppressionIfNoCounts(self):
        conspec = (["vi- T",
                    "iio yfdf yt",
                    "rio ham; 5",
                    "rio spam; None",
                    "tio 1,0,1,0",])
        self._driveConsole(conspec)
        self._checkConMsgs(conspec)

    def _makeBool(self, char):
        if char[0].lower() == "t":
            return True
        else:
            return False

    def _makeCounts(self, counts):
        if counts.strip() == "None":
            return None
        countList = [int(x) for x in counts.split(",")]
        return Counts(*countList)

    def _driveConsole(self, spec):
        for cmd in spec:
            if cmd[1] != "i": continue
            cmdChar = cmd[0]
            cmdOpnd = cmd[4:]
            if cmdChar == "v":
                hi.conMsg.setVerbose(self._makeBool(cmdOpnd))
            elif cmdChar == "i":
                hi.conTotal.init(cmdOpnd[0], cmdOpnd[1], cmdOpnd[2],
                              self._makeBool(cmdOpnd[3]))
            elif cmdChar == "d":
                hi.conTotal.folderTitle(cmdOpnd)
            elif cmdChar == "r":
                fileName, counts = cmdOpnd.split(";")
                hi.conTotal.fileResult(fileName, self._makeCounts(counts))
            elif cmdChar == "e":
                hi.conTotal.directoryTotal(self._makeCounts(cmdOpnd))
            else: # should be "t", not checked.
##                hi.conTotal.finalTotal(self._makeCounts(cmdOpnd))
                hi.conTotal.finalTotal()

    def _errHeader(self, status):
        if status:
            return
        em("\nconsole message mismatch for: %s" % self.id())

    def _checkConMsgs(self, spec):
        msgs = hi.conMsg.errMsgList
        sx = mx = 0
        err = False
        while sx < len(spec) and mx < len(msgs):
            if err:
                em("merge process. spec %s %s" % (sx, spec[sx]))
                em("---msg %s %s" % (mx, msgs[mx]))
            cmd = spec[sx]
            if cmd[2] != "o":
                sx += 1
                continue
            msg = msgs[mx].rstrip()
            cmdChar = cmd[0]
            cmdOpnd = cmd[4:]
            if cmdChar == "i":
                run, total = [x[1:-1] for x in msg.split()
                              if x[0] == "'"]
                if (cmdOpnd[5], cmdOpnd[6]) != (run, total):
                    self._errHeader(err)
                    em("cmd: %s msg: %s" % (cmd, msg))
                    err = True
                sx += 1
                mx += 1
                continue
            elif cmdChar == "d":
                dirPos = msg.find(":")
                if dirPos == -1:
                    self._errHeader(err)
                    em("cmd: %s msg: %s" % (cmd, msg))
                    err = True
                    sx += 1
                    continue
                if cmdOpnd.strip() != msg[dirPos+1:].strip():
                    self._errHeader(err)
                    em("cmd: %s msg: %s" % (cmd, msg))
                    err = True
                sx += 1
                mx += 1
                continue
            elif cmdChar == "r":
                suppressMsg = "Run Suppressed by Application Exit"
                if msg.startswith(suppressMsg):
                    msgCounts = None
                    msgName = msg[len(suppressMsg):].strip()
                else:
                    exPos = msg.find("exceptions")
                    if exPos == -1:
                        self._errHeader(err)
                        em("cmd: %s msg: %s" % (cmd, msg))
                        err = True
                        sx += 1
                        continue
                    splitPos = msg.find(" ", exPos + 1)
                    if splitPos == -1:
                        msgCounts = Counts(msg)
                        msgName = ""
                    else:
                        msgCounts = Counts(msg[:splitPos])
                        msgName = msg[splitPos+1:]
                cmdName, cmdString = cmdOpnd.split(";")
                cmdCounts = self._makeCounts(cmdString)
                cmdFileName = FG.fsa.basename(cmdName)
                if msgCounts != cmdCounts or msgName != cmdFileName:
                    self._errHeader(err)
                    em("cmd: %s msg: %s" % (cmd, msg))
                    err = True
                sx += 1
                mx += 1
                continue
            elif cmdChar == "e":
                if not msg.startswith("Total this Directory:"):
                    self._errHeader(err)
                    em("err1 - cmd: %s msg: %s" % (cmd, msg))
                    err = True
                    sx += 1
                    continue
                else:
                    exPos = msg.find(":")
                    msgString = msg[exPos:].strip()
                    msgCounts = Counts(msgString.strip())
                    cmdCounts = self._makeCounts(cmdOpnd)
                    if msgCounts != cmdCounts:
                        self._errHeader(err)
                        em("err2 - cmd: %s msg: %s" % (cmd, msg))
                        err = True
                sx += 1
                mx += 1
                continue    
            elif cmdChar == "t":
                if not msg.startswith("Total tests Processed:"):
                    self._errHeader(err)
                    em("cmd: %s msg: %s" % (cmd, msg))
                    err = True
                    sx += 1
                    continue
                else:
                    exPos = msg.find(":")
                    msgString = msg[exPos:].strip()
                    msgCounts = Counts(msgString.strip())
                    cmdCounts = self._makeCounts(cmdOpnd)
                    if msgCounts != cmdCounts:
                        self._errHeader(err)
                        em("cmd: %s msg: %s" % (cmd, msg))
                        err = True
                sx += 1
                mx += 1
                continue
            else:
                mx += 1
                continue
        while sx < len(spec):
            if spec[sx][2] != "o":
                sx += 1
                continue
            self._errHeader(err)
            em("extra specification elements at end of messages")
            em("next element to process: %s" % spec[sx])
            err = True
            break
        if err:
            em("---- message list ----")
            for msg in hi.conMsg.errMsgList:
                em(msg)
        assert not err

class Utilities(object):        
    def addFile(self, fileList, path, name):
        pieces = {"t": name, "n": '\n', "f": name}
        newList = [x % pieces for x in fileList]
        FG.fsa._addFile(path, newList)

    def verExists(self, *paths):
        result = True
        for path in paths:
            if FG.fsa.exists(path): continue
            print "--- in verExists. File or directory %s does not exist!" % path
            result = False
        return result

    def verNotExist(self, *paths):
        result = True
        for path in paths:
            if not FG.fsa.exists(path): continue
            print "--- in verNotExist. File or directory %s exists!" % path
            result = False
        return result

    def verContains(self, path, *items):
        result = True
        aFile = FG.fsa._findFile(path)
        if not aFile:
            print "--- in verContains. File %s does not exist!" % path
            return False
        text = "".join(aFile[1])
        for item in items:
            aCount = text.count(item)
            if not aCount:
                print "--- File %s does not contain %s" % (path, item)
                result = False
        return result
        
    def verDoesNotContain(self, path, *items):
        result = True
        aFile = FG.fsa._findFile(path)
        if not aFile:
            print "--- in verDoesNotContain. File %s does not exist!" % path
            return False
        text = "".join(aFile[1])
        for item in items:
            aCount = text.count(item)
            if aCount:
                print "--- File %s contains %s" % (path, item)
                result = False
        return result

class TestAllFilesInDirectory(TestCase, Utilities):
    def setUp(self):
        print '%s %s' % (self.id(), self.shortDescription())
        hi.conMsg = ConsoleMessageHandlerMock()
        FG.fsa = VirtualFileSystem()
        FG.fsa._addDirectories("in/a", "in/a/b", "in/a/c", "out/a")
        fileList = ["<html><head><title>%(t)s</title></head><body>%(n)s",
                  "<h1><center>%(t)s</center></h1>%(n)s",
                  "<table>%(n)s",
                  "<tr><td>%(f)s</td></tr>%(n)s",
                  "</table></body></html>%(n)s"
                  ]
        self.addFile(fileList, "in/a/a1.htm", "a1")
        self.addFile(fileList, "in/a/a2.htm", "a2")
        self.addFile(fileList, "in/a/a3.htm", "a3")
        self.addFile(fileList, "in/a/SetUp.htm", "SetUpA")
        self.addFile(fileList, "in/a/TearDown.htm", "TearDownA")
        self.addFile(fileList, "in/a/b/b1.htm", "b1")
        self.addFile(fileList, "in/a/b/b2.htm", "b2")
        self.addFile(fileList, "in/a/b/b3.htm", "b3")
        self.addFile(fileList, "in/a/b/SetUp.html", "SetUpB")
        self.addFile(fileList, "in/a/c/c1.html", "c1")
        self.addFile(fileList, "in/a/c/c2.html", "c2")
        self.addFile(fileList, "in/a/c/c3.html", "c3")
        self.addFile(fileList, "in/a/c/TearDown.html", "TearDownC")
        self.obj = hi.FileRunner()

    def tearDown(self):
        hi.conMsg.printStdErrMsgs()
        hi.conMsg = hi.ConsoleMessageHandler()
        FG.fsa = FG.FileSystemAdapter()

    def testSingleDirectory(self):
        obj = self.obj
        assert obj.parms("FileRunner.py +v +q et in/a out/a".split())
        obj.run()
        assert self.verExists("out/a/a1.htm", "out/a/a2.htm", "out/a/a3.htm")
        assert self.verNotExist("out/a/b", "out/a/c",
                                "out/a/SetUp.htm", "out/a/TearDown.htm")
        assert self.verContains("out/a/a1.htm", "a1")
        assert self.verDoesNotContain("out/a/a1.htm", "SetUpA", "TearDownA")

    def testSingleDirectoryWithSetup(self):
        obj = self.obj
        assert obj.parms("FileRunner.py +v +q et +s in/a out/a".split())
        obj.run()
        assert self.verExists("out/a/a1.htm", "out/a/a2.htm", "out/a/a3.htm")
        assert self.verNotExist("out/a/b", "out/a/c",
                                "out/a/SetUp.htm", "out/a/TearDown.htm")
        assert self.verContains("out/a/a1.htm", "a1", "SetUpA", "TearDownA")

    def testMultipleDirectories(self):
        obj = self.obj
        assert obj.parms("FileRunner.py +v +q et +r in/a out/a".split())
        obj.run()
        assert self.verExists("out/a/a1.htm", "out/a/a2.htm", "out/a/a3.htm")
        assert self.verExists("out/a/b/b1.htm", "out/a/b/b2.htm", "out/a/b/b3.htm")
        assert self.verExists("out/a/c/c1.html", "out/a/c/c2.html", "out/a/c/c3.html")
        assert self.verNotExist("out/a/SetUp.htm", "out/a/TearDown.htm")
        assert self.verContains("out/a/a1.htm", "a1")
        assert self.verDoesNotContain("out/a/a1.htm", "SetUpA", "TearDownA")
        assert self.verContains("out/a/b/b1.htm", "b1")
        assert self.verDoesNotContain("out/a/b/b1.htm", "SetUpB", "TearDownB")

    def testStatisticsFileOutput(self):
        obj = self.obj
        assert obj.parms("FileRunner.py +v +q et +r +s +x in/a out/a".split())
        obj.run()
        assert self.verExists("out/a/FitStatistics.xml")

class ExamplesForListOfFiles(TestCase, Utilities):
    def setUp(self):
        print '%s %s' % (self.id(), self.shortDescription())
        FixtureLoader.clearFixtureRenameTable()
        hi.conMsg = ConsoleMessageHandlerMock()
        FG.RunAppConfigModule = None
        FG.RunAppConfig = None
        FG.appConfigModule = None
        FG.appConfig = None
        FG.fsa = VirtualFileSystem()
        FG.fsa._addDirectories("in/a", "in/a/b", "in/a/c", "out/a")
        fileList = ["<html><head><title>%(t)s</title></head><body>%(n)s",
                  "<h1><center>%(t)s</center></h1>%(n)s",
                  "<table>%(n)s",
                  "<tr><td>%(f)s</td></tr>%(n)s",
                  "</table></body></html>%(n)s"
                  ]
        self.addFile(fileList, "in/a/a1.htm", "a1")
        self.addFile(fileList, "in/a/a2.htm", "a2")
        self.addFile(fileList, "in/a/a3.htm", "a3")
        self.addFile(fileList, "in/a/SetUp.htm", "SetUpA")
        self.addFile(fileList, "in/a/TearDown.htm", "TearDownA")
        self.addFile(fileList, "in/a/b/b1.htm", "b1")
        self.addFile(fileList, "in/a/b/b2.htm", "b2")
        self.addFile(fileList, "in/a/b/b3.htm", "b3")
        self.addFile(fileList, "in/a/b/SetUp.html", "SetUpB")
        self.addFile(fileList, "in/a/c/c1.html", "c1")
        self.addFile(fileList, "in/a/c/c2.html", "c2")
        self.addFile(fileList, "in/a/c/c3.html", "c3")
        self.addFile(fileList, "in/a/c/TearDown.html", "TearDownC")
        FG.fsa._addFile("in/a/fl.txt", [
            "[options]\n", "-v\n", "[files]\n", "in/a/a.htm\n", "\n"])
        
        self.obj = hi.FileRunner()

    def tearDown(self):
        hi.conMsg.printStdErrMsgs()
        hi.conMsg = hi.ConsoleMessageHandler()
        FG.fsa = FG.FileSystemAdapter()
        FG.RunAppConfigModule = None
        FG.RunAppConfig = None
        FG.appConfigModule = None
        FG.appConfig = None
        FixtureLoader.clearFixtureRenameTable()

    def exampleOfListInParms(self):
        obj = self.obj
        result = obj.parms("FileRunner.py in/a/fl.txt out/a".split())
        assert result, "result of obj.parms(self.fakeparms1)"
        inFileExpect = os.path.join("in", "a", "fl.txt")
        assert obj.inFile.endswith(inFileExpect), (
            "inFile expected: %s is %s" % (inFileExpect, obj.inFile))
        assert obj.outDir.endswith(os.path.join("out", "a"))
        assert obj.runType == "l", "check for proper run type"
        assert obj._runObj.fileList == ["in/a/a.htm\n"]

    def exampleOfOptionsSection(self):
        obj = self.obj
        unused = obj.parms("FileRunner.py in/a/fl.txt out/a".split())
        assert obj.options.verbose is False

    def exampleOfOptionsSection2(self):
        obj = self.obj
        FG.fsa._addFile("in/a/fl.txt", [
            "[options]\n", "-v\n", "-c\n", "+d utf-8\n",
            "[files]\n", "in/a/a.htm\n", "\n"])
        unused = obj.parms("FileRunner.py in/a/fl.txt out/a".split())
        assert obj.options.verbose is False
        assert obj.options.useCSS is False
        assert obj.options.defaultEncoding == "utf-8"
        assert obj.options.isValid

    def exampleOfInvalidOptionsSection(self):
        obj = self.obj
        FG.fsa._addFile("in/a/fl.txt", [
            "[options]\n", "-w\n",
            "[files]\n", "in/a/a.htm\n", "\n"])
        unused = obj.parms("FileRunner.py in/a/fl.txt out/a".split())
        msgs = "".join(hi.conMsg.errMsgList)
        assert msgs.find("Parameter w not recognized") > -1
        assert not obj.options.isValid

    def exampleOfMissingFileNameInFileSection(self):
        obj = self.obj
        FG.fsa._addFile("in/a/fl.txt", [
            "[files]\n", "+v\n", "\n"])
        unused = obj.parms("FileRunner.py in/a/fl.txt out/a".split())
        assert obj.run() != 0
        msgs = "".join(hi.conMsg.errMsgList)
        assert msgs.find("input file or directory missing in") > -1

    def exampleOfExtraPositionalParametersInFileSection(self):
        obj = self.obj
        FG.fsa._addFile("in/a/fl.txt", [
            "[files]\n", "larry moe curly", "\n"])
        unused = obj.parms("FileRunner.py in/a/fl.txt out/a".split())
        assert obj.run() != 0
        msgs = "".join(hi.conMsg.errMsgList)
        assert msgs.find("too many positional parameters in") > -1

    def exampleOfFixtureRenamesSection(self):
        obj = self.obj
        FG.fsa._addFile("in/a/fl.txt", [
            "[options]\n", "-v\n", "-c\n", "+d utf-8\n",
            "[files]\n", "in/a/a1.htm\n",
            "[fixture renames]\n", "foo: bar\n", "\n"])
        unused = obj.parms("FileRunner.py in/a/fl.txt out/a".split())
        assert FixtureLoader._fixtureRenameTable.get("foo")

    def exampleOfRunningOneFile(self):
        obj = self.obj
        FG.fsa._addFile("in/a/fl.txt", [
            "[options]\n", "-v\n", "-c\n", "+d utf-8\n",
            "[files]\n", "a1.htm\n",
            "[fixture renames]\n", "foo: bar\n", "\n"])
        assert obj.parms("FileRunner.py in/a/fl.txt out/a".split())
        obj.run()
        assert self.verExists("out/a/a1.htm")

    def exampleOfRunningTwoFilesAndADirectory(self):
        obj = self.obj
        FG.fsa._addFile("in/fl.txt", [
            "[options]\n", "-v\n", "-c\n", "+d utf-8\n",
            "[files]\n", "a/a1.htm\n", "a/a2.htm\n", "a/b\n",
            "[fixture renames]\n", "foo: bar\n", "\n"])
        assert obj.parms("FileRunner.py in/fl.txt out".split())
        obj.run()
        assert self.verExists("out/a/a1.htm", "out/a/b/b1.htm")

    def exampleOfOptionsOnASingleLine(self):
        obj = self.obj
        FG.fsa._addFile("in/fl.txt", [
            "[options]\n", "-v\n", "-c\n", "+d utf-8\n",
            "[files]\n", "+r a\n",
            "[fixture renames]\n", "foo: bar\n", "\n"])
        assert obj.parms("FileRunner.py in/fl.txt out".split())
        obj.run()
        assert self.verExists("out/a/a1.htm", "out/a/b/b1.htm")

    def exampleOfFileWithAConfigurationModule(self):
        obj = self.obj
        FG.fsa._addFile("in/fl.txt", [
            "[options]\n", "-v\n", "-c\n", "+d utf-8\n",
            "[files]\n", "+a tests.RunnerTestCommon +r a\n",
            "[fixture renames]\n", "foo: bar\n", "\n"])
        assert obj.parms("FileRunner.py in/fl.txt out".split())
        obj.run()
#        msgs = "".join(hi.conMsg.errMsgList)
#        em(msgs)
        assert self.verExists("out/a/a1.htm", "out/a/b/b1.htm")

    def exampleOfFileWithAnIncorrectConfigurationModule(self):
        obj = self.obj
        FG.fsa._addFile("in/fl.txt", [
            "[options]\n", "-v\n", "-c\n", "+d utf-8\n",
            "[files]\n", "+a tests.RunnerTestNotThere +r a\n",
            "[fixture renames]\n", "foo: bar\n", "\n"])
        assert obj.parms("FileRunner.py in/fl.txt out".split())
        obj.run()
        msgs = "".join(hi.conMsg.errMsgList)
        assert msgs.find("Error loading application configuration module") > -1

    def exampleOfTargetedOutputs(self):
        obj = self.obj
        FG.fsa._addFile("in/fl.txt", [
            "[options]\n", "-v\n", "-c\n", "+d utf-8\n",
            "[files]\n", "a/a1.htm\n", "a/a2.htm a/b/ax.htm\n", "a/b a/c\n",
            "[fixture renames]\n", "foo: bar\n", "\n"])
        assert obj.parms("FileRunner.py in/fl.txt out".split())
        obj.run()
        assert self.verExists("out/a/b/ax.htm", "out/a/c/b1.htm")

    def exampleOfTargetingFileToDirectory(self):
        obj = self.obj
        FG.fsa._addFile("in/fl.txt", [
            "[options]\n", "-v\n", "-c\n", "+d utf-8\n",
            "[files]\n", "a/a1.htm a/c\n",
            "[fixture renames]\n", "foo: bar\n", "\n"])
        assert obj.parms("FileRunner.py in/fl.txt out".split())
        obj.run()
        assert self.verExists("out/a/c/a1.htm")

    def exampleOfNonexistantInput(self):
        obj = self.obj
        FG.fsa._addFile("in/fl.txt", [
            "[options]\n", "-v\n", "-c\n", "+d utf-8\n",
            "[files]\n", "laurel/hardy",
            "[fixture renames]\n", "foo: bar\n", "\n"])
        assert obj.parms("FileRunner.py in/fl.txt out".split())
        obj.run()
        msgs = "".join(hi.conMsg.errMsgList)
        assert msgs.find("laurel/hardy does not exist") > -1

    def exampleOfComments(self):
        obj = self.obj
        FG.fsa._addFile("in/fl.txt", [
            "[options]\n", "-v\n", "#\n", "-c\n", "+d utf-8\n",
            "[files]\n", "a/a1.htm\n", "#\n", "a/a2.htm a/b/ax.htm\n", "a/b a/c\n",
            "[fixture renames]\n", "#\n", "foo: bar\n", "\n"])
        assert obj.parms("FileRunner.py in/fl.txt out".split())
        obj.run()
        assert self.verExists("out/a/b/ax.htm", "out/a/c/b1.htm")

class BeforeTestExecutionExit(object):
    result = True
    def beforeTestExecution(self, unused='inFileName', dummy='parseTree'):
        return self.result

class TestHTMLRunner(TestCase):
    def setUp(self):
        print '%s %s' % (self.id(), self.shortDescription())
        FixtureLoader.clearFixtureRenameTable()
        hi.conMsg = ConsoleMessageHandlerMock()
        hi.FileRunner.InjectedSetUpTearDownFileHandler = (
            hi.SetUpTearDownFileHandler)
        FG.fsa = VirtualFileSystem()
        FG.fsa._addDirectories("fat/Documents", "fat/Reports")
        FG.fsa._addFile("fat/Documents/BinaryChop.html",
                 ["<html><head><title>A Test File</title></head><body>",
                  "<h1><center>A Test File</center></h1>",
                  "<table>",
                  "<tr><td>fit.Summary</td></tr>",
                  "</table></body></html>\n"
                  ])
        FG.fsa._addFile("fat/Documents/ListOfFiles.txt",
            ["not an example of a list of files!"])

    def tearDown(self):
        hi.conMsg.printStdErrMsgs()
        hi.conMsg = hi.ConsoleMessageHandler()
        FG.fsa = FG.FileSystemAdapter()
        FixtureLoader.clearFixtureRenameTable()
        FG.appConfigModule = None
        FG.appConfig = None

    def shouldSuppressExecutionOnRequest(self):
        options = Options(["FileRunner.py",
                              "+v",
                              "fat/Documents/ListOfFiles.txt",
                              "fat/Reports",
                              "fat/RenamesFile.txt",
                              ], BatchBase.parmDict)
        obj = hi.HTMLRunner("fat/Documents/BinaryChop.html",
                            "fat/Reports", options)
        FG.appConfigModule = BeforeTestExecutionExit
        FG.appConfig = BeforeTestExecutionExit()
        BeforeTestExecutionExit.result = False
        result = obj.run()
        assert result == Counts(0,0,1)

    def shouldComplainIfInputDoesNotExist(self):
        options = Options(["FileRunner.py",
                              "+v",
                              "fat/Documents/fubar.html",
                              "fat/Reports",
                              "fat/RenamesFile.txt",
                              ], BatchBase.parmDict)
        obj = hi.HTMLRunner("fat/Documents/fubar.html",
                            "fat/Reports", options)
        assert not obj.verify()
        msgs = "".join(hi.conMsg.errMsgList)
        assert msgs.find("fat/Documents/fubar.html does not exist!") > -1
        head, part3 = os.path.split(obj.outFileName)
        part1, part2 = os.path.split(head)
        pathList = [part1, part2, part3]
        assert pathList == ["fat", "Reports", "fubar.html"]

    def shouldComplainIfParentIsNotADirectory(self):
        options = Options(["FileRunner.py",
                              "+v",
                              "fat/Documents/fubar.html",
                              "Laurel/Hardy.html",
                              "fat/RenamesFile.txt",
                              ], BatchBase.parmDict)
        obj = hi.HTMLRunner("fat/Documents/fubar.html",
                            "Laurel/Hardy.html", options)
        assert not obj.verify()
        msgs = "".join(hi.conMsg.errMsgList)
        assert msgs.find("Laurel is not a directory!") > -1

    def _writeTestFile(self, encoding="utf-8", useBom=True, meta="",
                       htmlTag=True, headTag=True, bodyTag=True,
                       cssLink=None):
        textList = []
        if encoding.lower().startswith("utf") and useBom:
            textList.append(u"\ufeff")
        if htmlTag: textList.append("<html>")
        if headTag: textList.append("<head>")
        if meta:
            textList.append('<meta http-equiv="Content-Type" '
                  'content="text/html; charset=%s">' % meta)
        textList.append("<title>A Test File</title></head>")
        if cssLink:
            textList.append('<link rel="stylesheet" href="%s"'
                            ' type="text/css">\n' % cssLink)
        if headTag: textList.append("</head>")
        if bodyTag: textList.append("<body>")
        textList.append("<h1><center>A Test File</center></h1>"
                  "<table>"
                  "<tr><td>fit.Summary</td></tr>"
                  "</table>")
        if bodyTag: textList.append("</body>")
        if htmlTag: textList.append("</html>")
        text = "".join(textList)
        if encoding:
            encoded = text.encode(encoding)
        else:
            encoded = text
        FG.fsa._addFile("fat/Documents/Test1.html", encoded)
        inThing = FG.fsa._findFile("fat/Documents/Test1.html")
        assert inThing is not None
        return inThing

    def _createOptions(self, out=None, inEncoding=None):
        optionList = ["FileRunner.py", "+v"]
        if out:
            optionList += ["+o", out]
        if inEncoding:
            optionList += ["+i", inEncoding]
        optionList += ["fat/Documents/Test1.html",
                       "fat/Reports",
                       "fat/RenamesFile.txt",]
        options = Options(optionList, BatchBase.parmDict)
        return options

    def _verifyOutputEncoding(self, BOM=None):
        fileThing = FG.fsa._findFile("fat/Reports/Test1.html")
        assert fileThing is not None
        assert fileThing[1][0].startswith(BOM)

    def shouldAcceptUTF8Input(self):
        utf8BOM = "\xef\xbb\xbf"
        inThing = self._writeTestFile()
        assert inThing[1].startswith(utf8BOM)
        options = self._createOptions()
        obj = hi.HTMLRunner("fat/Documents/Test1.html",
                            "fat/Reports", options)
        result = obj.run()
        self._verifyOutputEncoding(utf8BOM)
        assert result == Counts(0,0,0)

    def shouldAcceptUTF16LEInput(self):
        utf16leBOM = "\xff\xfe"
        inThing = self._writeTestFile(encoding="utf-16le")
        assert inThing[1].startswith(utf16leBOM)
        options = self._createOptions()
        obj = hi.HTMLRunner("fat/Documents/Test1.html",
                            "fat/Reports", options)
        result = obj.run()
        self._verifyOutputEncoding(utf16leBOM)
        assert result == Counts(0,0,0)

    def shouldAcceptUTF16BEInput(self):
        utf16beBOM = "\xfe\xff"
        inThing = self._writeTestFile(encoding="utf-16be")
        assert inThing[1].startswith(utf16beBOM)
        options = self._createOptions()
        obj = hi.HTMLRunner("fat/Documents/Test1.html",
                            "fat/Reports", options)
        result = obj.run()
        self._verifyOutputEncoding(utf16beBOM)
        assert result == Counts(0,0,0)

    def shouldTransformUTF8ToUTF16beOnRequest(self):
        utf8BOM = "\xef\xbb\xbf"
        utf16beBOM = "\xfe\xff"
        inThing = self._writeTestFile(encoding="utf-8")
        assert inThing[1].startswith(utf8BOM)
        options = self._createOptions(out="utf-16be")
        obj = hi.HTMLRunner("fat/Documents/Test1.html",
                            "fat/Reports", options)
        result = obj.run()
        self._verifyOutputEncoding(utf16beBOM)
        assert result == Counts(0,0,0)

    def shouldForceInputEncodingToUTF8(self):
        utf8BOM = "\xef\xbb\xbf"
        inThing = self._writeTestFile(encoding="", useBom=False)
        assert not inThing[1].startswith(utf8BOM)
        options = self._createOptions(inEncoding="utf-8")
        obj = hi.HTMLRunner("fat/Documents/Test1.html",
                            "fat/Reports", options)
        result = obj.run()
        self._verifyOutputEncoding(utf8BOM)
        assert result == Counts(0,0,0)

    def shouldAcceptEncodingFromMetaTag(self):
        utf8BOM = "\xef\xbb\xbf"
        inThing = self._writeTestFile(encoding="", useBom=False,
                                      meta="utf-8")
        assert not inThing[1].startswith(utf8BOM)
        options = self._createOptions()
        obj = hi.HTMLRunner("fat/Documents/Test1.html",
                            "fat/Reports", options)
        result = obj.run()
        self._verifyOutputEncoding(utf8BOM)
        assert result == Counts(0,0,0)

    def shouldRemoveMetaTagForUTF16(self):
        utf16beBOM = "\xfe\xff"
        inThing = self._writeTestFile(encoding="utf-16be", meta="utf-16be")
        assert inThing[1].startswith(utf16beBOM)
        text = inThing[1].decode("utf-16be")
        assert text.find("charset=utf-16be") > -1
        options = self._createOptions()
        obj = hi.HTMLRunner("fat/Documents/Test1.html",
                            "fat/Reports", options)
        result = obj.run()
        self._verifyOutputEncoding(utf16beBOM)
        fileThing = FG.fsa._findFile("fat/Reports/Test1.html")
        text = fileThing[1][0].decode("utf-16be")
        assert text.find("charset=utf-16be") == -1
        assert result == Counts(0,0,0)

    def shouldChangeMetaEncodingIfFileEncodingChanges(self):
        utf8BOM = "\xef\xbb\xbf"
        inThing = self._writeTestFile(encoding="utf-8", meta="utf-8")
        assert inThing[1].startswith(utf8BOM)
        options = self._createOptions(out="windows-1252")
        obj = hi.HTMLRunner("fat/Documents/Test1.html",
                            "fat/Reports", options)
        result = obj.run()
        fileThing = FG.fsa._findFile("fat/Reports/Test1.html")
        text = fileThing[1][0]
        encoding, kind = obj._encodingFromMetaTag(text)
        assert encoding == "windows-1252"
        assert result == Counts(0,0,0)

    def shouldNotChangeMetaEncodingIfFileEncodingDoesNotChange(self):
        utf8BOM = "\xef\xbb\xbf"
        inThing = self._writeTestFile(encoding="utf-8", meta="utf-8")
        assert inThing[1].startswith(utf8BOM)
        options = self._createOptions()
        obj = hi.HTMLRunner("fat/Documents/Test1.html",
                            "fat/Reports", options)
        result = obj.run()
        self._verifyOutputEncoding(utf8BOM)
        fileThing = FG.fsa._findFile("fat/Reports/Test1.html")
        text = fileThing[1][0].decode("utf-8")
        encoding, kind = obj._encodingFromMetaTag(text)
        assert encoding == "utf-8"
        assert result == Counts(0,0,0)

    def shouldAddMetaIfHeadMissingAndHTMLpresent(self):
        utf8BOM = "\xef\xbb\xbf"
        inThing = self._writeTestFile(encoding="utf-8", headTag=False)
        assert inThing[1].startswith(utf8BOM)
        options = self._createOptions()
        obj = hi.HTMLRunner("fat/Documents/Test1.html",
                            "fat/Reports", options)
        result = obj.run()
        self._verifyOutputEncoding(utf8BOM)
        fileThing = FG.fsa._findFile("fat/Reports/Test1.html")
        text = fileThing[1][0].decode("utf-8")
        encoding, kind = obj._encodingFromMetaTag(text)
        assert encoding == "utf-8"
        assert text.find("<html><meta") > -1
        assert result == Counts(0,0,0)

    def shouldAddMetaToFrontIfBothHeadAndHtmlMissing(self):
        utf8BOM = "\xef\xbb\xbf"
        inThing = self._writeTestFile(encoding="utf-8",
                                      headTag=False, htmlTag=False)
        assert inThing[1].startswith(utf8BOM)
        options = self._createOptions()
        obj = hi.HTMLRunner("fat/Documents/Test1.html",
                            "fat/Reports", options)
        result = obj.run()
        self._verifyOutputEncoding(utf8BOM)
        fileThing = FG.fsa._findFile("fat/Reports/Test1.html")
        text = fileThing[1][0].decode("utf-8")
        encoding, kind = obj._encodingFromMetaTag(text)
        assert encoding == "utf-8"
        assert text.find("<meta") == 1
        assert result == Counts(0,0,0)

    def shouldNotAddCssIfAlreadyThere(self):
        utf8BOM = "\xef\xbb\xbf"
        inThing = self._writeTestFile(encoding="utf-8", cssLink="FIT.css")
        assert inThing[1].startswith(utf8BOM)
        assert inThing[1].find("FIT.css") > -1
        options = self._createOptions()
        obj = hi.HTMLRunner("fat/Documents/Test1.html",
                            "fat/Reports", options)
        result = obj.run()
        self._verifyOutputEncoding(utf8BOM)
        fileThing = FG.fsa._findFile("fat/Reports/Test1.html")
        text = fileThing[1][0].decode("utf-8")
        encoding, kind = obj._encodingFromMetaTag(text)
        assert encoding == "utf-8"
        assert text.count("FIT.css") == 1
        assert result == Counts(0,0,0)

class TestDirectoryRunner(TestCase):
    def _makeFile(self, aList, sub):
        return [x.replace("%s", sub) for x in aList]
    
    protoFile = ["<html><head><title>Test %s</title></head><body>",
                  "<h1><center>A Test File</center></h1>",
                  "<table>",
                  "<tr><td>fit.Comment</td></tr>",
                  "<tr><td>%s</td></tr>",
                  "</table></body></html>\n"
                  ]

    def setUp(self):
        print '%s %s' % (self.id(), self.shortDescription())
        FixtureLoader.clearFixtureRenameTable()
        hi.conMsg = ConsoleMessageHandlerMock()
        hi.FileRunner.InjectedSetUpTearDownFileHandler = (
            hi.SetUpTearDownFileHandler)
        FG.fsa = VirtualFileSystem()
        FG.fsa._addDirectories("inDir/CVS", "inDir/inSubdir",
                               "outDir/inSubdir")
        FG.fsa._addFile("inDir/TestFile1.html",
                        self._makeFile(self.protoFile, "1"))
        FG.fsa._addFile("inDir/TestFile2.html",
                        self._makeFile(self.protoFile, "2"))
        FG.fsa._addFile("inDir/TestFile3.html",
                        self._makeFile(self.protoFile, "3"))
        FG.fsa._addFile("inDir/SetUp.html",
                        self._makeFile(self.protoFile, "S1"))
        FG.fsa._addFile("inDir/TearDown.html",
                        self._makeFile(self.protoFile, "T1"))
        FG.fsa._addFile("inDir/inSubdir/TestFileA1.html",
                        self._makeFile(self.protoFile, "A1"))
        FG.fsa._addFile("inDir/inSubdir/TestFileA2.html",
                        self._makeFile(self.protoFile, "A2"))
        FG.fsa._addFile("inDir/inSubdir/TestFileA3.html",
                        self._makeFile(self.protoFile, "A3"))
        FG.fsa._addFile("inDir/inSubdir/SetUp.html",
                        self._makeFile(self.protoFile, "S2"))
        FG.fsa._addFile("inDir/inSubdir/TearDown.html",
                        self._makeFile(self.protoFile, "T2"))

    def tearDown(self):
        hi.conMsg.printStdErrMsgs()
        hi.conMsg = hi.ConsoleMessageHandler()
        FG.fsa = FG.FileSystemAdapter()
        FixtureLoader.clearFixtureRenameTable()
        FG.appConfigModule = None
        FG.appConfig = None

    def _createOptions(self, recurse=False):
        optionList = ["DirectoryRunner.py", "+v"]
        if recurse:
            optionList += ["+r"]
        optionList += ["inDir", "outDir",]
        options = Options(optionList, BatchBase.parmDict)
        return options

    def shouldComplainIfDirectoriesDontExist(self):
        obj = hi.DirectoryRunner("Laurel", "Hardy", self._createOptions())
        result = obj.verify()
        assert not result
        text = "".join(hi.conMsg.errMsgList)
        assert text.count("does not exist or is not a directory!") == 2

    def shouldNotComplainIfDirectoriesDoExist(self):
        obj = hi.DirectoryRunner("inDir", "outDir", self._createOptions())
        result = obj.verify()
        assert result
        text = "".join(hi.conMsg.errMsgList)
        assert text.count("does not exist or is not a directory!") == 0

    def shouldVerifyIfOutputIsADirectory(self):
        FG.fsa._addDirectories("inDir/badDir", "inDir/newDir")
        FG.fsa._addFile("outDir/badDir", self._makeFile(self.protoFile, "T2"))
        obj = hi.DirectoryRunner("inDir", "outDir",
                                 self._createOptions(recurse=True))
        result = obj.verify()
        assert result
        obj.run()
        text = "".join(hi.conMsg.errMsgList)
        assert text.count("Cannot create output directory outDir") > 0

if __name__ == '__main__':
    main(defaultTest='makeRunnerImplementationTest')
