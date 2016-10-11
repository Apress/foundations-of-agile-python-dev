# Local File from FitLibrary.differences
#LegalStuff rm5 jr5
#endLegalStuff

import os, os.path
from fit import FitGlobal
from fit.Utilities import em

def LocalFileFactory(aPath):
    __pychecker__ = "no-returnvalues" # pychecker doesn't check superclass??
    if FitGlobal.Environment == "FitNesse":
        return FitNesseLocalFile(aPath)
    return BatchLocalFile(aPath)

class LocalFile(object):
    def _splitAll(self, aPath):
        parts = []
        drive, aPath = os.path.splitdrive(aPath)
        while aPath:
            head, tail = os.path.split(aPath)
            parts = [tail] + parts
            aPath = head
            if head in ("/", "\\"):
                parts = [head] + parts
                break
        if drive:
            parts = [drive] + parts
        return parts

class FitNesseLocalFile(LocalFile):
##    LOCAL_FILES = "/files"
##    FITNESSE_FILES_LOCATION = "FitNesseRoot" + LOCAL_FILES # rel path

    # !!! The invariant here is that the filename always begins
    #     immediately after the files directory - the FitNesseRoot/files/
    #     is added when the full path name is required, and the
    #     files/ is added whenever it's being inserted into HTML.

    def __init__(self, aPath):
        if aPath.startswith("/"): # Hack!!!
            aPath = aPath[1:]
        self.filename = self._toFitNesseLocal(aPath)

    def withSuffix(self, suffix):
        root, ext = os.path.splitext(self.filename)
        aPath = root + "." + suffix
        return FitNesseLocalFile(aPath)

    def getFile(self):
        return os.path.join(FitGlobal.FitNesseUserFiles, self.filename)
##        return os.path.join(self.FITNESSE_FILES_LOCATION, self.filename)

    # FitNesse local references do not begin with files
    # files/ is added to the html version when it's written.
    # The FitNesse path in FitGlobal always ends with FitNesseRoot/files
    def _toFitNesseLocal(self, path):
        aParts = self._splitAll(path)
        fParts = self._splitAll(FitGlobal.FitNesseUserFiles)
        fLast = len(fParts) - 1
        if (len(aParts) > len(fParts) and
                aParts[fLast] == fParts[fLast] and
                aParts[fLast-1] == fParts[fLast-1]):
            parts = aParts[fLast+1:]
        elif aParts[0] == "files":
            parts = aParts[1:]
        elif (aParts[0].endswith(":") or aParts[0] == "/" or
              (len(aParts) > 1 and aParts[1] == "/")):
            raise Exception(
                "Illegal File name for FitNesse local file: '%s'" % path)
        else:
            parts = aParts
        return "/".join(parts)

    def htmlImageLink(self):
        return '<img src="files/%s">' % (self.filename)

    def htmlLink(self):
        head, tail = os.path.split(self.filename)
        return '<a href="files/%s">%s</a>' % (self.filename, tail)

    def __eq__(self, other):
        if not isinstance(other, FitNesseLocalFile):
            return False
        return self.filename == other.filename

    def __ne__(self, other):
        if not isinstance(other, FitNesseLocalFile):
            return False
        return self.filename != other.filename

    def __str__(self):
        return self.filename

    def __repr__(self):
        return "LocalFile[%s]" % self.filename

class BatchLocalFile(LocalFile):
    def __init__(self, aPath):
        parts = self._splitAll(aPath)
        self.filename = "/".join(parts)

    def withSuffix(self, suffix):
        root, ext = os.path.splitext(self.filename)
        aPath = root + "." + suffix
        return BatchLocalFile(aPath)

    def getFile(self):
        return self.filename

    def htmlImageLink(self):
        return '<img src="%s">' % (self.filename)

    def htmlLink(self):
        head, tail = os.path.split(self.filename)
        return '<a href="%s">%s</a>' % (self.filename, tail)

    def __eq__(self, other):
        if not isinstance(other, BatchLocalFile):
            return False
        aPath = self._normalize(self.filename)
        bPath = self._normalize(other.filename)
        return aPath == bPath

    def __ne__(self, other):
        if not isinstance(other, BatchLocalFile):
            return False
        aPath = self._normalize(self.filename)
        bPath = self._normalize(other.filename)
        return aPath != bPath

    def _normalize(self, aPath):
        parts = self._splitAll(aPath)
        try:
            x = parts.index("files")
            parts = parts[x+1:]
        except:
            pass
        return "/".join(parts)

    def __str__(self):
        return self.filename

    def __repr__(self):
        return "LocalFile[%s]" % self.filename
