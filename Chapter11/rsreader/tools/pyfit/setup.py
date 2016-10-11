# Distutils setup file.

from distutils.core import setup
from distutils.sysconfig import get_python_lib, get_config_vars
import fnmatch
import os, os.path
import sys

# Thanks to Martin Fuzzey for the following two def's 
# and the associated logic elsewhere.

def destDir(*elements):
    return os.path.join(get_python_lib(), "fit", *elements)

def findDataFiles(destRoot, sourceRoot, include=("*",), exclude=("*.py", "*.py?",)):
    def matchesSomePattern(f, patterns):
        for pattern in patterns:
            if fnmatch.fnmatch(f, pattern):
                return True
        return False

    dataFiles = []
    sourceRootLen = len(sourceRoot)
    for root, dirs, files in os.walk(sourceRoot):
        dest = destRoot + root[sourceRootLen:]
        filesToInstall = []
        for f in files:
            if matchesSomePattern(f, exclude):
                continue
            if matchesSomePattern(f, include):
                filesToInstall.append(os.path.join(root, f))                    
        dataFiles.append((dest, filesToInstall))
    return dataFiles

# patch distutils if it can't cope with the "classifiers" or
# "download_url" keywords
if sys.version < '2.2.3':
    from distutils.dist import DistributionMetadata
    DistributionMetadata.classifiers = None
    DistributionMetadata.download_url = None

dataFiles = []
dataFiles.extend(findDataFiles(destDir(), "fit"))
dataFiles.extend(findDataFiles(destDir("fit/AccTests"), "fit/fit/AccTests"))
dataFiles.extend(findDataFiles(destDir("Doc"),  "fit/Doc"))
dataFiles.extend(findDataFiles(destDir("DocSource"),  "fit/DocSource"))
dataFiles.extend(findDataFiles(destDir("distdoc"),  "fit/distdoc"))
dataFiles.extend(findDataFiles(destDir("eg/music"),  "fit/eg/music"))
dataFiles.extend(findDataFiles(destDir("fat"),  "fit/fat"))
dataFiles.extend(findDataFiles(destDir("fitLib"),  "fit/fitLib"))
dataFiles.extend(findDataFiles(destDir("tests"),  "fit/tests"))

def fixLineEndings(fileName):
    if os.linesep == "\r\n":
        return
    path = os.path.join(os.getcwd(), fileName)
    inFile = open(path, "rb")
    text = inFile.read()
    text.replace("\r\n", os.linesep)
    inFile.close()
    outFile = open(path, "wb")
    outFile.write(text)
    outFile.close()

if sys.argv[1] == "install":
    fixLineEndings("fit/FileRunner.py")
    fixLineEndings("fit/WikiRunner.py")
    fixLineEndings("fit/FitServer.py")
    fixLineEndings("fit/TestRunner.py")
    fixLineEndings("fit/HtmlRunner.py")
    fixLineEndings("fit/FolderRunner.py")
    fixLineEndings("fit/FitFilter.py")
    fixLineEndings("fit/DocSource/FitMakeDocumentation.py")

dist = setup(name="PyFIT",
      version="0.8a2",
      # ??? why do I have to list all subpackages individually ?
      packages = ["fit", "fit/fit", "fit/fit/AccTestFixtures", 
                  "fit/fat", "fit/fat/Fit1_1Tests",
                  "fit/tests", "fit/eg", "fit/eg/music",
                  "fit/fitnesse", "fit/fitnesse/fixtures", "fit/fitnesse/testutil",
                  "fit/fitLib", "fit/fitLib/specify", "fit/fitLib/tests",
                  "fit/DocSource"],
      author = "John Roth",
      author_email = "PyFit_maintainer@jhrothjr.com",
      maintainer = "John Roth",
      maintainer_email = "PyFit_maintainer@jhrothjr.com",
      url = "http://fit.c2.com",
      description = "Python language port of FIT",
      long_description =
          """ FIT is an acceptance test package originally written in Java
              by Ward Cunningham and ported to Python by Simon Michael. This
              release brings the code up to Java version 1.1 at
              fit.c2.com, and also includes changes for and interfaces to
              Object Mentor's Fitnesse package up to the 20050731 release.
              It incudes most of Rick Mugridge's FitLib package as well.
              It can be downloaded from the Python Cheese Shop.
              0.8a2 is mostly a bug fix release, although it contains one
              new feature; see the changelog for details.
          """,
      classifiers = ["Development Status :: 4 - Beta", 
                     "Environment :: Console", 
                     "Environment :: Web Environment", 
                     "Intended Audience :: Developers",
                     "Intended Audience :: Other Audience",
                     "License :: OSI Approved :: GNU General Public License (GPL)",
                     "Natural Language :: English",
                     "Operating System :: OS Independent",
                     "Programming Language :: Python",
                     "Topic :: Software Development :: Testing",
                    ],
      scripts=["fit/FileRunner.py", "fit/WikiRunner.py", 
               "fit/FitServer.py", "fit/TestRunner.py",
               "fit/HtmlRunner.py", "fit/FolderRunner.py",
               "fit/DocSource/FitMakeDocumentation.py"],
      data_files = dataFiles,
      )

#cmds = "\n".join(["%s" % key for key in dist.command_obj.keys()])
#sys.stderr.write(cmds)

def createDirectory(path):
    if not os.path.exists(path):
        os.mkdir(path)

def copyScript(outPath):
    scriptDir = dist.command_obj["install"].install_scripts
    inPath = os.path.join(scriptDir, os.path.basename(outPath))
    inFile = open(inPath, "rb")
    text = inFile.read()
    inFile.close()
    outFile = open(destDir(outPath), "wb")
    outFile.write(text)
    outFile.close()

if sys.argv[1] == "install":
#    sys.stderr.write("in install\n")
    createDirectory(destDir("fat/Reports"))
    createDirectory(destDir("fat/Reports/footnotes"))
    createDirectory(destDir("fit/Results"))
    createDirectory(destDir("fitLib/testFiles/emptyDiry"))
    createDirectory(destDir("fitLib/testFiles/alsoEmptyDiry"))
    createDirectory(destDir("fitLib/testFiles/selfDiry"))
    createDirectory(destDir("fitLib/testFiles/diry6/emptyFolder"))
    createDirectory(destDir("fitLib/tests/Results"))
    createDirectory(destDir("tests/testout"))

#    sys.stderr.write(dist.command_obj["install"].install_scripts)
    copyScript("FileRunner.py")
    copyScript("WikiRunner.py")
    copyScript("FitServer.py")
    copyScript("TestRunner.py")
    copyScript("HtmlRunner.py")
    copyScript("FolderRunner.py")
    copyScript("FitFilter.py")
    copyScript("DocSource/FitMakeDocumentation.py")

    cmd2Text = "@echo off\nset PYTHONPATH=%s\n" % destDir()
    cmd2File = open(destDir("tests", "cmd2.cmd"), "wt")
    cmd2File.write(cmd2Text)
    cmd2File.close()

    pthText = destDir() + "\n"
    pthDir = os.path.dirname(pthText)
    pthFile = open(os.path.join(pthDir, "fit.pth"), "wt")
    pthFile.write(pthText)
    pthFile.close()
