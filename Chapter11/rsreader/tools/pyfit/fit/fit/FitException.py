# FitException
#LegalStuff jr04-05
# Copyright 2004-2005 John H. Roth Jr.
# Released under the terms of the General Public License (GPL), Release 2.1 or later
# See license.txt for terms and disclaimer of all warrenties and liability.
# Last updated for Release 0.8a1
#endLegalStuff

from types import StringTypes
from fit import FitGlobal
from fit.Utilities import FitEnum

def exceptionIfNone(test, *exceptionParms):
    if test is None:
        raise FitException(*exceptionParms)
raiseIfNone = exceptionIfNone

def raiseIf(condition, *exceptionParms):
    if condition:
        raise FitException(*exceptionParms)

class KindOfMessage(FitEnum):
    def _typeErrorMessage(self, parm):
        return ("Parameter must be 0, 1, exc or wrong. actual: %s" %
                        (parm,))

    _strTable = {"wro": 0, "exc": 1}

    _numList = ["wrong", "exception"]

class TraceWanted(FitEnum):
    def _typeErrorMessage(self, parm):
        return ("Parameter must be 0, 1, 2, trace, notrace or ignore. actual: %s" %
                        (parm,))

    _strTable = {"not": 0, "tra": 1, "ign": 2}

    _numList = ["notrace", "trace", "ignore"]

EXC = KindOfMessage("exception") # 1
WRONG = KindOfMessage("wrong") # 0
TRACE = TraceWanted("trace") # 1
NOTRACE = TraceWanted("notrace") # 0
IGNORE = TraceWanted("ignore") # 2

