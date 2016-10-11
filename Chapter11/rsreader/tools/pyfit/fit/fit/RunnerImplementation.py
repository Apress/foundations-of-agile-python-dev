# RunnerImplementation.
#LegalStuff jr05
# Copyright 2005 John H. Roth Jr.
# Released under the terms of the General Public License (GPL), Release 2.1 or later
# See license.txt for terms and disclaimer of all warrenties and liability.
# Last updated for Release 0.8a1
#endLegalStuff

"""
usage for FileRunner
python FileRunner [options] in-file out-file [rename-file]
\t+ turns option on, - turns option off
\ta <module> Application Configuration module
\tb <option> Option to pass to Application Configuration Module
\tc - CSS formatting mode
\td <encoding> - default if input encoding cannot be determined
\te - force strict compliance with FIT 1.1 specification
\ti <encoding> - input encoding regardless of <meta> tag
\tl <level> - standards level (currently 1.1 only)
\to <encoding> - output encoding
\tq <options> - print results to console
\tr is recursive mode: process all subdirectories
\ts - add SetUp and TearDown files
\tt - run level parameters in the symbol table
\tv - option processing results
\tx - write xml statistics file - must be in multi-file mode.
\tz <option> diagnostic options
\tin-file input file, directory or file list
\tout-file. Output file or directory
\trenames-file is optional
"""


try:
    False
except: #pragma: no cover
    False = 0
    True = 1

try:
    bool(0)
except: #pragma: no cover
    def bool(predicate):
        if predicate:
            return True
        else:
            return False

import copy
import os, os.path
import re
#import stat
import sys
import time
import traceback

from fit.Counts import Counts
from fit import FitGlobal as FG
from fit.Fixture import Fixture
from fit.FixtureLoader import FixtureLoader
from fit.Options import Options
from fit.Parse import Parse
from fit.RunnerCommon import RunnerUtilities
from fit.SiteOptions import BatchBase
from fit.Utilities import em
from fit import Variations

# This module contains six groups of classes. Five of these groups are
# utilities that are effectively singletons. Some of them are replaced by
# the test harness with mocks and simulators, others have global visibility
# for convenience.

# ConsoleMessageHandler (testing mock)
# FileSystemAdapter (testing simulator)
# SetupTeardown
# Statistics Collecter
# Console Total handler

# The actual work is done by the final cluster of classes: FileRunner,
# FileListRunner, DirectoryRunner and HTMLRunner. FileRunner is the top
# level class; it instantiates FileListRunner, DirectoryRunner or
# HTMLRunner as needed for the options on the command line. FileListRunner
# can, in turn, instantiate either DirectoryRunner or HTMLRunner as needed
# by the list of files. DirectoryRunner can instantiate itself recursively
# and also instantiate HTMLRunner. Finally, HTMLRunner actually runs the
# tests. Whew!

# This is an adapter class; there is one instance bound to the module
# level identifier conMsg. It's replaced by the testing framework to
# capture console messages.

# It's marked as no-cover because I'm a bit too lazy to replace the
# stderr handler to write tests for it.

class ConsoleMessageHandler(object): #pragma: no cover
    def __init__(self):
        self.verbose = False

    def setVerbose(self, verbose):
        self.verbose = verbose

    # Overridden by mock for testing console totals.
    def err(self, msg):
        if msg[-1] != "\n":
            msg += "\n"
        sys.stderr.write(msg)

    def notes(self, msg):
        if self.verbose:
            self.err(msg)

    def stats(self, msg):
        self.err(msg)

    def debug(self, msg):
        if msg[-1] != "\n":
            msg += "\n"
        sys.stderr.write(msg)

    def write(self, msg):
        self.err(msg)

conMsg = ConsoleMessageHandler()

# The setup and teardown stack is a global singleton for convenience;
# there's no reason why it needs to be overridden for testing. The
# convenience has more to do with initializing and passing it around
# than it does anything else.

class SetUpTearDownFileHandler(object):
    def __init__(self, dirName):
        self._firstParseTree = None
        self._lastParseTree = None
        self.dirName = dirName
        if not FG.fsa.isdir(self.dirName): #pragma: no cover # not possible
            return
        self._firstParseTree = self._fetchFile("SetUp")
        self._lastParseTree = self._fetchFile("TearDown")

    def _fetchFile(self, fileName):
        text = self._fetchOneFile(fileName, ".htm")
        text = text or self._fetchOneFile(fileName, ".html")
        if text == "":
            return None
        return self._parseText(text)

    def _fetchOneFile(self, fileName, suffix):
        fileName = FG.fsa.join(self.dirName, fileName + suffix)
        if not FG.fsa.isfile(fileName):
            return ""
        inFile = FG.fsa.open(fileName, "rb")
        text = inFile.read()
        inFile.close()
        return text

    def _parseText(self, text):
        return Parse(text)

