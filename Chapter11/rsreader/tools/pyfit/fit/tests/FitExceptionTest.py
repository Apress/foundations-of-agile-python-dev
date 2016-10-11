# test module for FitException
#legalStuff jr04-05
# Copyright 2004-2005 John H. Roth Jr.
# Released under the terms of the General Public License (GPL), Release 2.1 or later
# See license.txt for terms and disclaimer of all warrenties and liability.
# Last updated for Release 0.8a1
#endLegalStuff 

from unittest import makeSuite, TestCase, main

from fit.FitException import FitException, KindOfMessage, TraceWanted
from fit import FitGlobal
from fit import InitEnvironment
from fit.Utilities import em

try:
    False
except: #pragma: no cover
    True = 1
    False = 0

def makeFitExceptionTest():
    theSuite = makeSuite(Test_FitException, 'should')
#    theSuite.addTest(makeSuite(SpecifyFoo, 'should')
    return theSuite

class ExceptionTestAppConfig(object):
    def mapErrorMessage(self, args, unused="isExc", dummy="doTrace"):
        __pychecker__ = 'no-returnvalues'
        if args[0] == "Test003":
            return "It's magic!"
        elif args[0] == "Test002":
            return "Insert lightbulb joke here", TraceWanted("ignore")
        elif args[0] == "Test001":
            return None, TraceWanted("Ignore")
        return None

class Test_FitException(TestCase):
    def setUp(self):
        print '%s %s' % (self.id(), self.shortDescription())
        self.saveAppConfig = (FitGlobal.RunAppConfigModule,
                              FitGlobal.RunAppConfig,
                              FitGlobal.appConfigModule,
                              FitGlobal.appConfig)

    def _setAppConfig(self, parms):
        FitGlobal.RunAppConfigModule, FitGlobal.RunAppConfig, \
            FitGlobal.appConfigModule, FitGlobal.appConfig = parms
        
    def tearDown(self):
        self._setAppConfig(self.saveAppConfig)

    def shouldRetrieveMessageParameters(self):
        e = FitException("Test001", "snark", "bojum")
        isExc, doTrace, msg = e.getMeaningfulMessage()
        assert msg == "For the snark was a bojum, you see."
        assert isExc == KindOfMessage("wrong")
        assert doTrace == TraceWanted("notrace")

    def shouldRetrieveProperMessage(self):
        e = FitException("aMessage",
                        "And he swiftly and silently vanished away")
        assert str(e) == "And he swiftly and silently vanished away"

    def should_badKey(self):
        e = FitException("100tseT", "snark", "bojum")
        result = e.getMeaningfulMessage()
        assert result[2] == "Unknown Message Key: ('100tseT', 'snark', 'bojum')"

    def shouldRaiseExceptionOnBadKindOfMessage(self):
        self.assertRaises(TypeError, KindOfMessage, "fubar")

    def shouldRaiseExceptionOnBadTraceWanted(self):
        self.assertRaises(TypeError, TraceWanted, "fubar")

    def shouldPuntIfNoParameters(self):
        e = FitException()
        assert str(e) == "No arguments to FitException found"

    def shouldHaveTupleArgsForSingleParamter(self):
        e = FitException("Parse001")
        assert len(e.args) == 1

    def shouldGiveMessageForWrongNumberOfParameters(self):
        e = FitException("Test001")
        assert str(e).find("Wrong number of parameters to FitException") > -1

    def shouldHandleStringFromApplicationExit(self):
        self._setAppConfig((ExceptionTestAppConfig, ExceptionTestAppConfig(),
                           ExceptionTestAppConfig, ExceptionTestAppConfig()))
        e = FitException("Test003")
        isExc, doTrace, msg = e.getMeaningfulMessage()
        assert msg == "It's magic!"
        assert isExc == KindOfMessage("exception")
        assert doTrace == TraceWanted("trace")

    def shouldHandleTraceOverrideFromApplicationExit(self):        
        self._setAppConfig((ExceptionTestAppConfig, ExceptionTestAppConfig(),
                           ExceptionTestAppConfig, ExceptionTestAppConfig()))
        e = FitException("Test001", "snark", "bojum")
        isExc, doTrace, msg = e.getMeaningfulMessage()
        assert msg == "For the snark was a bojum, you see."
        assert isExc == KindOfMessage("wrong")
        assert doTrace == TraceWanted("ignore")

    def shouldHandleNewMessageAndTraceFromApplicationExit(self):        
        self._setAppConfig((ExceptionTestAppConfig, ExceptionTestAppConfig(),
                           ExceptionTestAppConfig, ExceptionTestAppConfig()))
        e = FitException("Test002")
        isExc, doTrace, msg = e.getMeaningfulMessage()
        assert msg == "Insert lightbulb joke here"
        assert isExc == KindOfMessage("exception")
        assert doTrace == TraceWanted("ignore")

if __name__ == '__main__':
    main(defaultTest='makeFitExceptionTest')
