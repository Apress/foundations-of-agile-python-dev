# Utility routines and other miscellaney
#LegalStuff jr05
# Copyright 2005 John H. Roth Jr.
# Released under the terms of the General Public License (GPL), Release 2.1 or later
# See license.txt for terms and disclaimer of all warrenties and liability.
# Last updated for Release 0.8a1
#endLegalStuff

# a little gadget that lets me quickly write message to the
# console for debugging.

import sys
from types import StringTypes

def em(msg): #pragma: no cover
    if msg[-1] != "\n":
        msg += "\n"
    sys.stderr.write(msg)

def firstNonNone(*parms):
    for aParm in parms:
        if aParm is not None:
            return aParm
    return parms[-1]

# a parameter parsing routine that's shared among all
# of the runners. Again, it's not anything really fancy,
# but it does allow turning options on and off, which
# is useful.

##def _doParms(obj, parmList):
##    posParms = []
##    errorMessages = []
##    j = 0
##    while j < len(parmList):
##        aParm = parmList[j]
##        if aParm[0] == "+":
##            setting = True
##        elif aParm[0] == "-":
##            setting = False
##        else:
##            break
##        i = 1
##        while i < len(aParm):
##            parmCode = aParm[i]
##            if obj.options.find(parmCode) == -1:
##                kind, varName = None, None
##            else:
##                kind, varName = obj._parmDict.get(parmCode, (None, None))
##            if kind == "s":
##                setattr(obj, varName, setting)
##            elif kind == "p":
##                setattr(obj, varName, parmList[j+1])
##                j += 1
##            else:
##                errorMessages.append("unrecognized option: '%s'\n"
##                                 % parmCode)
##            i += 1
##        j += 1
##    while j < len(parmList):
##        posParms.append(parmList[j])
##        j += 1
##    return errorMessages, posParms

# XXX DRY violation - I could build _strTable from _numList
class FitEnum(object):
    def __init__(self, parm):
        self.value = self._verifyParm(parm)

    def _verifyParm(self, parm):
        if isinstance(parm, StringTypes):
            value = self._strTable.get(parm.lower()[:3])
            if value is not None:
                return value
        elif (isinstance(parm, self.__class__)):
            return parm.value
        elif (isinstance(parm, int)):
            if 0 <= parm < len(self._strTable):
                return parm
        raise TypeError(self._typeErrorMessage(parm))

    def __eq__(self, other):
        return self.value == self._verifyParm(other)

    def __str__(self):
        return self._numList[self.value]

    # The following three items must be overridden by an implementation
    _strTable = {}
    _numList = []
    def _typeErrorMessage(self, parm):
        raise Exception("Unoverridden exception. parm: %s" % parm)