class FitException(Exception):
    def getMeaningfulMessage(self):
        __pychecker__ = "no-classattr" # self.args
        args = self.args
        if len(args) == 0:
            args = ("zeroLengthArgs",)
        #
        numParms, isExc, doTrace, template = self.templates.get(args[0],
                                                (None, None, None, None))
        if numParms is None:
            isExc, doTrace = EXC, TRACE
            msg = ("Unknown Message Key. Application Configuration Exit"
                   " did not override it.")

        exitResult = FitGlobal.appConfigInterface("mapErrorMessage", args,
                                              isExc, doTrace)
        #
        if exitResult is None:
            return self.extractEnglishMessage(args)

        if isinstance(exitResult, StringTypes):
            return isExc, doTrace, exitResult

        if exitResult[0] is None:
            isExc, doTrace, msg = self.extractEnglishMessage(args)
            doTrace = exitResult[1]
            return isExc, doTrace, msg

        msg, doTrace = exitResult
        return isExc, doTrace, msg

    def extractEnglishMessage(self, args):
        numParms, isExc, doTrace, template = self.templates.get(args[0],
                                                (None, None, None, None))
        if numParms is None:
            msgValue = self.templates.get("UnknownMessageKey")
            args = ("UnknownMessageKey",) + (args,)
            numParms, isExc, doTrace, template = msgValue
        if len(args) != (numParms + 1):
            result = ("Wrong number of parameters to FitException."
                      " Expected message key plus %s parameters. "
                      "Got: %s Template: %s" % (numParms, args, template))
            isExc, doTrace = EXC, TRACE
        elif len(args) > 1:
            result = template % args[1:]
        else:
            result = template
        return isExc, doTrace, result

    def __str__(self):
        isExc, doTrace, result = self.getMeaningfulMessage()
        return result

    templates = {
     "Test001": (2, WRONG, NOTRACE, "For the %s was a %s, you see."),
     "NoTypeInfo": (2, EXC, NOTRACE,
        "Metadata for '%s' not found in class '%s'"),
     "NoMetadata": (1, EXC, NOTRACE, "No metadata for '%s'"),
     "UnknownType": (1, EXC, TRACE, "Cannot identify type '%s'"),
     "BadParm001": (0, WRONG, NOTRACE,
        "Metadata is required if no instance is supplied"),
     "BadParm002": (1, WRONG, NOTRACE,
        "Class '%s' must be subclass of TypeAdapter"),
     "NoSuchMethod": (2, EXC, NOTRACE,
        "Method '%s' not found in class '%s'"),
     "defaultTANoAttribute": (1, EXC, NOTRACE,
        "Attribute '%s' not found in class for default type adapter"),
     "defaultTAinvalidAdapter": (1, EXC, NOTRACE,
        "Cannot find adapter for '%s'"),
     "descriptorInvalidForDefaultTA": (0, EXC, NOTRACE,
        "Cannot use a descriptor (property) with Default Type Adapter"),
     "WrongNumberOfParameters": (2, WRONG, NOTRACE,
        "Method '%s' in class '%s' has wrong number of parameters"),
     "InvokeField": (0, WRONG, NOTRACE, "You can't invoke a field!"),
     "aMessage": (1, WRONG, NOTRACE, "%s"),
     "anException": (1, EXC, NOTRACE, "%s"),
     # ActionFixture messages
     "missingActorNameCell": (0, EXC, NOTRACE,
        "Row Too Short: Cell containing actor name is missing"),
     "missingMethodNameCell": (0, EXC, NOTRACE,
        "Row Too Short: Cell containing method name is missing"),
     "missingDataCell": (0, EXC, NOTRACE,
        "Row too short: Cell containing data to enter or check missing"),
     "missingMethodName": (0, EXC, NOTRACE, "Method name required. Missing"),
     "missingActor": (0, EXC, NOTRACE,
        "Start Command missing, no actor found"),
     "ActionStart": (0, EXC, NOTRACE, "You must specify a fixture to start."),
     "ActionCheck": (0, EXC, NOTRACE, "You must specify a value to check."),
     "InvalidCommand": (1, WRONG, NOTRACE, "Command '%s' not recognized"),
     # end of ActionFixtureMessages
     "CallSetOnGetter": (0, WRONG, NOTRACE, "Cannot call set on a getter!"),
     "CallGetOnSetter": (0, WRONG, NOTRACE, "Cannot call get on a setter!"),
     "InvokeASetter": (0, WRONG, NOTRACE, "Cannot invoke a setter!"),
     "Parse001": (0, WRONG, NOTRACE, "Add and Subtract only allowed for complex"),
     "Parse002": (1, WRONG, NOTRACE, "Name '%s' not allowed"),
     "Parse003": (1, WRONG, NOTRACE, "Class '%s' not allowed"),
     "BooleanValue": (1, WRONG, NOTRACE, "Invalid Boolean Value: '%s'"),
     "FixtureNotFound": (1, EXC, NOTRACE, 'The fixture "%s" was not found.'),
     "ModuleNotFound": (1, EXC, NOTRACE, "The module '%s' was not found."),
     "PackageError": (1, WRONG, NOTRACE, "'%s' is not a package"),
     "RowTooLong": (0, EXC, NOTRACE,
        "Row is too long<br>This cell is not in a column"),
     "RowTooShort": (0, EXC, NOTRACE, "This row is too short"),
     "ColumnHeadsMissing": (0, EXC, NOTRACE,
        "Row containing column headers is missing"),
     "MissingCell": (1, EXC, NOTRACE, "Missing cell: %s"),
     "IgnoreException": (0, WRONG, IGNORE, "This text should never appear"),
     "PrivateConstructorTest": (0, EXC, NOTRACE, "Simulate a private constructor"),
     "ForcedException": (0, EXC, NOTRACE, "Exception forced for tests"),
     "FieldNotInData": (1, EXC, NOTRACE, "Field '%s' not in input data"),
#                 "ClassNotDerivedFromFixture": (2, EXC, TRACE, "Object '%s' in module '%s' is not derived from Fixture"),
     "ClassNotDerivedFromFixture": (1, EXC, TRACE,
        '"%s" was found, but it\'s not a fixture.'),
     "flClassNotFound": (2, EXC, NOTRACE, "Class '%s' not found in module '%s'"),
     "WrongValueForTypeAdapter": (0, EXC, TRACE,
        "Cell value cannot be handled by type adapter"),
     # Collected exceptions from FitLibrary
     "FitFailureException": (1, EXC, NOTRACE, "%s"),
     "AmbiguousNameFailureException": (1, EXC, NOTRACE, '"%s" is ambiguous'),
     "ExtraCellsFailureException": (0, EXC, NOTRACE, "Extra table cells"),
     "MissingCellsFailureException": (0, EXC, NOTRACE, "Missing table cells"),
     "MissingRowFailureException": (0, EXC, NOTRACE, "Missing row"),
     "NoSuchFieldFailureException": (1, EXC, NOTRACE, "Could not find field: %s."),
     "VoidMethodFitFailureException": (1, EXC, NOTRACE, "method %s is void"),
     "MissingTable": (0, EXC, NOTRACE, "Missing Table"),
     "BooleanMethodFitFailureException": (1, EXC, NOTRACE,
        "Method %s does not return a boolean."),
     "RowIsWrongLength": (0, EXC, NOTRACE, "Row is wrong length"),
     "RowSBxWide": (1, EXC, NOTRACE, "Row should be %s columns wide"),
     "NoGivenColumns": (0, EXC, NOTRACE, "No Given columns in table"),
     "NoCalculatedColumns": (0, EXC, NOTRACE, "No Calculated columns in table"),
     "notImgTag": (1, EXC, NOTRACE, "Not a valid graphic link: %s"),
     "noClassQualifierFor": (1, EXC, NOTRACE, "No %s.class metadata key"),
     # End of collected exceptions from FitLibrary
     "UnknownProtocol": (1, EXC, TRACE,
        "Type Adapter requests invalid ptotocol: '%s'"),
     "CellAccessMissingCell": (0, EXC, TRACE,
        "Cell Access Protocol Requires a parse cell"),
     "SmartDateFormatError": (0, WRONG, NOTRACE, "Smart Date Format error"),
     "UnsupportedCollectionType": (1, EXC, NOTRACE,
        "Collection must be a list, tuple, iterator or dictionary. Found %s"),
     "SymbolNotDefined": (1, EXC, NOTRACE,
        "Parameter '%s' to Row Fixture was not defined by prior fixture."),
     "FieldNotInCollection": (0, EXC, NOTRACE,
        "Field is not in any object in the collection."),
     "InvalidKindForMapLabel": (1, EXC, TRACE,
        "Incorrect parameter '%s' for mapLabel service. check .useToMapLabel metadata"),
     "UnknownColumnType": (2, EXC, NOTRACE,
        "Unknown column type: '%s'. Check %s.columnType metadata"),
     "UnknownMessageKey": (1, EXC, TRACE, "Unknown Message Key: %s"),
     "zeroLengthArgs": (0, EXC, TRACE,
        "No arguments to FitException found"),
     "noRows": (0, EXC, NOTRACE, "This table has no rows!"),
     "noCells": (0, EXC, NOTRACE, "This row has no cells!"),
     "taRejected": (1, EXC, NOTRACE,
        "Type adapter '%s' rejected by application exit"),
     "invRangeExp": (1, EXC, NOTRACE, "Invalid Range Expression: %s"),
     "invEpsilonExp": (1, EXC, NOTRACE, "Invalid Epsilon Expression: %s"),
     "noFloatCheck1": (0, EXC, NOTRACE,
        "Check of single floating value prohibited by standards or "
        "application exit. See documentation for alternatives"),
     "noFloatCheckEpsilon": (0, EXC, NOTRACE,
        "Check of float with epsilon expression prohibited by standards or "
        "application exit. See documentation for alternatives"),
     "noFloatCheckRange": (0, EXC, NOTRACE,
        "Check of float with range expression prohibited by standards or "
        "application exit. See documentation for alternatives"),
     "floatImproperSyntax": (1, EXC, NOTRACE,
        "Improper syntax for float: %s"),
     "badConstructorType": (3, EXC, TRACE,
        "Incorrect constructor type for %s. Expected: %s Found: %s"),
     "invalidCellHandlerType": (2, EXC, NOTRACE,
        "Invalid Type for Cell Handler. type: '%s' value: '%s'"),
     "parseExceptionCHNoValue": (0, EXC, NOTRACE,
        "Exception Cell Handler must have a value when used with a source field"),
     "exceptionCHinvalidSignature": (1, EXC, NOTRACE,
        "Wrong format for parameters to exception cell handler: %s"),
     "exceptionCHUnknownToken": (1, EXC, NOTRACE,
        "Unknown token type in exception cell handler parameters: %s"),
     "exceptionCHParseError": (1, EXC, NOTRACE,
        "Error tokenizing exception cell handler parameters at %s"),
     }
