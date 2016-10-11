# FitServerImplementation From FitNesse
#legalStuff om03-05 jr05
# Original Java version copyright 2003-2005 by Object Mentor, Inc.
# Released under the terms of the General Public License (GPL), Release 2.1 or later
# See license.txt for terms and disclaimer of all warrenties and liability.
# changes Copyright 2005 John H. Roth Jr.
# Last updated for Release 0.8a1
#endLegalStuff

# This consists of all the classes required to implement both the
# FitServer and the TestRunner, other than some general use classes
# from the Fit implementation.

"""
usage: python TestRunner.py [options] host port page-name
+a <module> Application Configuration Exit
+b <parameter> Parameters for Application Configuration Exit
+e only save pages with errors as HTML or raw files.
+f use Fitnesse to format results
+h format results as HTML and save to a file
+o <directory> The directory for raw, HTML and XML statistics
+p <path string> Python path; -p gets path from FitNesse
+r save raw test results to a file.
+t run level symbols
+u <path> List of files (pages) to process
+v (verbose): prints test progress to stdout
+x XML run statistics will be produced
+z <option> Diagnostic options
host - the network address of the host with the FitNesse server
port - the port the FitNesse server is listening on, frequently 80
page-name - the full page name in FitNesse
"""

try:
    False
except: #pragma: no cover
    False = 0
    True = 1

import copy
# import getopt
import os
import socket
import sys
import traceback

from fit.Counts import Counts
from fit import FitGlobal as FG
from fit.Fixture import Fixture
from fit.Options import Options
from fit.Parse import Parse, ParseException
from fit.RunnerCommon import RunnerUtilities
from fit import SiteOptions
from fit import Variations
from fit.Utilities import em, firstNonNone

class MsgWriter(object):
    def setVerbose(self, option):
        self.verbose = option

    def setEnvironment(self, env="FitServer"):
        self.env = env # "FitServer" or "TestRunner"

    def _addNL(self, msg):        
        if msg[-1] != "\n":
            msg += "\n"
        return msg
    
    def emsg(self, msg): # error messages
        sys.stderr.write(self._addNL(msg))

    def err(self, msg):
        sys.stderr.write(self._addNL(msg))

    def smsg(self, msg): # diag messages from FitServer
        if self.env == "TestRunner":
            sys.stderr.write(self._addNL(msg))
        else:
            sys.stdout.write(self._addNL(msg))

    def rmsg(self, msg): # diag messages from TestRunner
        sys.stderr.write(self._addNL(msg))

    def tmsg(self, msg): # trace messages
        sys.stdout.write(self._addNL(msg))

conMsg = MsgWriter()    

class TestMsgWriter(MsgWriter):
    def __init__(self):
        self.msgs = []
    
    def _logMsg(self, msg, pfx):
        self.msgs.append(pfx + self._addNL(msg))
    
    def emsg(self, msg): # error messages
        self._logMsg(msg, "ee: ")

    def smsg(self, msg): # diag messages from FitServer
        self._logMsg(msg, "so: ")

    def rmsg(self, msg): # diag messages from TestRunner
        self._logMsg(msg, "re: ")

    def tmsg(self, msg): # trace messages
        self._logMsg(msg, "to: ")

    def logToStderr(self, id):
        if self.msgs:
            sys.stderr.write("\n------ messages for %s ------\n" % id)
            for msg in self.msgs:
                sys.stderr.write(msg)
            sys.stderr.write("----------------- end of messages -------\n")
        else:
            sys.stderr.write("\n-- no messages for %s --\n" % id)

    def logToStdout(self, id):
        if self.msgs:
            sys.stdout.write("\n------ messages for %s ------\n" % id)
            for msg in self.msgs:
                sys.stdout.write(msg)
            sys.stdout.write("----------------- end of messages -------\n")
        else:
            sys.stdout.write("\n-- no messages for %s --\n" % id)

class FitNesseNetworkInterface(object):
    def __init__(self):
        self.host = "localhost"
        self.port = 80
        self.socketToken = 0

    def getNumArgs(self):
        return 3

