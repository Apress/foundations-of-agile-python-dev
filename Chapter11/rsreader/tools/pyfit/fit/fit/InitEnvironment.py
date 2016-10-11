# InitEnvironment module from Python FIT
#LegalStuff jr2005
#endLegalStuff

import copy
from fit import FitGlobal as FG
from fit import Variations
from fit.Options import Options
from fit import SiteOptions as SO

if FG.RunOptions is None:
    FG.RunOptions = Options(["FileRunner", "+v"], SO.BatchBase.parmDict)
    FG.Options = FG.RunOptions
    FG.annotationStyleVariation = Variations.returnVariation("Batch")

# following is invoked by many of the test classes in the SetUp routine.
def setupFitGlobalForTests(env, opts=[]):
    # Run Level Globals
    FG.specificationLevel = "1.1"
    FG.Environment = env
    FG.RunAppConfigModule = None
    FG.RunAppConfig = None
    FG.RunDiagnosticOptions = {}
    FG.RunLevelSymbols = {}
    if env == "Batch":
        FG.RunOptions = Options(["FileRunner", "+v"] + opts,
                                SO.BatchBase.parmDict)
    elif env == "FitNesseOnline":
        FG.RunOptions = Options(["FitServer", "+v"] + opts,
                                SO.FitServer.parmDict)
        FG.Environment = "FitNesse"
    elif env == "FitNesseBatch":
        FG.RunOptions = Options(["TestRunner", "+v"] + opts,
                                SO.TestRunner.parmDict)
        FG.Environment = "FitNesse"
    FG.FitNesseRoot = SO.OptionsBase.fitNesse_Root
    # Test Level Globals
    FG.Options = FG.RunOptions
    FG.appConfigModule = FG.RunAppConfigModule
    FG.appConfig = FG.RunAppConfig
    FG.diagnosticOptions = copy.copy(FG.RunDiagnosticOptions)
    FG.annotationStyleVariation = Variations.returnVariation(FG.Environment)
    FG.inFileName = ""
    FG.outFileName = ""
    FG.testLevelSymbols = copy.copy(FG.RunLevelSymbols)
clearFitGlobalForTests = setupFitGlobalForTests