class NullSetupFileHandler(SetUpTearDownFileHandler):
    def __init__(self):
        self._firstParseTree = None
        self._lastParseTree = None

class SetUpTearDownStack(object):
    def __init__(self):
        self.theStack = [NullSetupFileHandler()]

    def init(self, options):
        self.theStack = [NullSetupFileHandler()]
        self.options = options

    def push(self, dirName):
        if self.options.doSetUp:
            self.theStack.append(SetUpTearDownFileHandler(dirName))
        else:
            self.theStack.append(NullSetupFileHandler())

    def pop(self):
        del self.theStack[-1]

    def wrapParseTree(self, mainTree):
        if not self.options.doSetUp:
            return mainTree
        resultTree = mainTree
        parseStack = self.theStack[1:]
        parseStack.reverse()
        for entry in parseStack:
            resultTree = self._attachTrees(copy.deepcopy(entry._firstParseTree),
                                           resultTree, retain="last")
            resultTree = self._attachTrees(resultTree,
                            copy.deepcopy(entry._lastParseTree),
                            retain = "first")
        return resultTree

    def _attachTrees(self, firstTree, lastTree, retain="last"):
        if firstTree is None: return lastTree
        if lastTree is None: return firstTree
#        firstTree1stNode = firstTree
        firstTreeLastNode = firstTree.last()
        head1, body1 = self._splitHeaderFromBody(firstTree.leader)
        head2, body2 = self._splitHeaderFromBody(lastTree.leader)
        if retain == "last" and head2 != "":
            firstTree.leader = self._makeNewLeader(head2, body1)
        lastTree.leader = body2
        trailer1 = self._removeEndBody(firstTree.last().trailer)
        lastTree.leader = self._makeNewLeader(trailer1, lastTree.leader)
        firstTreeLastNode.more = lastTree
        firstTreeLastNode.trailer = ""
        return firstTree

    def _splitHeaderFromBody(self, leader):
        lcLeader = leader.lower()
        bodyOffset = lcLeader.find("<body")
        if bodyOffset == -1:
            return "", leader
        endBodyTag = lcLeader.find(">", bodyOffset) + 1
        return leader[:endBodyTag], leader[endBodyTag:]

    def _makeNewLeader(self, head, body):
        if head == "":
            return body
        if body == "":
            return head
        return head + "\n<br>" + body

    def _removeEndBody(self, trailer):
        lcTrailer = trailer.lower()
        endBodyTag = lcTrailer.find("</body")
        if endBodyTag == -1:
            endBodyTag = lcTrailer.find("</html")
        if endBodyTag == -1:
            return trailer
        return trailer[:endBodyTag]

stack = SetUpTearDownStack()    

# The statistics file collector has a single instance of StatsProxy
# bound to the module level stats identifier. The StatsProxy instance,
# in turn, proxies either an instance of StatCollector or NullStatCollector

class StatNode(object):
    def __init__(self, fileName, counts, summary):
        self.fileName = fileName
        self.counts = counts
        self.summary = summary

    def outputAsXML(self, parts, indent):
        parts.append("%s<result><Name>%s</Name>\n" % (indent, self.fileName))
        self.outputCounts(parts, self.counts, indent + "   ")
        self.outputSummary(parts, self.summary, indent + "   ")
        parts.append("%s</result>\n" % indent)

    def outputCounts(self, parts, counts, indent):
        if counts is None:
            return
        parts.append("%s<counts>\n" % indent)
        parts.append('%s   <right>%i</right>\n' % (indent, counts.right))
        parts.append('%s   <wrong>%i</wrong>\n' % (indent, counts.wrong))
        parts.append('%s   <ignores>%i</ignores>\n' % (indent, counts.ignores))
        parts.append('%s   <exceptions>%i</exceptions>\n' % (indent, counts.exceptions))
        parts.append("%s</counts>\n" % indent)

    def outputSummary(self, parts, unused, indent):
        items = self.summary.items()
        items.sort()
        parts.append("%s<summary>\n" % indent)
        for key, value in items:
            parts.append('%s   <item key="%s">%s</item>\n' %
                         (indent, key, value))
        parts.append('%s</summary>\n' % indent)