##    def getSocketToken(self):
##        return self.socketToken

    def extractParameters(self, parmList):
        self.host = parmList[0]
        self.port, portStatus = self._editInt(parmList[1], "Port Number")
        self.socketToken, tokenStatus = self._editInt(parmList[2], "Request Token")
        return portStatus and tokenStatus, self.host, self.port, self.socketToken

    def _editInt(self, aString, parameterName):
        try:
            result = int(aString)
        except:
            conMsg.emsg("'%s' must be an integer. Is: '%s'" % (parameterName, aString))
            return 0, False
        return result, True

    def connect(self, host, port):
        conMsg.tmsg("in connect. host: '%s' port: '%s'" % (host, port))
        self.host = host
        self.port = port
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((self.host, self.port))
        return None

##    def getInputStream(self):
##        return self
##
##    def getOutputStream(self):
##        return self
##
    def read(self, size):
        resultString = ""
        while len(resultString) < size:
            result = self.socket.recv(size - len(resultString))
            resultString += result
        return resultString.decode("utf-8")

    def write(self, document):
        self.socket.sendall(document)

    def flush(self):
        pass

    def close(self):
        try:
            self.socket.close()
        except:
            # XXX should probably do a bit of diagnosis on this...
            pass
        return None

net = FitNesseNetworkInterface()
netIn = net
netOut = net

class FitNesseTestExecutor(object):

    input = ""
    tables = None # table
    counts = Counts()
    options = None #Option object from Options or TestRunner

    def __init__(self, listener, options):
        self.fixtureListener = listener
        self._renameFileName = ""
        self.options = options
        self.counts = Counts()

    def process(self, renamesFile=""):
        self._renameFileName = renamesFile
        self.fixture = Fixture()
        self.fixture.listener = self.fixtureListener
        self.fixture.listener.runner = self
        try:
            while True:
                try:
                    self._newFixture()
                    size = FitProtocol.readSize(netIn)
                    if not size: break
                    conMsg.tmsg("processing document of size: %s \n" % size)
                    document = FitProtocol.readDocument(netIn, size)
                    firstSep = document.find("\n")
                    if firstSep > -1:
                        docName = document[:firstSep]
                    else:
                        conMsg.emsg("Malformed Document received!. Exiting!")
                        raise Exception("Malformed Document received!")
                    conMsg.tmsg("new document: '%s'" % docName)
                    tables = Parse(document)
                    shouldExecute = FG.appConfigInterface(
                        "beforeTestExecution", docName, tables)
                    if shouldExecute is not False:
##                        outDir = getattr(self.options, "outputDir", None)
##                        if outDir:
##                            docName = docName or "The Test"
##                            FG.outFileName = (
##                                "%s/%s.html" % (outDir, docName))
                        self.fixture.listener.createPage(tables)
                        self.fixture.doTables(tables)
                        self.fixture.listener.writeCounts(
                            self.fixture.counts, self.options.verbose)
                        self.counts += self.fixture.counts
                        FG.appConfigInterface("afterTestExecution",
                                         self.fixture.counts,
                                         self.fixture.summary)
                except ParseException, e:
                    self.handleParseException(e, docName)
            conMsg.tmsg("completion signal received\n")
        except Exception, e:
            self.exception(e)
        return self.counts

    def _newFixture(self):
        fixture = Fixture()
        fixture.listener = self.fixtureListener
        fixture.listener.runner = self
        self._loadRenameFile(fixture, "FixtureRenames.txt")
        self._loadRenameFile(fixture, self._renameFileName)
        self.fixture = fixture
        return fixture

    def _loadRenameFile(self, fixture, renameFileName):
        if not renameFileName:
            return
        try:
            aFile = open(renameFileName, "rt")
            aList = aFile.readlines()
            aFile.close()
            fixture.fixtureLoader.loadFixtureRenameTable(aList)
