# RunnerTestCommon
#LegalStuff jr05
# Copyright 2005 John H. Roth Jr.
# Released under the terms of the General Public License (GPL), Release 2.1 or later
# See license.txt for terms and disclaimer of all warrenties and liability.
# Last updated for Release 0.8a1
#endLegalStuff

import os, os.path
from fit.FitGlobal import FileSystemAdapter
import fitnesse.FitServerImplementation as fsi
from fit.Utilities import em

class DummyApplicationExit(object):
    def __init__(self, opts):
        return

applicationExitClass = {}
def defineConfig(opts):
    return applicationExitClass["test1"](opts)

class VirtualFileSystem(FileSystemAdapter):
    def __init__(self):
        self._root = {}

    def abspath(self, path):
        return os.path.normpath(path)

    def isfile(self, path):
        result = self._findFile(path)
        if not result:
            return False
        if result[0] == "file":
            return True
        return False

    def isdir(self, path):
        result = self._findFile(path)
        if not result:
            return False
        if result[0] == "dir":
            return True
        return False

    def exists(self, path):
        result = self._findFile(path)
        if result:
            return True
        return False

    def _splitAll(self, path):
        result = list(os.path.split(path))
        while result[0]:
            result2 = list(os.path.split(result[0]))
            result[:1] = result2
        del result[0]
        if not result[-1]:
            del result[-1]
        return result

    def _findFile(self, path):
        parts = self._splitAll(path)
        theDir = ["dir", self._root, "a date"]
        i = 0
        while i < len(parts):
            if theDir is None: return None
            if theDir[0] != "dir": break
            theDir = theDir[1].get(parts[i])
            i += 1
        return theDir

    def _findDirForLeaf(self, path):
        parts = self._splitAll(path)
        del parts[-1]
        theDir = ["dir", self._root, "a date"]
        i = 0
        while i < len(parts):
            theDir = theDir[1].get(parts[i])
            if theDir is None:
                raise Exception, "path '%s' is too long" % path
            if theDir[0] != "dir":
                raise Exception, "path '%s' conains a non-directory" % path
            i += 1
        return theDir

    def listdir(self, path):
        result = self._findFile(path)
        if result is not None and result[0] == "dir":
            result = result[1].keys()
            return result
        raise Exception, "%s isn't a directory!" % path

    def mkdir(self, path):
        head, tail = os.path.split(path)
        theDir = self._findFile(head)
        if theDir is not None and theDir[0] == "dir":
            theDir[1][tail] = ["dir", {}, "a date"]
        else:
            raise Exception, "%s isn't a directory!" % head

    def makedirs(self, path):
        parts = self._splitAll(path)
        i = 0
        curDir = self._root
        while i < len(parts):
            nextDir = curDir.get(parts[i])
            if nextDir is None: break
            if nextDir[0] != "dir":
                raise Exception, "path '%s' contains a file!" % path
            curDir = nextDir[1]
            i += 1
        if i >= len(parts):
            raise Exception, "path '%s' is full!" % path
        while i < len(parts):
            nextDir = {}
            curDir[parts[i]] = ["dir", nextDir, "a date"]
            curDir = nextDir
            i += 1

    def timeUpdated(self, path):
        theFile = self._findFile(path)
        return theFile[2]

    def _addDirectories(self, *paths):
        for path in paths:
            self.makedirs(path)

    def _addFile(self, path, aList):
        theDir = self._findDirForLeaf(path)
        theDir[1][os.path.basename(path)] = ["file", aList, "a date"]

    def open(self, path, mode):
        if mode[0].lower() == "r":
            theFile = self._findFile(path)
            if theFile is None or theFile[0] != "file":
                raise Exception, "%s isn't a file!" % path
            return MockFileObject(theFile[1])
        head, tail = os.path.split(path)
        theDir = self._findFile(head)
        if theDir is None or theDir[0] != "dir":
            raise Exception, "%s isn't a directory!" % head
        newFile = []
        theDir[1][tail] = ["file", newFile, "a date"]
        return MockFileObject(newFile)

class MockFileObject(object):
    def __init__(self, aList):
        self.aList = aList
        self.filePos = 0

    def close(self):
        return
        
    def read(self):
        if self.filePos < len(self.aList):
            self.filePos = len(self.aList)
            return "".join(self.aList)
        return ""

    def readline(self):
        if self.filePos < len(self.aList):
            self.filePos += 1
            return self.aList[self.filePos - 1]
        return ""

    def readlines(self):    
        if self.filePos < len(self.aList):
            self.filePos = len(self.aList)
            return self.aList
        return []

    def write(self, aString):
        self.aList.append(aString)

    def writeline(self, aString):
        self.aList.append(aString)

    def writelines(self, aList):
        self.aList += aList

class ioMock(fsi.FitNesseNetworkInterface):
    def __init__(self):
        self.listIndex = 0
        self.inputList = []
        self.outputList = []
        self.errorOnWrite = -1
        self.recNumOut = -1

    def connect(self, host, port):
        print "in establishConnection host: '%s' port: '%s'" % (host, port)
        self.host = host
        self.port = port