class StatCollector(object):
    def __init__(self, statFileName):        
        self._outDirName, self._statFileName = FG.fsa.split(statFileName)
        self.dirs = {}

    def reportStats(self, fileName, counts, summary):
        head, tail = FG.fsa.split(fileName)
        fileDir = self.dirs.get(head)
        if fileDir is None:
            fileDir = {}
            self.dirs[head] = fileDir
        fileDir[tail] = StatNode(tail, counts, summary)

    def __str__(self):
#        counts = Counts()
        # XXX did I forget something - like the final counts?
        parts = ['<?xml version="1.0"?>\n',
                 "<testResults><Name>%s</Name>\n" % self._statFileName]
        dirs = self.dirs.items()
        dirs.sort()
        for dirName, fileDir in dirs:
            parts.append("  <Directory>\n"
                         "    <Name>%s</Name>\n" % dirName)
            files = fileDir.items()
            files.sort()
            for fileName, fileObj in files:
                fileObj.outputAsXML(parts, "    ")
            parts.append("  </Directory>\n")
        parts.append("</testResults>\n")
        xmlText = "".join(parts)
        outText = xmlText.encode("UTF-8")
        return outText

    def writeXMLFile(self):
        outPath = FG.fsa.join(self._outDirName, self._statFileName)
        outFile = FG.fsa.open(outPath, "w")
        outFile.write(str(self))
        outFile.close()       

class NullStatCollector(StatCollector):
    def __init__(self): pass
    def reportStats(self, fileName, counts, summary): pass
    def writeXMLFile(self): pass
    def __str__(self):
        return "Null Stat Collector!"

class StatProxy(StatCollector):
    def __init__(self):
        self.stats = NullStatCollector()
    def init(self, statFileName):
        self.stats = StatCollector(statFileName)
    def reportStats(self, fileName, counts, summary):
        self.stats.reportStats(fileName, counts, summary)
    def writeXMLFile(self):
        self.stats.writeXMLFile()
    def __str__(self):
        return str(self.stats)

stats = StatProxy()

# There is a single instance of ConsoleTotals bound to the
# conTotal module level identifier. While the class maintains
# some paramters for convenience it does not need to be
# reinstantiated for testing: it is sufficient to call the
# init method to set new parameters.

class ConsoleTotals(object):
    def __init__(self):
        self.testTotals = "n"
        self.summaryTotals = "n"
        self.runType = "h"
        
    def init(self, testTotals, summaryTotals, file, recursion):
        self.testTotals = testTotals # "y", "e", "n"
        self.summaryTotals = summaryTotals # "f", "t", "n"
        self.runType = file # "h", "d", "l", "r"
        if self.runType == "d":
            if recursion is True:
                self.runType = "r"
        # let's have some sanity here...
        if self.runType == "h":
            self.summaryTotals = "n"
        elif self.runType == "d":
            if self.summaryTotals == "f":
                self.summaryTotals = "t"
        elif self.runType == "r":
            if self.summaryTotals == "t":
                self.summaryTotals = "f"
        conMsg.notes("Result print level in effect. "
                    "Files: '%s' Summaries: '%s'\n" %
                   (self.testTotals, self.summaryTotals))
        self.currDir = None
        self.dirCounts = None
        self.finalCounts = Counts()

        self.lastPrintedDirectoryCounts = None
        self.dirHeaderPrinted = False
        self.newDirectory = True

        self.directorySummariesNeeded = False
        if (self.runType in ("r", "l") and
            self.summaryTotals == "f"):
            self.directorySummariesNeeded = True

    def _captureSummaryCounts(self, path, testCounts):
        if testCounts is None:
            testCounts = Counts(0, 0, 1, 0)
        self.finalCounts.summarize(testCounts)
        dirName, fileName = FG.fsa.split(path)
        if self.currDir != dirName:
            self._printDirectoryTotal()
            self.dirCounts = Counts()
            self.currDir = dirName
            self.dirHeaderPrinted = False
            self.newDirectory = True
        self.dirCounts.summarize(testCounts)

    def _printDirectoryTotal(self):
        if self.dirHeaderPrinted:
            conMsg.stats("Total this Directory: %s"
                     % str(self.lastPrintedDirectoryCounts))
            self.dirHeaderPrinted = False

    def _doDirectoryLines(self, path):
        if not self.directorySummariesNeeded:
            return
        dirName, fileName = FG.fsa.split(path)
        if self.newDirectory:
            head, dirName = FG.fsa.split(dirName)
            conMsg.stats("Processing Directory: %s" % dirName)
            self.lastPrintedDirectoryCounts = self.dirCounts
            self.dirHeaderPrinted = True
            self.newDirectory = False

    def fileResult(self, fileName, counts):
        self._captureSummaryCounts(fileName, counts)
        if self.testTotals == "n":
            return
        if self.testTotals == "e":
            if counts is None:
                return
            if not counts.isError():
                return

        self._doDirectoryLines(fileName)
        if self.runType == 'h':
            fileMsg = ""
        else:
            fileMsg = FG.fsa.basename(fileName)
        if counts is None:
            countMsg = "Run Suppressed by Application Exit"
        else:
            countMsg = str(counts)
        conMsg.stats("%s %s" % (countMsg, fileMsg))

    def finalTotal(self):
        self._printDirectoryTotal()
        if self.summaryTotals != "n":
            conMsg.stats("Total tests Processed: %s" %
                         str(self.finalCounts))
        return self.finalCounts