##            fixture.loadFixtureRenamesFromFile(renameFileName)
        except:
            if renameFileName == "FixtureRenames.txt":
                conMsg.tmsg("Rename file FixtureRenames.txt failed to load")
            else:
                conMsg.emsg("Rename file '%s' failed to load" % renameFileName)

    def handleParseException(self, e, docName):
        excClass, info, tb = sys.exc_info()
        traceList = traceback.format_exception(excClass, info, tb)
        trace = "".join(traceList)
        conMsg.tmsg("Parse exception occurred!: " + trace)
        html = "<table><tr><td>Unable to parse input. Input ignored</td></tr></table>"
        tables = Parse(html)
        tables.leader = docName + "\n" + tables.leader
        self.fixture.exception(tables, e)
        self.fixture.listener.createPage(tables)
        self.counts += self.fixture.counts
        try:
            self.fixture.listener.tableFinished(tables)
            self.fixture.listener.tablesFinished(self.counts)
        except:
            pass
        self.fixture.listener.writeCounts(
            self.fixture.counts, self.options.verbose)
        FG.appConfigInterface("afterTestExecution",
                         self.fixture.counts,
                         self.fixture.summary)
        return

    def exception(self, e):
        excClass, info, tb = sys.exc_info()
        traceList = traceback.format_exception(excClass, info, tb)
        conMsg.emsg("Unexpected Exception occurred!: " + "".join(traceList))
        tables = Parse(tag = "span",
                       body = "Unexpected exception. Unable to continue.")
        self.fixture.exception(tables, e)
        self.counts.exceptions += 1
        try:
            self.fixture.listener.tableFinished(tables)
            self.fixture.listener.tablesFinished(self.counts)
        except:
            pass

    def getCounts(self):
        return self.counts

    def getSummary(self):
        return self.fixture.summary

    def writeCounts(self, unused):
        FitProtocol.writeCounts(self.counts, netOut)

class ServerBase(RunnerUtilities):
    def establishConnection(self, request, host, port):
        bytes = request.encode("UTF-8")
        net.connect(host, port)
        netOut.write(bytes)
        netOut.flush()
        conMsg.tmsg("http request sent\n")

    def validateConnection(self):
        conMsg.smsg("validating connection...")
        statusSize = FitProtocol.readSize(netIn)
        if statusSize == 0:
            conMsg.smsg("...ok\n")
        else:
            errorMessage = FitProtocol.readDocument(netIn, statusSize)
            conMsg.emsg("Connection failed because: %s\n" % errorMessage)
            conMsg.tmsg("An error occured while connecting to client.")
            conMsg.tmsg(errorMessage)
            sys.exit(-1)

    def closeConnection(self):
        net.close()            

    def extractPythonPath(self, pathString, opts):
        # !!! note that this isn't perfect.
        #     it does not handle escape characters
        #     nor path separators inside quotes
        #     nor path separators when the target system has a different
        #      os than the FitNesse server.
        pathString = pathString.replace("'", "")
        pathString = pathString.replace('"', "")
        pathList = pathString.split(os.pathsep)
        pythonPath = []
        renameFileName = ""
        for path in pathList:
            lowerpath = path.lower()
            if (lowerpath.endswith(".jar") or lowerpath.endswith(".class")
                or path.endswith(".*") or lowerpath == "classes"):
                continue
            if lowerpath.endswith(".txt"):
                renameFileName = path
                continue
            if lowerpath.endswith(".sym"):
                opts.runLevelSymbols.append(path[:-4])
                continue
            if (lowerpath.endswith(".true") or lowerpath.endswith(".false")
                or lowerpath.endswith(".z")):
                opts.diagnosticOptions.append(path)
                continue
            if lowerpath.endswith(".std"):
                opts.standardsLevel = path[:-4]
            if lowerpath.endswith(".py"):
                opts.appConfigurationModule = path
                continue
            if lowerpath.endswith(".parm"):
                opts.appConfigurationParms.append(path[:-5])
                continue
            pythonPath.append(path)
        return pythonPath, renameFileName

    def establishCommonTopLevelOptions(self, opts, pythonPath):
        # ??? should we avoid adding elements that are already there?
        if pythonPath:
            sys.path[1:1] = pythonPath
        FG.RunOptions = opts
        if opts.standardsLevel in ("1.1", "2.0"):
            FG.SpecificationLevel = opts.standardsLevel
        self._extractDiagnosticOptions(opts, FG.RunDiagnosticOptions)
        self._extractRunLevelSymbols(opts, FG.RunLevelSymbols)
        self._loadAppConfigurationModule(opts)
        Variations.returnVariation()
        return