##    def getInputStream(self):
##        return self
##
##    def getOutputStream(self):
##        return self

    def setErrorOnWrite(self, writeNum):
        self.errorOnWrite = writeNum
        
    def write(self, text):
        print "in write: length: '%s' text: '%s'" % (len(text), text[:50])
        self.outputList.append(text)
        self.recNumOut += 1
        if self.recNumOut == self.errorOnWrite:
            raise IOError(99, "Error raised in testing", "it's a file?")

    def flush(self):
        return None

    def read(self, unused='size'):
        print "in read listIndex: %s" % self.listIndex
        self.listIndex += 1
        return self.inputList[self.listIndex - 1]

    def close(self):
        return None

ft2chunk1 = ("""<h1>
Integer Arithmetic</h1>

<p>The computer relies on arithmetic. Here we test a variety of arithmetic
operations expressed as 32 bit two's complement binary numbers (Java's
int).
<br>&nbsp;
<table BORDER COLS=6 CELLSPACING=0 CELLPADDING=3 >
<tr>
<td COLSPAN="6">eg.ArithmeticFixture</td>
</tr><tr><td>x</td><td>y</td><td>+</td><td>-</td><td>*</td><td>/</td>
</tr><tr>
<td>0</td><td>0</td><td>0</td><td>0</td><td>0</td><td>0</td>
</tr><tr>
<td>1</td><td>2</td><td>3</td><td>-1</td><td>2</td><td>0.5</td>
</tr><tr>
<td>1</td><td>-1</td><td>0</td><td>2</td><td>-1</td><td>-1</td>
</tr><tr>
<td>10000</td><td>10000</td><td>20000</td><td>0</td><td>100000000</td><td>1</td>
</tr><tr>
<td>100000</td><td>100000</td><td>200000</td><td>0</td><td>10000000000</td><td>1</td>
</tr><tr>
<td>1000000</td><td>1000000</td><td>2000000</td><td>0</td><td>1000000000000</td><td>1</td>
</tr>
</table>
<br><br>
The divide by zero exception and the error just under it are
expected. The exception could be avoided, but it's still an
error so there isn't much point in "fixing" it. The error
under it is caused by using integer arithmetic: the quotient
will always be an integer, so it cannot compare equal to 0.5.
<br>
Also, notice that some of the numbers are larger than you
would expect from 32 bit integer arithmetic. That's because
I changed them for the Python version; Python has unlimited
precision integers, and there was no way to duplicate the
hash Java makes of integer overflows.
<br><br>
Now we try something similar using automatic type conversion offered by ColumnFixtures.
<br><br>
<table BORDER CELLSPACING=0 CELLPADDING=3>
    <tr>
        <td colspan=5>eg.ArithmeticColumnFixture</td>
    </tr><tr>
        <td>x</td>
        <td>y</td>
        <td>plus()</td>
        <td>times()</td>
        <td>divide()</td>
        <td>floating()</td>
    </tr>
    <tr>
        <td>2</td>
        <td>3</td>
        <td>5</td>
        <td>6</td>
        <td>0</td>
        <td>0.666667</td>
    </tr>
    <tr>
        <td>0</td>
        <td>0</td>
        <td>0</td>
        <td>0</td>
        <td>error</td>
        <td>error</td>
    </tr>
    <tr>
        <td>0</td>
        <td>0</td>
        <td>0</td>
        <td>0</td>
        <td></td>
        <td></td>
    </tr>
    <tr>
        <td>200</td>
        <td>300</td>
        <td>500</td>
        <td>60000</td>
        <td>0</td>
        <td>0.666667</td>
    </tr>
    <tr>
        <td>2</td>
        <td>3</td>
        <td>10</td>
        <td>10</td>
        <td>10</td>
    </tr>
    <tr>
        <td>200</td>
        <td>3</td>
        <td>5</td>
        <td>6</td>
        <td>0</td>
        <td>0.666667</td>
    </tr>
    <tr>
        <td>2</td>
        <td>-3</td>
        <td>-1</td>
        <td>-6</td>
        <td>-0</td>
        <td>-0.666667</td>
    </tr>
</table>
<br><br>
Several of the errors in this one are planned; the
incorrect values were there originally to show off
the nice red background for an error.
<br>
"error" is a value that will compare to an exception;
that's what the green background with the "error" message
is in the third row. What the ones with the white background
are is another question: I'd expect an exception since there
wasn't any value there originally, but it seems to put
"error" in there anyway.
<br>
The only unexpected error is the one on the last line,
where a zero is expected from a divide, and the actual
result is a -1. This is due to Python's rather unusual
integer divide: it uses "floor division" which means that
the result is the greatest integer less than the actual
result.
<br><br>
<table BORDER CELLSPACING=0 CELLPADDING=3>
<tr>
<td COLSPAN="2">fit.Summary</td>
</tr>
</table>
<p>Document prepaired by Ward Cunningham
<br>First Version July 11, 2002
<br>Last Update August 17, 2002
<br>Notes added by John Roth April 22, 2004
""")
