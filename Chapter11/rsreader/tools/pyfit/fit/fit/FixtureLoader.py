# FixtureLoader, part of Fixture from FIT
#legalStuff cc02 om04 jr03-05
# Original Java version Copyright 2002 Cunningham and Cunningham, Inc.
# Released under the terms of the General Public License (GPL), Release 2.1 or later
# See license.txt for terms and disclaimer of all warrenties and liability.
# Contains changes copyright 2004 by Object Mentor, Inc.
# changes Copyright 2003-2005 John H. Roth Jr.
# Last updated for Release 0.8a1
#endLegalStuff

__pychecker__ = "no-miximport" # from fit. import xxx and import fit
import copy
# import inspect
import sys
import types
from fit.FitException import FitException, raiseIfNone
from fit import FitGlobal
from fit.Utilities import em
# to make sure Fixture.Fixture is there when we need it, and
# avoid an import loop.
import fit

try:
    False
except: #pragma: no cover
    True = 1
    False = 0

class FixtureLoader(object):    
    _fixtureRenameTable = {}
    def __init__(self):
        self._rememberedPackages = copy.copy(["fit"])

    def loadFixture(self, pathToClass, shouldBeAFixture = True):
        self.originalNameRequested = pathToClass
        newPath = FitGlobal.appConfigInterface("mapFixture", pathToClass)
        if newPath is not None:
            pathToClass = newPath
        else:
            if self.isGracefulName(pathToClass):
                pathToClass = self.unGracefulName(pathToClass)
            pathToClass = self._renameFixture(pathToClass)

        parts = pathToClass.split(".")
        if newPath is None and len(parts) == 1:
            for prefix in self._rememberedPackages:
                newParts = prefix.split(".") + parts
                newPath = ".".join(newParts)
                try:
                    result = self._loadModuleIsLastElement(newPath, newParts,
                                              shouldBeAFixture)
                except FitException:
                    continue
                return result
            result = self._loadModuleIsLastElement(pathToClass, parts,
                                                   shouldBeAFixture)
        elif len(parts) == 1:
            result = self._loadModuleIsLastElement(pathToClass, parts,
                                                   shouldBeAFixture)
        else:
            result = self._loadClassIsLastElement(pathToClass, parts,
                                                  shouldBeAFixture)
            packageName = ".".join(parts[:-2])
            if result is None:
                result = self._loadModuleIsLastElement(pathToClass, parts,
                                          shouldBeAFixture)
                packageName = ".".join(parts[:-1])
            self.rememberPackage(packageName)
        return result

    def _loadClassIsLastElement(self, unused, parts, shouldBeAFixture):
        pathToModule = ".".join(parts[:-1])
        className = parts[-1]
        theClass = self._doLoad(parts[:-1], pathToModule, className)
        if theClass is None: # need to load final module
            return None
        self._verifyClassType(theClass, pathToModule, className,
                              shouldBeAFixture)
        return theClass

    def _loadModuleIsLastElement(self, pathToModule, parts, shouldBeFixture):
        className = parts[-1]
        theClass = self._doLoad(parts, pathToModule, className)
        raiseIfNone(theClass, "flClassNotFound", className, pathToModule)
        self._verifyClassType(theClass, pathToModule, className,
                              shouldBeFixture)
        return theClass

    def _doLoad(self, parts, pathToModule, className):
        try:
            result = __import__(pathToModule)
        except ImportError, e:
            msg = str(e)
            self.msgFromImportError = msg
            if msg.startswith("No module named "):
                raise FitException("ModuleNotFound", pathToModule)
            else: #pragma: no cover
                raise
        for comp in parts[1:]:
            result = getattr(result, comp)
        result = getattr(result, className, None)
        if type(result) == types.ModuleType:
            return None
        return result # which may or may not be a class!

##    def _verifyClassExists(self, aClass, pathToModule, className):
##        if aClass is not None:
##            return
##        raise FitException("flClassNotFound", className, pathToModule)
##
    def _verifyClassType(self, aClass, unused, dummy,
                         shouldBeAFixture):
        isItAFixture = issubclass(aClass, fit.Fixture.Fixture)
        if isItAFixture is shouldBeAFixture:
            return
        raise FitException("ClassNotDerivedFromFixture",
                             self.originalNameRequested)
        
    ## Fixture Renames feature #####################

    # This is called from the runners.
    # specifically, the FitNesse runner. I'm getting rid of it.
    # Batch uses the list version.
##    def loadFixtureRenamesFromFile(cls, fileName):
##        fileObj = open(fileName, "rt")
##        renameList = fileObj.readlines()
##        fileObj.close()
##        cls.loadFixtureRenameTable(renameList)
##    loadFixtureRenamesFromFile = classmethod(loadFixtureRenamesFromFile)

    # this is called from the Import fixture.
    def addRenameToRenameTable(self, alias, packageName):
        self._fixtureRenameTable[alias.lower()] = packageName

    def clearFixtureRenameTable(cls):
        table = cls._fixtureRenameTable
        table.clear()
    clearFixtureRenameTable = classmethod(clearFixtureRenameTable)

    # this is called from the runners to (re)initialize the table. 
    def loadFixtureRenameTable(cls, aList):
        table = cls._fixtureRenameTable
        for item in aList:
            if item.startswith("#"):
                continue
            if item.endswith("\n"):
                item = item[:-1]
            key, value = item.split(":")
            table[key.strip()] = value.strip()
    loadFixtureRenameTable = classmethod(loadFixtureRenameTable)
        
    def _renameFixture(self, path):
        # look for exact name match first
        newPath = self._fixtureRenameTable.get(path)
        if newPath is not None:
            return newPath
        # now look for the longest match, component by component
        aDot = len(path)
        while True:
            aDot = path.rfind(".", 0, aDot)
            if aDot == -1:
                break
            oldPrefix = path[:aDot]
            newPrefix = self._fixtureRenameTable.get(oldPrefix)
            if newPrefix is not None:
                newPath = newPrefix + path[aDot:]
                return newPath
        return path

    ## Remembered Packages feature.

    def rememberPackage(self, packageName):
        if packageName == "": #pragma: no cover
            return
        try:
            self._rememberedPackages.index(packageName)
        except ValueError:
            self._rememberedPackages.append(packageName)

    def clearRememberedPackageTable(self):
        self._rememberedPackages = copy.copy(["fit"])

    ## Graceful Names

    def isGracefulName(self, aName):
        if aName.count(".") > 0:
            return False
        return aName.count(" ") != 0

    def unGracefulName(self, aName):
        bName = aName.replace("'", "").title()
        charList = []
        for char in bName:
            if char.isalpha() or char.isdigit() or char == ".":
                charList.append(char)
        return "".join(charList)
    