class FitServer(ServerBase):

    input = ""
    tables = None # table
    counts = Counts()
    options = None #Option object from Options
    socketToken = 0

    def __init__(self):
        self.host = "localhost"
        self.port = 80
        self.fixtureListener = TablePrintingFixtureListener()
        self._renameFileName = ""
        FG.Environment = "FitNesse"
        FG.inFileName = ""
        FG.outFileName = ""
        Variations.returnVariation()
        conMsg.setEnvironment("FitServer")

    def run(self, argv):
        result = self.args(argv)
        if not result:
            return result
        self.establishCommonTopLevelOptions(self.options,
                                            self._addToPythonPath)
        self.establishConnection(self._makeHttpRequest(),
                                 self.host, self.port)
        self.validateConnection()
        FG.appConfigInterface("beforeRunExecution")
        self.executor = FitNesseTestExecutor(
            TablePrintingFixtureListener(),
            self.options)
        self.counts = self.executor.process(self._renameFileName)
        FG.appConfigInterface("afterRunExecution", self.counts)
        self.closeConnection()
        self.exit()
        return self.exitCode()

    def args(self, argv):
        self.options = Options(argv, SiteOptions.FitServer.parmDict)
        FG.CommandOptions = self.options
        opts = self.options
        errMsgs = opts.eMsgs
        vMsgs = opts.vMsgs
        pos = opts.posParms
        if not opts.isValid:
            for aMsg in errMsgs:
                conMsg.emsg(aMsg)
            self.usage()
            return False

        numIOArgs = net.getNumArgs() # may be testing mock.
        self._renameFileName = ""
        self._addToPythonPath = []
        if len(pos) == numIOArgs + 1:
            self._addToPythonPath, self._renameFileName = (
                self.extractPythonPath(pos[0], opts))
            pos = pos[1:]
        if len(pos) != numIOArgs:
            conMsg.emsg("wrong number of positional parameters")
            self.usage()
            return False
        fitnesseParmStatus, self.host, self.port, self.socketToken = net.extractParameters(pos)
        if fitnesseParmStatus is False:
            self.usage()
            return False
        conMsg.setVerbose(opts.verbose)
        if opts.verbose:
            for aMsg in vMsgs:
                conMsg.smsg(aMsg)
        return True

    # !!! code duplication with SiteOptions.FitServer.parmDict
    def usage(self):
        conMsg.emsg("usage: python FitServer [-v] [PythonPath] host port socketTicket\n")
        conMsg.emsg("\t-v - verbose\n")
        conMsg.emsg("\tThis only runs from the FitNesse server!\n")
        conMsg.emsg("\tIt does not run from the command line\n")

    def exit(self):
        conMsg.smsg("exiting\n")
        conMsg.smsg(str(self.counts))

    def exitCode(self):
        return self.counts.numErrors()
    
    def _makeHttpRequest(self):
        return ("GET /?responder=socketCatcher&ticket=%s HTTP/1.1\r\n\r\n"
                % self.socketToken)

##    def getCounts(self):
##        return self.counts
##
##    def writeCounts(self, count):
##        FitProtocol.writeCounts(self.counts, netOut)
##
class TablePrintingFixtureListener(object):
    runner = None # dependency injected by FitServer._newFixture

    def createPage(self, table):
        return

    def tablesStarted(self, table):
        return

    def tableFinished(self, table):
        try:
            bytes = table.oneHTMLTagToString() # returns string, not UTF-8 encoded
            if len(bytes) > 0:
                FitProtocol.writeData(bytes, netOut)
        except IOError:
            errClass, info, tb = sys.exc_info()
            traceList = traceback.format_exception(errClass, info, tb)
            conMsg.tmsg("".join(traceList))

    def tablesFinished(self, count):
        try:
            FitProtocol.writeCounts(count, netOut);
        except IOError:
            errClass, info, tb = sys.exc_info()
            traceList = traceback.format_exception(errClass, info, tb)
            conMsg.tmsg("".join(traceList))

##    # page name may be available, but right now we don't care.
##    def getPageName(self):
##        return ""

    def writeCounts(self, unused, verbose):
        if verbose:
            conMsg.smsg("%s\n" % (str(self.runner.fixture.counts)))

