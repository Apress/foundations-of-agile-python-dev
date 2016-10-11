# Options class, used in RunnerImplementation and FitServerImplementation
# copyright 2005, John H. Roth Jr.
# Released under the terms of the GNU General Public License, version 2.0 or higher
# See license.txt for the license and general disclaimer of all liability and warrenties

import codecs
import os, os.path
from fit import SiteOptions
from fit.Utilities import em

try:
    False
except: #pragma: no cover
    False = 0
    True = 1

class Options(object):
    # XXX The defaultRunner parameter is no longer used; it should be
    #     removed when runnerImplementation is updated.
    
    def __init__(self, parmList, optionDict, defaultRunner = "fubar"):
        __pychecker__ = "no-stringiter no-argsused"
        self.posParms = []
        self.eMsgs = []
        self.vMsgs = []
        self.isValid = True
        self.optionDict = optionDict
        # Download the options from SiteOptions into the instance
        # Also build the validOptions string
        self.runner, ext = os.path.splitext(os.path.basename(parmList[0]))
        self.siteOptions = getattr(SiteOptions, self.runner, None)
        if self.siteOptions is None:
            self.siteOptions = getattr(SiteOptions,
                                       optionDict[" defaultRunner"])
        validOpts = ""
        
        for char in "abcdefghijklmnopqrstuvwxyz":
            optName = "option_%s" % char
            optValue = getattr(self.siteOptions, optName, None)
            if optValue is not None:
                optVparm, optVinit = optValue
                if optVinit == []: # !!! get a fresh empty list
                    optVinit = []
                optTableEntry = optionDict.get(char)
                if optTableEntry is not None:
                    setattr(self, optTableEntry[1], optVinit)
                    if optVparm:
                        validOpts += char

        for name in ["fitNesse_Root", "fitNesse_Port", "fitNesse_Host"]:
            value = getattr(self.siteOptions, name, None)
            setattr(self, name, value)

        self.validOpts = validOpts
        self.addNewOptions(parmList)

    def addNewOptions(self, parmList):
        j = 1
        while j < len(parmList):
            aParm = parmList[j]
            if aParm[0] == "+":
                setting = True
            elif aParm[0] == "-":
                setting = False
            else:
                break
            i = 1
            while i < len(aParm):
                parmCode = aParm[i]
                if self.validOpts.find(parmCode) == -1:
                    kind, varName = "$n", None
                else:
                    kind, varName = self.optionDict.get(parmCode, ("$n", None))
                editType = kind[0]
#                editReq = kind[1]
                    
                if editType == "b":
                    setattr(self, varName, setting)
                    self.vMsgs.append("Parameter %s (%s) set to %s" %
                                (parmCode, varName, setting))
                elif editType == "c": # character string
                    j += 1
                    value = parmList[j]
                    setattr(self, varName, value)
                    self.vMsgs.append("Parameter %s (%s) set to %s" %
                                (parmCode, varName, value))
                elif editType == "e":
                    j += 1
                    value = parmList[j]
                    try:
                        codecs.lookup(value)
                        setattr(self, varName, value)
                        self.vMsgs.append("Parameter %s (%s) set to encoding %s" %
                                    (parmCode, varName, value))
                    except LookupError:
                        self.eMsgs.append("'%s' is not a valid encoding" % value)
                        self.isValid = False
                elif editType == "l": # multiple parameter list
                    j += 1
                    value = parmList[j]
                    vList = getattr(self, varName)
                    vList.append(value)
                    setattr(self, varName, vList)
                    self.vMsgs.append("'%s' appended to '%s' list" %
                                      (value, parmCode))
                elif editType == "q": # Console summary level
                    j += 1
                    value = parmList[j].lower()
                    if (len(value) == 2 and value[0] in ("y", "n", "e")
                        and value[1] in ("n", "t", "f")):
                        self.vMsgs.append("Level of results detail set to %s" % value)
                        setattr(self, varName, value)
                    else:
                        self.eMsgs.append("Level of results parameter "
                                     "(q) is invalid: %s" % value)
                        self.isValid = False
                elif editType in "fs":
                    j += 1
                    value = parmList[j]
                    setattr(self, varName, value)
                    self.vMsgs.append("Parameter %s (%s) set to %s" %
                                (parmCode, varName, value))
                elif editType in "p": #pragma: no cover
                    if not setting:
                        setattr(self, varName, False)
                    else:
                        j += 1
                        value = parmList[j]
                        setattr(self, varName, value)
                        self.vMsgs.append("%s will be added to the Python path" %
                                    value)
                else:
                    self.eMsgs.append("Parameter %s not recognized editType: %s"
                                      % (parmCode, editType))
                    self.isValid = False
                i += 1
            j += 1
        while j < len(parmList):
            self.posParms.append(parmList[j])
            j += 1
        return
