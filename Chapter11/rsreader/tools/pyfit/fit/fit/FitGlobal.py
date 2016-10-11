# FitGlobal module for base Python Fit
# Copyright 2005 John H. Roth jr.
# Released under the GNU General Public License, version 2.0 or later

import os, os.path
import time
from fit.Utilities import em

# Global factors that should stay stable for the entire run.
# Most of the contents are NOT part of the API, and WILL change
#  from release to release.

# ---------------------------------------------
# The following identifiers are part of the API
# appConfigInterface(functionName, parameters...)
# getDiagnosticOption(optionName) => option
# RunOptions => Options object 
# ---------------------------------------------

#-------------------------------------------
# The following two identifiers are global objects
# that are used for file system access. Think
# Service Layer. They are set by the tests and
# the runners. They may be used but not changed
# by other components.
#-------------------------------------------

fsa = None # Either FileSystemAdapter or VirtualFileSystem
fss = None # File System Scenario: Batch, FitNesse.FitServer or
           #  FitNesse.TestRunner

#----------------------------------------------
# Run Level variables. These are initialized at
#  the beginning of the run from the runner
#  options and the list-of-files [options] section.
#  They are never reinitialized; they
#  serve as the source for the test level variables
#----------------------------------------------

ReleaseLevel = "0.8a1"
SpecificationLevel = "1.1"
RunOptions = None          # Options object from command and list [options]
Environment = "Batch"      # "FitNesse", "Batch", other IDE environments
RunAppConfigModule = None  # Application Configuration Module
RunAppConfig = None        # instance of AppConfig class
RunDiagnosticOptions = {}  # result of -z parameter
RunLevelSymbols = {}       # Run level symbol table.
FitNesseUserFiles = "C:/fitnesse/FitNesseRoot/files"

# --------------------------------------------------
# Test level variables. They are initialized at the
# beginning of the run to be the same as the run level variables.
# The batch runners, as well as the FitNesse TestRunner
# have different policies about how they get reinitialized.
# --------------------------------------------------

Options = None          # Options object updated with [files] in list runner
appConfigModule = None  # Application Configuration Module
appConfig = None        # instance of AppConfig class
diagnosticOptions = {}  # result of -z parameter
#topLevelSymbols = {}    # top level symbol table.
annotationStyleVariation = None # Strategy object for HTML markup or 2 CSS
inFileName = ""         # fully qualified input file name, FitNesse page
outFileName = ""        # fully qualified output file name, batch and TestRunner
testLevelSymbols = {}   # cleared at the start of each test by Fixture.

def appConfigInterface(serviceName, *parms, **kwds):
    if appConfig is None:
        return None
    method = getattr(appConfig, serviceName, None)
    
    if method:
        result = method(*parms, **kwds)
        return result
    return None

def getDiagnosticOption(option):
    return diagnosticOptions.get(option)

class FileSystemAdapter(object):
    def abspath(self, path): return os.path.abspath(path)
    def basename(self, path): return os.path.basename(path)
    def dirname(self, path): return os.path.dirname(path)
    def exists(self, path): return os.path.exists(path)
    def getcwd(self): return os.getcwd()
    def isdir(self, path): return os.path.isdir(path)
    def isfile(self, path): return os.path.isfile(path)
    def join(self, *paths): return os.path.join(*paths)
    def listdir(self, path): return os.listdir(path)
    def mkdir(self, path): return os.mkdir(path)
    def makedirs(self, path): return os.makedirs(path)
    def open(self, path, mode): return open(path, mode)
    def split(self, path): return os.path.split(path)
    def splitext(self, path): return os.path.splitext(path)
#    def stat(self, path): return os.stat(path)
# following returns wkd mon dd hh:mm:ss yyyy
    def timeUpdated(self, path): return time.ctime(os.stat(path).st_mtime)

fsa = FileSystemAdapter()    
    