# this class consists entirely of static methods.
# ??? should they be class methods? The class has nothing
#     to offer, but it would slightly simplify the code. I
#     could write self.blah rather than FitProtocol.blah.
class FitProtocol(object):
    def writeData(data, output):
        bytes = data.encode("UTF-8")
        FitProtocol.writeEncoded(bytes, output)
    writeData = staticmethod(writeData)

    def writeEncoded(bytes, output):
        length = len(bytes)
        FitProtocol.writeSize(length, output)
        output.write(bytes)
        output.flush()
    writeEncoded = staticmethod(writeEncoded)

    def writeSize(length, output):
        lengthBytes = "%010i" % length
        output.write(lengthBytes)
        output.flush()
    writeSize = staticmethod(writeSize)

    def writeCounts(count, output):
        FitProtocol.writeSize(0, output)
        FitProtocol.writeSize(count.right, output)
        FitProtocol.writeSize(count.wrong, output)
        FitProtocol.writeSize(count.ignores, output)
        FitProtocol.writeSize(count.exceptions, output)
    writeCounts = staticmethod(writeCounts)

    def readSize(reader):
        sizeString = reader.read(10)
        if len(sizeString) < 10:
            raise Exception, "A size value could not be read. Fragment='%s'" % sizeString
        else:
            return int(sizeString)
    readSize = staticmethod(readSize)

    def readDocument(reader, size):
        return reader.read(size)
    readDocument = staticmethod(readDocument)

##    def readCounts(reader):
##        counts = Counts()
##        counts.right = FitProtocol.readSize(reader)
##        counts.wrong = FitProtocol.readSize(reader)
##        counts.ignores = FitProtocol.readSize(reader)
##        counts.exceptions = FitProtocol.readSize(reader)
##        return counts
##    readCounts = staticmethod(readCounts)

# container for a single test output.
class PageResult(object):

    _contentBuffer = ""
    _counts = None
    _title = ""
    _isPartOfSuite = True
    _fullPageName = "***unknown***"

    def __init__(self, title):
        self._title = title

    def content(self):
        return self._contentBuffer

    def append(self, data):
        self._contentBuffer += data

    def title(self):
        return self._title

    def counts(self):
        return self._counts

##    def summary(self):
##        return self._runTimes

    def fullPageName(self):
        if self._isPartOfSuite:
            return self._fullPageName + "." + self._title
        else:
            return self._fullPageName

##    def isPartOfSuite(self):
##        return self.isPartOfSuite

    def setTitle(self, title):
        self._title = title

    def setCounts(self, counts):
        self._counts = counts

    def setSummary(self, runTimes):
        self._runTimes = runTimes

    def setFullPageName(self, fullPageName):
        self._fullPageName = fullPageName

    def setIsPartOfSuite(self, isPartOfSuite):
        self._isPartOfSuite = isPartOfSuite
        
    def toString(self):
        return "%s\n%s\n%s" % (self._title, self._counts.toString(),
                             self._contentBuffer)

##    def parse(resultString):
##        result = resultString.split("\n", 2) # maxsplit +1 is # of list elements
##        title, counts, content = result
##        counts = Counts(counts)
##        pageResult = PageResult(title)
##        pageResult.setCounts(counts)
##        pageResult.append(content)
##        return pageResult
##    parse = staticmethod(parse)

class StandardResultHandler(object):
    _pageCounts = Counts()
    currentSuite = ""

    def __init__(self, fullPageName, host, port):