conTotal = ConsoleTotals()

class ParmEditStatus(object):
    def __init__(self):
        self.status = True

    def __iadd__(self, other):
        if other is False:
            self.status = False
        return self

    def __nonzero__(self):
        return self.status

class FileRunner(RunnerUtilities):
    def __init__(self):
        self._parseTree = None
        self.fixture = Fixture()
        self.command = "FileRunner"
        FG.Environment = "Batch"
        self.inDir = ""
        self.inFile = ""
        self.outDir = ""

    def parms(self, optv):
        self.options = Options(optv, BatchBase.parmDict, "BatchBase")
        # was self._parmDict
        opts = self.options
        FG.RunOptions = opts
        FG.Options = opts
        conMsg.setVerbose(opts.verbose)
        errMsgs = opts.eMsgs
        fileList = opts.posParms
        if not opts.isValid:
            for msg in errMsgs:
                conMsg.err(msg)
            self._usage()
            return False

        if opts.standardsLevel == "":
            FG.SpecificationLevel = "1.1"
        elif opts.standardsLevel != "1.1":
            conMsg.err("Standards level must be 1.1")
            FG.SpecificationLevel = "1.1"
        else:
            FG.SpecificationLevel = opts.standardsLevel

        if opts.standardMode is True:
            if opts.useCSS is True:
                conMsg.err("Standards mode requested. CSS output suppressed")
                opts.useCSS = False

        parmEditOK = ParmEditStatus()
        runType = "?"

        result = self._loadAppConfigurationModule(opts)
        if result is not True:
            conMsg.err(result)
            parmEditOK += False

        if 2 <= len(fileList) <= 3:
            self.inDir = FG.fsa.abspath(fileList[0])
            self.outDir = FG.fsa.abspath(fileList[1])
            statFile = FG.fsa.join(self.outDir, "FitStatistics.xml")
            if FG.fsa.isdir(self.inDir):
                self.inFile = None
                runType = "d"
                self._runObj = DirectoryRunner(self.inDir, self.outDir,
                                               self.options)
                if not FG.fsa.isdir(self.outDir):
                    conMsg.err(
                        "Output must be existing directory for input directory option")
                    parmEditOK += False
            elif (FG.fsa.isfile(self.inDir)):
                self.inFile = self.inDir
                self.inDir, tail = FG.fsa.split(self.inFile)
                root, ext = FG.fsa.splitext(self.inFile)
                if ext == ".txt":
                    if len(fileList) > 2:
                        conMsg.err(
                            "Rename File not allowed for list of files option")
                        parmEditOK += False
                    runType = "l"
                    self._runObj = FileListRunner(self.inFile, self.outDir,
                                                  self.options)
                    if not self.options.isValid:
                        for msg in self.options.eMsgs:
                            conMsg.err(msg)
                        self._usage()
                        return False
                        
                    parmEditOK += FG.appConfigInterface("listOfFilesOptions",
                                          self.options)
                    if not FG.fsa.isdir(self.outDir):
                        conMsg.err(
                            "Output must be existing directory for List of Files option")
                        parmEditOK += False
                else:
                    runType = "h"
                    self._runObj = HTMLRunner(self.inFile, self.outDir,
                                              self.options)
                    statFile = ""
                    head, tail = FG.fsa.split(self.outDir)
                    if not FG.fsa.isdir(head):
                        conMsg.err(
                            "Output directory for result file must exist.")
                        parmEditOK += False
                    else:
                        if FG.fsa.exists(self.outDir) and not FG.fsa.isfile(self.outDir):
                            conMsg.err(
                                "Output for single file option must be a file.")
                            parmEditOK += False
                    
            else:
                conMsg.err("'%s' does not exist!\n" % self.inDir)
                parmEditOK += False

        else:
            conMsg.err("Wrong number of positional parameters\n")
            parmEditOK += False

        # options from the "list of files" have been merged at this point
        parmEditOK += self._extractDiagnosticOptions(opts,
                                        FG.RunDiagnosticOptions)
        result = self._extractRunLevelSymbols(opts,
                                        FG.RunLevelSymbols)
        parmEditOK += result

        if len(fileList) == 3:
            loadOK = self._loadRenameFile(fileList[2])
            if not loadOK:
                conMsg.err("Rename file '%s' failed to load" % fileList[2])
            parmEditOK += loadOK
        else:
            default = FG.fsa.join(self.inDir, "FixtureRenames.txt")
            self._loadRenameFile(default)

        self.runType = runType
        Variations.returnVariation()

        if parmEditOK:
            self._setupStatisticsFile(runType, opts, statFile)
            self._setupConsoleStatisticsPrint(opts, runType)
            stack.init(opts)
            return True

        self._usage()
        return False

    def _usage(self):
        text = __doc__.replace("FileRunner", self.options.runner)
        conMsg.err(text)        

    def _loadRenameFile(self, renameFileName):
