# ImageFixture from FitLibrary. Also ImageNameGraphic and GraphicTypeAdapter
#LegalStuff rm5 jr5
#endLegalStuff

import types
from fit.FitException import FitException
from fitLib.GridFixture import GridFixture
from fitLib.LocalFile import LocalFileFactory, LocalFile
from fit.Utilities import em

class ImageNameGraphic(object):
    expectedFile = None # LocalFile

    def __init__(self, aFile):
        if isinstance(aFile, types.StringTypes):
            self.expectedFile = LocalFileFactory(aFile)
        elif isinstance(aFile, LocalFile):
            self.expectedFile = aFile
        elif isinstance(aFile, ImageNameGraphic):
            self.expectedFile = aFile.expectedFile
        else:
            raise TypeError("argument must be a file name or a LocalFile")

    # !!! this does not verify that the named file exists!
    #     That's intentional.
    def parseGraphic(aPath):
        return ImageNameGraphic(aPath)
    parseGraphic = staticmethod(parseGraphic)

    def toGraphic(self):
        return self.expectedFile

    def __eq__(self, other):
        if not isinstance(other, ImageNameGraphic):
            return False
        return self.expectedFile == other.expectedFile

    def __ne__(self, other):
        if not isinstance(other, ImageNameGraphic):
            return False
        return self.expectedFile != other.expectedFile

    def __str__(self):
        return str(self.expectedFile)

class GraphicTypeAdapter(object):
    fitAdapterProtocol = "RawString"
    def _getClass(self):
        __pychecker__ = 'no-classattr' # metaData, name
        self._class = self.metaData.get("%s.class" % self.name)
        if self._class is None:
            raise FitException("noClassQualifierFor", self.name)

    def parse(self, aString):
        self._getClass()
        imagelink = self.getImageFileName(aString)
        return self._class.parseGraphic(imagelink)

    def toString(self, obj):
        if obj is None:
            return "null"
        return obj.toGraphic().htmlImageLink()

    def equals(self, a, b):
##        em("in GraphicTypeAdapter.equals a: '%s' b: '%s'" %
##           (a.__class__.__name__, b.__class__.__name__))
        self._getClass()
        if isinstance(a, types.StringTypes):
            obj = self.parse(a)
        elif isinstance(a, self._class):
            obj = a
        else:
            return False
        return obj == b

    # XXX very poor HTML parameter extraction routine.
    def getImageFileName(self, aString):
        srcPos = aString.lower().find("src=")
        if srcPos == -1:
            raise FitException("NotImgTag", aString)
        delim = aString[srcPos+4]
        endPos = aString.find(delim, srcPos + 5)
        return aString[srcPos+5: endPos]

class ImageFixture(GridFixture):
    def __init__(self, imageNames):
        grid = []
        for aList in imageNames:
            grid.append([ImageNameGraphic(x) for x in aList])
        self.setGrid(grid)
        self.setTypeAdapter({"name": GraphicTypeAdapter,
                             "name.class": ImageNameGraphic})
