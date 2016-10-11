# Copyright (c) 2002 Cunningham & Cunningham, Inc.
# Read license.txt in this directory.
# Converted to Python 2003/07/24 by John Roth

from fit.Fixture import Fixture
from fit.ActionFixture import ActionFixture
#import MusicPlayer

class Dialog(Fixture):
    _message = ""
    caller = None

    _typeDict = {"message": "String",
                 "ok": "String"}

    def __init__(self, message, caller):
        self._message = message
        self.caller = caller

    def message(self):
        return self._message

    def ok(self):
        if self._message == "load jamed":
            MusicPlayer.stop()
        ActionFixture.actor = self.caller