#        self._renameFileName = renameFileName
        if not FG.fsa.isfile(renameFileName):
            return False
        valid = True
        try:
            rFile = FG.fsa.open(renameFileName, "rt")
            rList = rFile.readlines()
            rFile.close()
            FixtureLoader.loadFixtureRenameTable(rList)
        except: #pragma: no cover # should't happen - see test above
            valid = False
        return valid

    def _setupStatisticsFile(self, runType, opts, statFileName):
        if not opts.collectStats:
            return
        if runType == "h":            
            conMsg.err("Cannot collect stats on single file")
            opts.collectStats = False
            return
        stats.init(statFileName)    

    def _setupConsoleStatisticsPrint(self, opts, runType):
        opts.filePrintLevel = opts.quietMode[0]
        opts.folderPrintLevel = opts.quietMode[1]
        conTotal.init(opts.filePrintLevel, opts.folderPrintLevel,
                        runType, opts.recursive)

    # main entry point.
    def run(self):
        FG.RunOptions = self.options
        self.pushRunOptionsToTest()
        if not self._runObj.verify():
            return -1
        FG.appConfigInterface("beforeRunExecution")
        self._runObj.run()
        finalTotals = conTotal.finalTotal()
        FG.appConfigInterface("afterRunExecution", finalTotals)
        stats.writeXMLFile()
        return finalTotals.numErrors()

class FileListRunner(RunnerUtilities):
    def __init__(self, inFileName, outDirName, options):
        self.inFileName = inFileName
        self.outDirName = outDirName
        self.options = options

        inFile = FG.fsa.open(self.inFileName, "rt")
        txtFile = inFile.readlines()
        inFile.close()

        self._doOptionSection(txtFile, options)
        self._doFixtureRenamesSection(txtFile)
        self._extractFileList(txtFile)

    def _doOptionSection(self, txtList, options):
        sectionList = self._extractSection(txtList, "[options]")
        optionList = self._makeOptionList(sectionList)
        options.addNewOptions(optionList)
        if not options.isValid:
            return
        if FG.RunAppConfigModule is None:
            self._loadAppConfigurationModule(options)

    def _doFixtureRenamesSection(self, txtList):
        sectionList = self._extractSection(txtList, "[fixture renames]")
        if sectionList:
            FixtureLoader.loadFixtureRenameTable(sectionList)

    def _extractFileList(self, txtList):
        self.fileList = self._extractSection(txtList, "[files]")

    def _extractSection(self, txtList, header):
        result = []
        i = 0
        while i < len(txtList):
            if txtList[i].startswith(header):
                break
            i += 1
        j = i + 1
        while j < len(txtList):
            if txtList[j][0] == "[":
                break
            j += 1
        result = txtList[i+1:j]
        i = 0
        while i < len(result):
            if result[i][0] == "#" or result[i] == "\n":
                del result[i]
                continue
            i += 1
        return result

    def _makeOptionList(self, sectionList):
        result = ["notARunner"]
        for item in sectionList:
            result = result + item.rstrip().split()
        return result

    def verify(self):
        error = False
        head, tail = FG.fsa.split(self.inFileName)
        self.executionList = []
        for line in self.fileList:
            lineList = [x.strip() for x in line.split()]
            optionList = ["notARunner"] + lineList
            newOption = copy.copy(self.options)
            newOption.posParms = []
            newOption.addNewOptions(optionList)
            fileList = newOption.posParms
            if len(fileList) == 0:
                conMsg.err("input file or directory missing in %s" % line)
                error = True
                continue
            if len(fileList) > 2:
                conMsg.err("too many positional parameters in %s" % line)
                error = True
                continue
            path = FG.fsa.join(head, fileList[0])
            if FG.fsa.isfile(path):
                if len(fileList) == 2:
                    inHead, inTail = FG.fsa.split(fileList[0])
                    outHead, outTail = FG.fsa.split(fileList[1])
                    if outTail.find(".") != -1:
                        outDirName = FG.fsa.join(self.outDirName, outHead)
                        outFileName = FG.fsa.join(outDirName, outTail)
                    else:
                        outDirName = FG.fsa.join(self.outDirName, fileList[1])
                        outFileName = FG.fsa.join(outDirName, inTail)
                else:
                    outFileName = FG.fsa.join(self.outDirName, fileList[0])
                    outDirName, outTail = FG.fsa.split(outFileName)
                if not FG.fsa.exists(outDirName):
                    FG.fsa.makedirs(outDirName)
                self.executionList.append(
                    (HTMLRunner(path, outFileName, newOption),
                     newOption))
            elif (FG.fsa.isdir(path)):
                if len(fileList) == 2:
                    outDirName = FG.fsa.join(self.outDirName, fileList[1])
                else:
                    outDirName = FG.fsa.join(self.outDirName, fileList[0])
                if not FG.fsa.exists(outDirName):
                    FG.fsa.makedirs(outDirName)
                self.executionList.append(
                    (DirectoryRunner(path, outDirName, newOption),
                     newOption))
            else:
                conMsg.err("%s does not exist" % path)
                error = True
        return not error

    def run(self):
        for item, opts in self.executionList:
            FG.appConfigInterface("individualTestOptions", opts)
            self.pushRunOptionsToTest()
            result = self.establishTestLevelOptions(opts, [])
            if result is True:
                item.run()
            else:
                conMsg.err(result)
            FG.Options = FG.RunOptions
        return

