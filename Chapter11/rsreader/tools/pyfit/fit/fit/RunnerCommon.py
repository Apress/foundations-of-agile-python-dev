# RunnerCommon
#LegalStuff jr05
# Copyright 2005 John H. Roth Jr.
# Released under the terms of the General Public License (GPL), Release 2.1 or later
# See license.txt for terms and disclaimer of all warrenties and liability.
# Last updated for Release 0.8a1
#endLegalStuff

# This contains a number of classes that are common to both the batch
# and the FitNesse runners. It also contains some test mocks that
# are used by several test modules.

import copy
#import os, os.path
import sys
#import time

from fit import FitGlobal

class RunnerUtilities(object):
    def _extractDiagnosticOptions(self, opts, diagDict):
        for option in opts.diagnosticOptions:
            if option.endswith(".z"): # online FitNesse hack
                option = option[:-2]
            delim = option.rfind(".")
            if delim != -1:
                key = option[:delim]
                value = option[delim+1:]
            else:
                key = option
                value = "true"
            if value.lower() in ("t", "true", "y", "yes", "on"):
                value = True
            elif value.lower() in ("f", "false", "n", "no", "off"):
                value = False
            diagDict[key] = value
        return True

    def _extractRunLevelSymbols(self, opts, diagDict):
        for symbol in opts.runLevelSymbols:
            if symbol.endswith(".sym"): # online FitNesse hack
                symbol = symbol[:-4]
            delim = symbol.rfind(".")
            if delim != -1:
                key = symbol[:delim]
                value = symbol[delim+1:]
            else:
                key = symbol
                value = None
            diagDict[key] = value
        return True

    def _loadAppConfigurationModule(self, opts):
        status = True
        if opts.appConfigurationModule:
            try:
                FitGlobal.RunAppConfigModule = self._import(opts.appConfigurationModule)
                FitGlobal.RunAppConfig = FitGlobal.RunAppConfigModule.defineConfig(opts)
                FitGlobal.appConfigModule = FitGlobal.RunAppConfigModule
                FitGlobal.appConfig = FitGlobal.RunAppConfig
            except Exception:
                status = ("Error loading application configuration module %s"
                                 % opts.appConfigurationModule)
        return status

    def _loadTestLevelAppConfigurationModule(self, opts):
        status = True
        if (opts.appConfigurationModule and
            FitGlobal.RunAppConfigModule is None):
            try:
                FitGlobal.appConfigModule = self._import(opts.appConfigurationModule)
                FitGlobal.appConfig = FitGlobal.appConfigModule.defineConfig(opts)
            except:
                status = ("Error loading application configuration module %s"
                                 % opts.appConfigurationModule)
        return status

    def pushRunOptionsToTest(self):
        FitGlobal.Options = copy.copy(FitGlobal.RunOptions)
        FitGlobal.appConfigModule = FitGlobal.RunAppConfigModule
        FitGlobal.appConfig = FitGlobal.RunAppConfig
        FitGlobal.diagnosticOptions = copy.copy(FitGlobal.RunDiagnosticOptions)
        FitGlobal.topLevelSymbols = copy.copy(FitGlobal.RunLevelSymbols)

    def establishTestLevelOptions(self, opts, pythonPath):
        # need a way to back out changes to the PythonPath
        if pythonPath: #pragma: no cover # fitnesse only.
            sys.path[1:1] = pythonPath
        FitGlobal.Options = opts
        self._extractDiagnosticOptions(opts, FitGlobal.diagnosticOptions)
        self._extractRunLevelSymbols(opts, FitGlobal.topLevelSymbols)
        result = self._loadTestLevelAppConfigurationModule(opts)
        return result

    def _import(self, path):
        parts = path.split(".")
        mod = __import__(path)
        for part in  parts[1:]:
            mod = getattr(mod, part)
        return mod