#        self.options = options
        self.fullPageName = fullPageName
        self.host = host
        self.port = port
        self._pageCounts = Counts()

    def acceptResult(self, result):
        opts = FG.Options
        counts = result.counts()
        self._pageCounts.tallyPageCounts(counts)
        if opts.verbose:
            if opts.onlyError is False or counts.isError():
                pageDescription = result.fullPageName()
                parts = pageDescription.split(".")
                left = ".".join(parts[:-1])
                right = parts[-1]
                if left != self.currentSuite:
                    self.currentSuite = left
                    conMsg.rmsg("processing Suite: %s\n" % self.currentSuite)
                conMsg.rmsg("%s %s\n" % (str(counts), right))

        if opts.onlyError is False or counts.isError():
            if opts.rawOutput:
                rawOutputFileName = self.writeRawOutput(result)
            elif opts.HTMLOutput and opts.useFormattingOptions:
                rawOutputFileName = self.writeRawOutputToTempFile(result)
            else:
                rawOutputFileName = ""
            if opts.HTMLOutput:
                self.writeHTMLOutput(result, rawOutputFileName)

    def _pageDescription(self, result):
        description = result.title()
        if description == "":
            description = "The test"
        return description

    def writeRawOutput(self, result):
        middle = self._pageDescription(result)
        pathOut = FG.fsa.join(FG.Options.outputDir, middle + ".raw.txt")
        self._writeRawOutput(result, pathOut)
        return pathOut

    def writeRawOutputToTempFile(self, result):
        pathOut = FG.fsa.join(FG.Options.outputDir, "Temp File.raw.txt")
        self._writeRawOutput(result, pathOut)
        return pathOut

    def _writeRawOutput(self, result, pathOut):    
        text = result.toString().replace("\r", "")
        rawText = "%010i%s%010i%010i%010i%010i%010i" % (len(text),
            text, 0, result.counts().right, result.counts().wrong,
            result.counts().ignores, result.counts().exceptions)
        self._writeOutput(pathOut, rawText, mode="wb")
        return

    def writeHTMLOutput(self, result, rawOutputFileName):
        title = self._pageDescription(result)
        pathOut = FG.fsa.join(FG.Options.outputDir, title + ".html")
        if FG.Options.useFormattingOptions:
            self._invokeFormattingOption(rawOutputFileName, "html",
                pathOut, self.host, self.port, result.fullPageName())
            return
        cssStuff = self.cssStyleTag
        text = (u"<html><head><title>%s</title>\n"
                u'<meta http-equiv="content-type" '
                u'content="text/html; charset=UTF-8">\n'
                u"%s</head><body>\n<h1>%s</h1>\n"
                u"%s\n</body></html>" % (
                    title, cssStuff, title, result.content()))
        self._writeOutput(pathOut, text)

    fitLink = '<link rel="stylesheet" href="%s" type="text/css">\n'
    cssStyleTag = """<style>
    <!--
.pass {	background-color: #AAFFAA; }
.fail {	background-color: #FFAAAA; }
.error { background-color: #FFFFAA; }
.ignore { background-color: #CCCCCC; }
.fit_stacktrace { font-size: 0.7em; }
.fit_label { font-style: italic; color: #C08080; }
.fit_grey {	color: #808080; }
--> </style>\n
"""

    def _invokeFormattingOption(self, pathIn, format, pathOut, host,
                                port, fullPageName):
        cwd = FG.fsa.getcwd()
        fullPathIn = FG.fsa.join(cwd, pathIn)
        fullPathOut = FG.fsa.join(cwd, pathOut) # XXX adjust path for .jar
        cmd = ("java -cp c:/fitnesse/fitnesse.jar "
               'fitnesse.runner.FormattingOption "%s" %s "%s" %s %s %s' %
               (fullPathIn, format, fullPathOut, host, port, fullPageName))
        os.system(cmd)

    def _writeOutput(self, pathOut, text, mode="w"):
        if type(text) == type(u""):
            text = text.encode("utf-8")
        theFile = FG.fsa.open(pathOut, mode)
        theFile.write(text)
        theFile.close()

    def acceptFinalCount(self, count):
        conMsg.rmsg("Test Pages: %s\n" % self._pageCounts)
        conMsg.rmsg("Assertions: %s\n" % count)

##    def getByteCount(self):
##        return 0
##
##    def getResultStream(self):
##        return None

    def cleanUp(self):
        return None

class StatsHandler(object):
    def __init__(self, outDir, suiteName, netName, port):
        self._netName = netName
        self._port = port
        self._outDir = outDir
        self._suiteName = suiteName
        self._pageList = []
        self._text = ""

    def endOfATest(self, title, counts, summary):
        self._pageList.append((title, counts, summary))

    def endOfAllTests(self):
        suiteCount = Counts()
        textList = ['<?xml version="1.0"?>\n',
                    "<testResults>\n",
                    "    <host>%s:%s</host>\n" % (self._netName, self._port),
                    "    <rootPath>%s</rootPath>\n" % self._suiteName,
                    ]
        for pageName, counts, summary in self._pageList:
            textList.append("    <result>\n")
            textList.append("        <relativePageName>\n")
            textList.append("            %s\n" % pageName)
            textList.append("        </relativePageName>\n")
            textList.append("        <counts>\n")
            self._countsToXML(counts, textList, "            ")
            textList.append("        </counts>\n")
            self._summaryToXML(summary, textList)
            textList.append("    </result>\n")
            suiteCount.tallyPageCounts(counts)
        textList.append("    <finalCounts>\n")
        self._countsToXML(suiteCount, textList, "        ")
        textList.append("    </finalCounts>\n")
        textList.append("</testResults>\n")
        self._text = "".join(textList)
        return self._text

    def _countsToXML(self, c, tl, i):
        tl.append("%s<right>%s</right>\n" % (i, c.right))
        tl.append("%s<wrong>%s</wrong>\n" % (i, c.wrong))
        tl.append("%s<ignores>%s</ignores>\n" % (i, c.ignores))
        tl.append("%s<exceptions>%s</exceptions>\n" % (i, c.exceptions))

    def _summaryToXML(self, summary, textList):
        items = summary.items()
        items.sort()
        textList.append("        <summary>\n")
        indent = "            "
        for key, value in items:
            textList.append("%s<item key='%s'>%s</item>\n" %
                            (indent, key, value))
        textList.append("        </summary>\n")

    def writeStats(self):
        if self._outDir == "":
            return
        outFileName = FG.fsa.join(self._outDir, self._suiteName + ".xml")
        outText = self._text.encode("utf-8")
        outFile = FG.fsa.open(outFileName, "wt")
        outFile.write(outText)
        outFile.close()