class DirectoryRunner(object):
    def __init__(self, inDirName, outDirName, options):
        self.inDirName = inDirName
        self.outDirName = outDirName
        self.options = options

#
# --- phase 2 - verify that the directories exist.
#

    def verify(self):
        error = False
        if not FG.fsa.isdir(self.inDirName):
            conMsg.err("%s does not exist or is not a directory!"
                       % self.inDirName)
            error = True
        if not FG.fsa.isdir(self.outDirName):
            conMsg.err("%s does not exist or is not a directory!"
                       % self.outDirName)
            error = True
        return not error

#
# --- Phase 3 --- run
#

    def run(self):
        dirList = FG.fsa.listdir(self.inDirName)
        dirList.sort()
        listOfFiles = []
        listOfDirectories = []
        for item in dirList:
            inFileName = FG.fsa.join(self.inDirName, item)
            # isfile, isdir and stat don't understand the current directory.
            if FG.fsa.isfile(inFileName):
                listOfFiles.append(item)
            else:
                listOfDirectories.append(item)
        if listOfFiles:
            self._doFilesInDirectory(self.inDirName,
                                    self.outDirName, listOfFiles)

        if self.options.recursive and listOfDirectories:
            stack.push(self.inDirName)
            for aDir in listOfDirectories:
                if aDir == "CVS":
                    continue
                newInDir = FG.fsa.join(self.inDirName, aDir)
                newOutDir = FG.fsa.join(self.outDirName, aDir)
                if FG.fsa.isdir(newOutDir):
                    pass
                elif (FG.fsa.exists(newOutDir)):
                    conMsg.err("Cannot create output directory %s;"
                               " file exists with same name" % newOutDir)
                    newOutDir = self.outDirName #reuse current output dir.
                else:
                    FG.fsa.mkdir(newOutDir)
                obj = DirectoryRunner(newInDir, newOutDir, self.options)
                obj.verify() # should't fail
                obj.run()
            stack.pop()
            return
    
    def _doFilesInDirectory(self, inDir, outDir, listOfFiles):
        for aFile in listOfFiles:
            if not self._isFileAcceptable(aFile):
                continue
            inFileName = FG.fsa.join(inDir, aFile)
            outFileName = FG.fsa.join(outDir, aFile)
            obj = HTMLRunner(inFileName, outFileName, self.options)
            obj.verify() # shouldn't fail
            obj.run()
        return

    def _isFileAcceptable(self, fileName):
        head, ext = FG.fsa.splitext(fileName)
        if ext.lower() not in (".html", ".htm"):
            return False
        if head in ("index", "SetUp", "TearDown"):
            return False
        return True    

class HTMLRunner(object):
    def __init__(self, inFileName, outFileName, options):
        self.inFileName = inFileName
        self.outFileName = outFileName
        self.options = options

