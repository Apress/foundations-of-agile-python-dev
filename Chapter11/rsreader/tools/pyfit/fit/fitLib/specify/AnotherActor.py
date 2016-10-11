# AnotherActor from FitLibrary Acceptance Tests
#legalStuff rm03 jr05
# Original version Contains code developed by Rick Mugridge.
# University of Auckland, NZ. Copyright 2003 Rick Mugridge.
# Released under the terms of the General Public License (GPL), Release 2.1 or later
# See license.txt for terms and disclaimer of all warrenties and liability.
# changes Copyright 2005 John H. Roth Jr.
# Last updated for Release 0.8a1
#endLegalStuff

from fit.Fixture import Fixture

class AnotherActor(Fixture):
    _typeDict = {}
    test = None

    def __init__(self, callback=None):
        self.callback = callback

    _typeDict["start"] = "Boolean"    
    def start(self):
        pass

    _typeDict["stop"] = "Boolean"    
    def stop(self):
        pass

    _typeDict["switchBack"] = "Boolean"
    def switchBack(self):
        if self.callback is None:
            raise Exception("Protocol violation with AnotherActor")
        self.callback()

