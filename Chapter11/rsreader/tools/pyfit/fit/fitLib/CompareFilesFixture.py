# CompareFilesFixture from FitLibrary
#legalStuff rm04 jr05
# Original version Contains code developed by Rick Mugridge.
# University of Auckland, NZ. Copyright 2004 Rick Mugridge.
# Released under the terms of the General Public License (GPL), Release 2.1 or later
# See license.txt for terms and disclaimer of all warrenties and liability.
# changes Copyright 2005 John H. Roth Jr.
# Last updated for Release 0.8a1
#endLegalStuff

import os, os.path
import sys
from fitLib.ListTree import ListTree, Tree, TreeTypeAdapter
from fitLib.DoFixture import DoFixture
from fit.Utilities import em

# Compare files and directories
# See the FixtureFixture specifications for examples

class CompareFilesFixture(DoFixture):
    _typeDict = {"baseDir": "String"}
    OK = ListTree("OK")
    baseDir = ""

    def __init__(self, sut=None):
        self.baseDir = os.getcwd()
#        print "in CompareFilesFixture.__init__ cwd: '%s'" % self.baseDir
        super(CompareFilesFixture, self).__init__(sut)

    # Returns OK if the two directories contain equal directories and files.
    # Otherwise it returns an error message for the mismatches.

    _typeDict["folderSameAs.types"] = [TreeTypeAdapter, "String", "String"]
    _typeDict["directorySameAs.RenameTo"] = "folderSameAs"

    def folderSameAs(self, diryName1, diryName2):
        result = self._dirySameAs(diryName1, diryName2)
        if result != self.OK:
            return result
        else:
            return ListTree(os.path.basename(diryName1))


    # Returns OK if the two files match.
    # Otherwise it returns an error message for the mismatch.
    _typeDict["fileSameAs.types"] = [TreeTypeAdapter, "String", "String"]
    def fileSameAs(self, fileName1, fileName2):
        return self._filesSameAs(fileName1, fileName2)

# ----------- end of externally callable routines ---------------    
# --------- edit checking routines: existance, type, type match -----------

    def _filesSameAs(self, file1, file2):
        f1Status = self._checkStatus(file1)
        f2Status = self._checkStatus(file2)
##        em("\nin _filesSameAs\nfile1: '%s' status: '%s'"
##           "\nfile2: '%s' status: '%s'" %
##           (file1, f1Status, file2, f2Status))
        if f1Status == "dir" and f2Status == "dir":
            return self._dirySame(file1, file2)
        if f1Status == "file" and f2Status == "file":
            return self._filesSame(file1, file2) # should this be error?
        if f1Status == "missing":
            return self._error(file1, "Missing")
        if f2Status == "missing":
            return self._error(file2, "Missing")
        return self._error(file1, "Mismatch: file and folder")

    def _dirySameAs(self, diry1, diry2):
        d1Status = self._checkStatus(diry1)
        d2Status = self._checkStatus(diry2)
##        em("\nin _dirySameAs\ndiry1: '%s' status: '%s'"
##           "\ndiry2: '%s' status: '%s'" %
##           (diry1, d1Status, diry2, d2Status))
        if d1Status == "dir" and d2Status == "dir":
            return self._dirySame(diry1, diry2)
        if d1Status == "file" and d2Status == "file":
            return self._filesSame(diry1, diry2)
        if d1Status == "missing":
            return self._error(diry1, "Missing")
        if d2Status == "missing":
            return self._error(diry2, "Missing")
        return self._error(diry1, "Mismatch: file and folder")

    def _checkStatus(self, fileOrDir):
        path = os.path.join(self.baseDir, fileOrDir)
        if os.path.isdir(path):
            return "dir"
        elif os.path.isfile(path):
            return "file"
        return "missing"

# ---------------- main compare routines ----------------------

    def _dirySame(self, diry1, diry2):
##        em("\nin _dirySame 1: '%s' 2: '%s'" % (diry1, diry2))
        resultTree = ListTree(os.path.basename(diry1))
        anyErrors = False
        surplus = [] # hack to match Java version specification tests.
        d1List = os.listdir(diry1)
        d1List.sort()
        d2List = os.listdir(diry2)
        d2List.sort()
        d1 = 0
        d2 = 0
        while d1 < len(d1List) and d2 < len(d2List):
            d1Base = d1List[d1]
            d2Base = d2List[d2]
            d1Path = os.path.join(diry1, d1Base)
            d2Path = os.path.join(diry2, d2Base)