#
# --------- phase 2 --- verify that the files exist.
#

    def verify(self):
        error = False        
        if not FG.fsa.isfile(self.inFileName):
            conMsg.err("%s does not exist!\n" % self.inFileName)
            error = True
        if FG.fsa.isdir(self.outFileName):
            head, tail = FG.fsa.split(self.inFileName)
            self.outFileName = FG.fsa.join(self.outFileName, tail)
        else:
            head, tail = FG.fsa.split(self.outFileName)
            if not FG.fsa.isdir(head):
                conMsg.err("%s is not a directory!" % head)
                error = True
        return not error

#
# -------- Phase 3 - Run the test.
#

    def run(self):
        FG.inFileName = FG.fsa.abspath(self.inFileName)
        FG.outFileName = FG.fsa.abspath(self.outFileName)
        head, tail = FG.fsa.split(self.inFileName)
        try:
            stack.push(head)
            self.parseTree = self.getParseTree(self.inFileName)
            self.parseTree = stack.wrapParseTree(self.parseTree)
            stack.pop()
        except Exception, e:
            FG.appConfigInterface("beforeTestExecution",
                                        FG.inFileName, e)
            conMsg.err("Unexpected Exception in parsing %s" % FG.inFileName)
            print "Unexpected Exception in parsing %s" % FG.inFileName
            exType, exInfo, exTrace = sys.exc_info()
            traceback.print_exception(exType, exInfo, exTrace,
                                      None, sys.stdout)
            traceback.print_exception(exType, exInfo, exTrace,
                                      None, conMsg)
            conTotal.fileResult(self.inFileName, Counts(0,0,0,1))
            return Counts(0,0,0,1)

        shouldExecute = FG.appConfigInterface("beforeTestExecution",
                                        FG.inFileName, self.parseTree)
        if shouldExecute in (True, None):
            self.fixture = Fixture()
            self.fixture.summary["input file"] = FG.inFileName
            self.fixture.summary["input update"] = FG.fsa.timeUpdated(self.inFileName)
            self.fixture.summary["output file"] = FG.outFileName
            self.fixture.doTables(self.parseTree)
            if self.options.outputEncodingForce:
                self.encoding = self.options.outputEncodingForce
                self.encodingType = "OutputOverride"
            if self.options.useCSS:
                outDir, foo = FG.fsa.split(FG.outFileName)
                self._createFitCSSFile(outDir)
                self._addCSSStuffToHeader(self.parseTree)
            self._fixMetaTag(self.parseTree, self.encoding, self.encodingType)
            textOut = self.parseTree.toString()
            self.write(textOut, self.encoding)
            FG.appConfigInterface("afterTestExecution",
                                         self.fixture.counts,
                                         self.fixture.summary)
            conTotal.fileResult(self.inFileName, self.fixture.counts)
            stats.reportStats(FG.inFileName, self.fixture.counts,
                              self.fixture.summary)
            return self.fixture.counts
        else:
            counts = Counts(0,0,1)
            summary = {}
            summary["input file"] = FG.inFileName
            summary["input update"] = FG.fsa.timeUpdated(self.inFileName)
            summary["output file"] = FG.outFileName
            stats.reportStats(FG.inFileName, None, summary)
            conTotal.fileResult(FG.inFileName, None)
            return counts
#
# -------- Phase 3a - Read the input, decode it to Unicode and parse it.
#

    def getParseTree(self, path):
        theFile = FG.fsa.open(path, "rb")
        text = theFile.read()
        theFile.close()
        decodedText = self._decodeText(text)
        return self._parseText(decodedText)
    
    def _parseText(self, text):
        tag = ("table", "tr", "td")
        if text.find("<wiki>") != -1:
            tag = ("wiki", "table", "tr", "td")
        return Parse(text, tag)

    def _decodeText(self, text):
        encoding = ""
        encodingType = ""
        if text[:3] == "\xef\xbb\xbf":
            encoding, encodingType = "utf-8", "BOM"
        elif text[:2] in ("\xfe\xff", "\x00<"):
            encoding, encodingType = "utf-16be", "BOM"
        elif text[:2] in ("\xff\xfe", "<\x00"):
            encoding, encodingType = "utf-16le", "BOM"
