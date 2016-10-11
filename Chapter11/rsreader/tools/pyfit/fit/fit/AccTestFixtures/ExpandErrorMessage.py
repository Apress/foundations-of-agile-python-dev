# ExpandErrorMessage fixture from Python FIT acceptance test suite
#legalNotices jr05
# Copyright 2005 John H. Roth Jr.
# Released under the terms of the General Public License (GPL), Release 2.1 or later
# See license.txt for terms and disclaimer of all warrenties and liability.
# Last updated for Release 0.8a1
#endLegalNotices

from fit.ColumnFixture import ColumnFixture
from fit.FitException import FitException, KindOfMessage, TraceWanted
from fit.Utilities import em

class ExpandErrorMessage(ColumnFixture):
    _typeDict = {"args": "Tuple",
                 "args.columnType": "given",
                 "exception.RenameTo": "exception2",
                 "exception2": KindOfMessage,
                 "exception.columnType": "result",
                 "Trace": TraceWanted,
                 "Trace.columnType": "result",
                 "Message": "String",
                 "Message.columnType": "result",
                 "notes.columnType": "comment",
                 }

    def args(self, aTuple):
#        em("\nargs: '%s'" % (aTuple,))
        excObj = FitException(*aTuple)
#        em("argsInFitException: '%s'" % (excObj.args,))
        self.exc, self.trace, self.message = excObj.getMeaningfulMessage()
        
    def exception2(self): # Name changed for pychecker override message
        return KindOfMessage(self.exc)

    def Trace(self):
        return TraceWanted(self.trace)

    def Message(self):
        return self.message