##            em("--- d1Base: '%s' d2Base: '%s'" % (d1Base, d2Base))
            if d1Base < d2Base:
                d1 += 1
                resultTree.children = self._mismatchError(d1Path, "Missing")
                anyErrors = True
                continue
            if d1Base > d2Base:
                d2 += 1
                surplus.append(self._mismatchError(d2Path, "Surplus"))
                anyErrors = True
                continue
            d1Status = self._checkStatus(d1Path)
            d2Status = self._checkStatus(d2Path)
            if d1Status == "missing":
                anyErrors = True
                resultTree.children = self._error(d1Base, "Missing")
            elif d2Status == "missing":
                anyErrors = True
                resultTree.children = self._error(d2Base, "Missing")
            elif d1Status != d2Status:
                resultTree.children = self._error(d1Base, d2Base,
                                   "Can't compare a folder with a file")
                anyErrors = True
            elif d1Status == "dir":
                if d1Base != "CVS":
                    resultTree.children = self._dirySame(d1Path, d2Path) # recursion
            else:
                filesSameAs = self._filesSame(d1Path, d2Path)
                if filesSameAs == self.OK:
                    resultTree.children = ListTree(self._htmlLink(d1Path))
                else:
                    anyErrors = True
                    resultTree.children = filesSameAs
            d1 += 1
            d2 += 1
        while d1 < len(d1List):
            anyErrors = True
            d1Path = os.path.join(diry1, d1List[d1])
            d1 += 1
            resultTree.children = self._mismatchError(d1Path, "Missing")
        while d2 < len(d2List):
            d2Path = os.path.join(diry2, d2List[d2])
            d2 += 1
            anyErrors = True
            surplus.append(self._mismatchError(d2Path, "Surplus"))
        resultTree._children += surplus
        if anyErrors:
            return resultTree
        return self.OK

    def _mismatchError(self, path, kind):
        result = self._checkStatus(path)
##        em("--- mismatch. path: '%s' kind: '%s' status: '%s'" %
##           (path, kind, result))
        base = os.path.basename(path)
        if result == "dir":
            return self._error(base, "%s folder" % kind)
        else:
            return self._error(base, kind)

    def _filesSame(self, file1, file2):
        if not os.path.exists(file1):
            return self._error(file1, "File doesn't exist")
        if not os.path.exists(file2):
            return self._error(file2, "File doesn't exist")
        f1Len = self._getLen(file1)
        f2Len = self._getLen(file2)
        if f1Len < 0:
            return self._error(file1, "File is inaccessible")
        if f2Len < 0:
            return self._error(file2, "File is inaccessible")
        lengthDifference = f2Len - f1Len
        if lengthDifference > 0:
            return self._error(file1, file2, "File shorter by %s"
                               " bytes than: " % lengthDifference)
        elif lengthDifference < 0:
            return self._error(file1, file2, "File longer by %s"
                               " bytes than: " % abs(lengthDifference))
        return self._compareFiles(file1, file2)

    def _getLen(self, path):
        try:
            length = os.stat(path).st_size
        except:
            length = -1
        return length

    def _compareFiles(self, file1, file2):
        f1Text = self._getFileText(file1)
        f2Text = self._getFileText(file2)
        if f1Text == f2Text:
            return self.OK
        i = 0
        while i < len(f1Text):
            if f1Text[i] != f2Text[i]:
                return self._error(file1, file2,
                    "Files differ at byte position %s" % i)
            i += 1
        return self.OK # should not be possible

    def _getFileText(self, path):
        f1 = open(path, "rb")
        f1Text = f1.read()
        f1.close()
        return f1Text

    def _error(self, file1, file2, msg=None):
        if msg is None:
            msg = file2
            file2 = None
        if file2 is None:
            return ListTree(self._htmlLink(file1),
                                 [ListTree("<i>%s</i>" % msg)])
        else:
            error = self._error(file1, msg)
            error.addChild(ListTree(self._htmlLink(file2)))
            return error

    def _htmlLink(self, path): # don't know what to do with this...
        lastPart = os.path.basename(path)
        return lastPart

##    public static boolean failingTree(ListTree tree) {
##        return tree instanceof ListTreeError;

##class ListTreeError(ListTree):
##    def __init__(self, message, children):
##        
##    public ListTreeError(String message, Tree[] trees) {
##        super(message,trees);
##    }
##    public ListTreeError(String name, List children) {
##        super(name,children);