class TestRunner(ServerBase):
    _host = ""
    _port = 80
    _pageName = ""
    executor = None # fitServer instance
    fixtureListener = None # TestRunnerFixtureListener
    handler = None # StandardResultHandler
    options = None # options object.
    _output = None # printstream

    def __init__(self):
        self.fixtureListener = TestRunnerFixtureListener(self)
        self._statsHandler = None
        FG.Environment = "FitNesse"
        FG.inFileName = ""
        conMsg.setEnvironment("TestRunner")
        Variations.returnVariation()

    def args(self, optv):
        self.options = Options(optv, SiteOptions.TestRunner.parmDict)
        opts = self.options
        conMsg.setVerbose(opts.verbose)
        errMsgs = opts.eMsgs
        pos = opts.posParms
        if not opts.isValid:
            for aMsg in errMsgs:
                conMsg.emsg(aMsg)
            self._usage()
            return False

        if len(pos) == 3 and not opts.listOfFiles:
            self._host, self._port, self._pageName = pos
        elif len(pos) == 2 and opts.listOfFiles:
            self._host, self._port = pos
            self._pageName = ""
        else:
            conMsg.emsg("wrong number of positional arguements\n")
            conMsg.emsg("%s" % pos)
            self._usage()
            return False
        self._port = int(self._port)

        self._pythonPath = ""
        self._renamesFileName = ""
        if self.options.pythonPath:
            self._pythonPath, self._renamesFileName = self.extractPythonPath(
                self.options.pythonPath, copy.copy(opts))

        if opts.outputDir != "":
            if not FG.fsa.isdir(opts.outputDir):
                conMsg.emsg("-o operand '%s' is not a directory\n" %
                            opts.outputDir)
                self._usage()
                return False

        self.listOfFiles = []
        if opts.listOfFiles:
            if not FG.fsa.exists(opts.listOfFiles):
                conMsg.emsg("-u operand '%s' must exist\n" %
                            opts.listOfFiles)
                self._usage()
                return False
            aFile = FG.fsa.open(opts.listOfFiles, "rt")
            self.listOfFiles = aFile.readlines()
            aFile.close()

        if ((opts.rawOutput or opts.stats) and not opts.outputDir):
            conMsg.emsg("No output directory for raw or XML options.\n")
            self._usage()
            return False

        if (opts.HTMLOutput and not opts.outputDir):
            opts.HTMLOutput = False
        self._statsHandler = StatsHandler(opts.outputDir, self._pageName,
                                          self._host, self._port)
        return True

    def _usage(self):
        doc = __doc__
        pgm = FG.fsa.basename(sys.argv[0])
        lines = [x for x in doc.split("\n")
                   if len(x) > 0]
        lines[0] = lines[0].replace("TestRunner.py", pgm)
        conMsg.emsg(lines[0])
        for theLine in lines[1:]:
            conMsg.emsg("\t%s\n" % theLine)

    def run(self, args):
        if not self.args(args):
            return False
        self.handler = StandardResultHandler(self._pageName,
                                             self._host, self._port)
        self.establishCommonTopLevelOptions(self.options, self._pythonPath)
        self.pushRunOptionsToTest()
        self.establishConnection(self.makeHttpRequest(),
                                 self._host, self._port)
        self.validateConnection()
        if not self.options.pythonPath:
            classpathItems = self._processClasspathDocument()
            if classpathItems:
                cpMsg = "Classpath received from server: " + classpathItems
                if self.options.verbose:
                    conMsg.rmsg(cpMsg)
                else:
                    conMsg.tmsg(cpMsg)
            self._pythonPath, renamesFileName = self.extractPythonPath(
                classpathItems, self.options)
            self._renamesFileName = firstNonNone(renamesFileName,
                                                 self._renamesFileName)
            self.pushRunOptionsToTest()
            self.establishTestLevelOptions(self.options, self._pythonPath)
        FG.appConfigInterface("beforeRunExecution")
        self.executor = FitNesseTestExecutor(self.fixtureListener,
                                             self.options)
        result = self.executor.process(self._renamesFileName) 
        FG.appConfigInterface("afterRunExecution", result)
        self._finalCount()
        self.closeConnection()
        self.handler.cleanUp()
        self._statsHandler.endOfAllTests()
        self._statsHandler.writeStats()
        return True

    def _processClasspathDocument(self):
        return self.readDocument()

    def readDocument(self):
        size = FitProtocol.readSize(netIn)
        document = FitProtocol.readDocument(netIn, size)
        return document

    def _finalCount(self):
        self.handler.acceptFinalCount(self.executor.getCounts())