## !!! Python doesn't support utf-32 at the 2.3 level.
##        elif text[:4] in ("\xff\xfe\x00\x00", "<\x00\x00\x00"):
##            encoding, encodingType = "utf-32le", "BOM"
##        elif text[:4] in ("\x00\x00\xfe\xff", "\x00\x00\x00<"):
##            encoding, encodingType = "utf-32ge", "BOM"
        if not encoding and self.options.inputEncodingOverride:
            encoding, encodingType = self.options.inputEncodingOverride, "Forced"
        if not encoding:
            encoding, encodingType = self._encodingFromMetaTag(text)
        if not encoding and self.options.defaultEncoding:
            encoding, encodingType = self.options.defaultEncoding, "Options" # ???
        if not encoding:
            encoding, encodingType = "Windows-1252", "default"
        self.encoding = encoding
        self.encodingType = encodingType
        decodedText = text.decode(encoding) # needs a try/except block.
        if decodedText[0] == u"\ufeff":
            decodedText = decodedText[1:]
        return decodedText

    metaRE = re.compile(r"<meta[ ]+http-equiv=[\"\']content-type[\"\']"
                        "[ ]+content=[\"\']text/html;[ ]+charset=(.+?)"
                        "[\"\'][ ]*/?>", re.I)

    def _encodingFromMetaTag(self, text):
        lc = text.lower()
        match = self.metaRE.search(lc)
        if match is None:
            return "", ""
        result = match.group(1)
        return result, "metaTag"

#
# --------- Phase 3b - write output and clean up.
#

    def write(self, textOut, encoding):
        isUtf = encoding.lower().startswith("utf")
        hasBom = (textOut[0] == u"\ufeff")
        if isUtf and not hasBom:
            textOut = u"\ufeff" + textOut
        elif (not isUtf and hasBom): #pragma: no cover #shouldn't be possible
            textOut = textOut[1:]
        text = textOut.encode(encoding)
        fileObj = FG.fsa.open(self.outFileName, "wb")
        fileObj.write(text)
        fileObj.close()

    def _fixMetaTag(self, table, encodingName, unused='encodingType'):
        if table.leader is None: #pragma: no cover # shouldn't occur
            table.leader = ""
        text = table.leader
        match = self.metaRE.search(text)
        if encodingName in ("utf-16be", "utf-16le"):
            if match is not None:
                text = self._removeMetaEncodingTag(text, match)
                table.leader = text
            return
        if match is None:
            text = self._addMetaEncodingTag(text, encodingName, None)
            table.leader = text
            return
        result = match.groups(1)[0]
        if  encodingName == result:
            return
        text = self._removeMetaEncodingTag(text, match)
        text = self._addMetaEncodingTag(text, encodingName, match)
        table.leader = text
        return None

    def _removeMetaEncodingTag(self, text, match):
        begin, end = match.span()
        return text[:begin] + text[end:]

    headRE = re.compile(r"<head( [^>]*?>|>)", re.I)
    htmlRE = re.compile(r"<html( [^>]*?>|>)", re.I)

    def _addMetaEncodingTag(self, text, encoding, match):
        newTag = ('<meta http-equiv="Content-Type" '
                  'content="text/html; charset=%s">' % encoding)
        if match is not None:
            insertAt = match.start()
        else:
            match = self.headRE.search(text)
            if match is None:
                match = self.htmlRE.search(text)
            if match is None:
                insertAt = 0
            else:
                insertAt = match.end()
        newText = text[:insertAt] + newTag + text[insertAt:]
        return newText

    fitLink = '<link rel="stylesheet" href="FIT.css" type="text/css">\n'

    def _addCSSStuffToHeader(self, table):
        if table.leader is None: #pragma: no cover # shouldn't occur
            table.leader = ""
        lc = table.leader.lower()
        if lc.find("fit.css") != -1:
            return
        endHead = lc.find("</head>")
        if endHead == -1:
            table.leader = "%s%s%s%s" % (
                "<html><head>\n<title>FIT Acceptance Test Dummy Header</title>\n",
                self.fitLink,
                "</head><body>",
                table.leader)
            # XXX need to scan to the end of the table chain and add the
            #     correct ending markup: </body></html>
            return
        table.leader = "%s%s%s%s" % (table.leader[:endHead], "\n",
                                     self.fitLink,
                                     table.leader[endHead:])
        return

    def _createFitCSSFile(self, outDir):
        cssFileName = FG.fsa.join(outDir, "FIT.css")
        try:
            cssFile = FG.fsa.open(cssFileName, 'rt')
            cssFile.close()
            return
        except:
            pass
        cssFile = FG.fsa.open(cssFileName, "wt")
        cssFile.write(cssFileContent)
        cssFile.close()
        return

cssFileContent = """
/**********
 Used in FIT
**********/
.fit_pass {background-color: #cfffcf;}
.fit_fail {background-color: #ffcfcf;}
.fit_error {background-color: #ffffcf;}
.fit_ignore {background-color: #efefef;}
.fit_stacktrace {font-size: 0.7em;}
.fit_label {font-style: italic; color: #c08080;}
.fit_grey {color: #808080;}
.fit_green {color: #80c080;}
"""