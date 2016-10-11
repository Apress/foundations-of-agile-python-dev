# DotGraphic from FitLibrary
#legalStuff rm05 jr05
# Original version Contains code developed by Rick Mugridge.
# University of Auckland, NZ. Copyright 2005 Rick Mugridge.
# Released under the terms of the General Public License (GPL), Release 2.1 or later
# See license.txt for terms and disclaimer of all warrenties and liability.
# changes Copyright 2005 John H. Roth Jr.
# Last updated for Release 0.8a1
#endLegalStuff

import os, os.path
import random
import types
from fit.FitException import FitException
from fit import FitGlobal
from fit.Utilities import em
from fitLib import LocalFile

## Used to check that the Dot file associated with the GIF matches the
## expected Dot file contents.
## It assumes that Dot is installed, as it runs it to produce a GIF
## for an actual value that doesn't match.
## This general approach can be used with any image-making scheme.

class DotGraphic(object):
    _random = random.Random()
    _random.seed()
    _dot = ""

    def __init__(self, aString):
        if isinstance(aString, types.StringTypes):
            self._dot = aString
        elif isinstance(aString, LocalFile.LocalFile):
            self._dot = self.getFileContents(aString) # XXX feature envy!
        else:
            raise FitException("badConstructorType", "DotGraphic",
                               "String or LocalFile", str(type(aString)))

    def parseGraphic(aPath):
        localFile = LocalFile.LocalFileFactory(aPath)
        dotFile = localFile.withSuffix("dot")
        dotPath = dotFile.getFile()
        if not os.path.isabs(dotPath):
            dotPath = os.path.join(os.path.dirname(FitGlobal.inFileName),
                                   dotPath)
        aFile = open(dotPath, "rt")
        text = aFile.read()
        aFile.close()
        return DotGraphic(text)
    parseGraphic = staticmethod(parseGraphic)
        
    def __eq__(self, other):
        if not isinstance(other, DotGraphic):
            return False
        return self._dot == other._dot

    def __ne__(self, other):
        if not isinstance(other, DotGraphic):
            return False
        return self._dot != other._dot

    def toGraphic(self):
        # exception may be here - Java intercepted and rethrew it.
        return self._actualImageFile(self._dot)

    def __str__(self):
        return self.toGraphic().htmlImageLink()

    def _actualImageFile(self, actualDot):
        actuals = "tempActuals"
        actualName = actuals+"/actual"+str(self._random.randint(0, 999999))
        dotFile = self._createTempDotFile(actuals, actualName + ".dot")
        aFile = open(dotFile, "wt")
        aFile.write(actualDot)
        aFile.close()
        imageFileName = os.path.splitext(dotFile)[0] + ".gif"
        imageFile = LocalFile.LocalFileFactory(imageFileName)
        dotCmd = 'dot -Tgif "%s" -o "%s"' % (dotFile, imageFileName)
        curDir = os.getcwd()
        os.chdir("c:/Program Files/ATT/Graphviz/bin")
        os.system(dotCmd)
        os.chdir(curDir)
        return imageFile

    def _createTempDotFile(self, aDir, aFile):
        # FIXME This is scheduled to be rewritten in 0.9 (hope, hope!)
        __pychecker__ = 'no-local'
        if FitGlobal.outFileName != "":
            dirName = os.path.dirname(FitGlobal.outFileName)
##        elif self._localFile is not None:
##            path = self._localFile.getFile()
##            dirName = os.path.dirname(path)
##            if dirName == "":
##                path = os.path.abspath(path)
##                dirName = os.path.dirname(path)
        else:
            dirName = FitGlobal.FitNesseUserFiles
        dirPath = os.path.join(dir, aDir)
        if os.path.isdir(dirPath):
            pass
        elif not os.path.exists(dirPath):
            os.mkdir(dirPath)
        else:
            raise Exception("cannot create .dot file. %s exists" % aDir)
        return os.path.join(dir, aFile)

    def getDot(self, aFile):
        return self.getFileContents(aFile.withSuffix("dot").getFile())

    def getFileContents(self, path):
        theFile = open(path, "rt")
        text = theFile.read()
        theFile.close()
        return text