##    def exitCode(self):
##        if self.executor is None:
##            return -1
##        return self.executor.exitCode()

    def makeHttpRequest(self):
        request = "GET /%s?responder=fitClient" % self._pageName
        if not self.options.pythonPath:
            request += "&includePaths=yes"
        return request + " HTTP/1.1\r\n\r\n"

##    def getCounts(self):
##        return self.executor.getCounts()

    def getSummary(self):
        return self.executor.getSummary()

    # This intercepts the PageResult on the way
    # by at the end of processing an individual test.
    # it gives us a chance to do some quick hacks.
    def acceptResults(self, pageResult):
        pageResult.setSummary(self.getSummary())
        pageResult.setFullPageName(self._pageName)
        if pageResult.title() == "":
            name = self._pageName.split(".")
            pageResult.setTitle(name[-1])
            pageResult.setIsPartOfSuite(False)
        counts = pageResult.counts()
#        self.executor.writeCounts(counts) # ???
        self.handler.acceptResult(pageResult)
        self._statsHandler.endOfATest(pageResult.title(),
                                      counts, self.getSummary())

class TestRunnerFixtureListener(object):
    counts = Counts()
    _atStartOfResult = True
    _currentPageResult = None # PageResult
    _runner = None # TestRunner instance

    def __init__(self, runner):
        self._runner = runner
        self._atStartOfResult = True
        self.counts = Counts()

    def createPage(self, table):
        indexOfFirstLineBreak = table.leader.find("\n")
        pageTitle = table.leader[:indexOfFirstLineBreak]
        table.leader = table.leader[indexOfFirstLineBreak + 1:]
        self._currentPageResult = PageResult(pageTitle)
        self._atStartOfResult = False

    def tablesStarted(self, table):
        pass
##        if self._atStartOfResult:
##            indexOfFirstLineBreak = table.leader.find("\n")
##            pageTitle = table.leader[:indexOfFirstLineBreak]
##            table.leader = table.leader[indexOfFirstLineBreak + 1:]
##            self._currentPageResult = PageResult(pageTitle)
##            self._atStartOfResult = False

    def tableFinished(self, table):
        data = table.oneHTMLTagToString().encode("UTF-8")
        self._currentPageResult.append(data)
##        type, info, tb = sys.exc_info()
##        traceList = traceback.format_exception(type, info, tb)
##        conMsg.tmsg("".join(traceList))

    def tablesFinished(self, count):
        self._currentPageResult.setCounts(count)
        self._runner.acceptResults(self._currentPageResult)
        self.counts.tally(count)
        self._atStartOfResult = True
##            type, info, tb = sys.exc_info()
##            traceList = traceback.format_exception(type, info, tb)
##            conMsg.tmsg("".join(traceList))

##    def getPageName(self):
##        parts = self._currentPageResult.fullPageName().split(".")
##        return ".".join(parts[-2:])

    # this is for FitServer, it should be silent for TestRunner
    def writeCounts(self, counts, verbose):
        return
