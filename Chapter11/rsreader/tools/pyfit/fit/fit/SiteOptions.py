# Site Options Module
#LegalStuff jr05
# Copyright 2005 John H. Roth Jr.
# Released under the terms of the General Public License (GPL), Release 2.1 or later
# See license.txt for terms and disclaimer of all warrenties and liability.
# Last updated for Release 0.8a1
#endLegalStuff

# This is where an installation creates installation-wide options.

# The runners, and possibly other modules, import SiteOptions.
# Since the runners get there first, they do the setup by calling
# one of the classes in the module. The initialization routine moves
# everything that looks like an option to the module level, so that
# any interested routine can access it simply by importing SiteOptions
# and then reading the attribute.

# The runner calls the class that has the same name as the runner.
# This class normally inherits from either FitNesseBase or BatchBase.
# Both FitNesseBase and BatchBase inherit from OptionsBase.

# If the runner can't find a class named after itself, it will try to
# initialize either FitNesseBase or BatchBase, as appropriate. If it
# can't do that, it quits with a diagnostic message. Be very careful
# making changes to this module: a compile error will shut everyone down!
# I strongly recommend putting this module under source control and making
# sure that your critical applications will run with any changes you
# make.

# Both the FitNesse and the Batch runners make consistency checks and
# apply defaults after the options are loaded. These routines are in the
# runners, not in this module, so they are not accessable without going
# into the source and changing it. See the comments in front of
# FitNesseBase and BatchBase.

class OptionsBase(object):
    fitNesse_Root = "c:/fitnesse/FitNesseRoot" # the root of the FitNesse directory structure.
    fitNesse_Host = "localhost"
    fitNesse_Port = 80

# There are several critical options. The most critical is
# the standardsMode. If this is True, batch FIT will conform
# to the FIT 1.1 specification. See fat.Fit1_1Tests for the
# spec tests and the fixtures that they use.

# The most important change is that the CSS mode will be set
# to false, and both standards mode and CSS mode will be
# disabled so they cannot be changed from the command line.

# The next most important thing to notice is that recursive
# mode is always available for FolderRunner, and not available
# for runners that process one file at a time. Likewise, the
# single file runners cannot create a stats file.

# The character set options cannot be disabled. They will be
# added back in if you try. You can specify an input default
# and an output default, although the system tends to do the
# right thing if you leave it alone.

class BatchBase(OptionsBase):

    option_a = (True, "")    # Application Configuration Module Name
    option_b = (True, [])    # Application Configuration Parm List
    option_c = (True, True)  # CSS mode
    option_d = (True, "")    # default file encoding
    option_e = (True, False) # standards mode
    option_i = (True, "")    # Input file encoding override
    option_l = (True, "")    # FIT specification level
    option_o = (True, "")    # Output file encoding
    option_q = (True, "yn")  # Quiet mode
    option_r = (True, False) # Recursive operation
    option_s = (True, True)  # Use SetUp and TearDown files
    option_t = (True, [])    # Run Level Symbols
    option_v = (True, True)  # Verbose mode
    option_x = (True, False) # Create an XML statistics file.
    option_z = (True, [])    # diagnostic parameters

    parmDict =  {"a": ("fo", "appConfigurationModule"),
                 "b": ("lo", "appConfigurationParms"),
                 "c": ("bo", "useCSS"),
                 "d": ("eo", "defaultEncoding"),
                 "e": ("bo", "standardMode"),
                 "i": ("eo", "inputEncodingOverride"),
                 "l": ("co", "standardsLevel"),
                 "o": ("eo", "outputEncodingForce"),
                 "q": ("qo", "quietMode"),
                 "r": ("bo", "recursive"),
                 "s": ("bo", "doSetUp"),
                 "t": ("lo", "runLevelSymbols"),
                 "v": ("bo", "verbose"),
                 "x": ("bo", "collectStats"), # should this be an f?
                 "z": ("lo", "diagnosticOptions"),
                 " defaultRunner": "FileRunner",
                 }


# FileRunner is one of the two standard runners supplied
# with every version of batch FIT. These are the options
# that are closest to the standard behavior of this runner.

# Remember that anything not specified here will default
# to what's in the superclass, that is BatchBase.

# This is the most generic runner. While most of the FIT
# documentation says it's for single files, it will actually
# do everything any other runner can do. 

class FileRunner(BatchBase):
    option_q = (True, "yn")    # Quiet mode
    option_r = (True, False)   # Recursive operation
    option_s = (True, False)   # Use SetUp and TearDown files
    option_v = (True, True)    # Verbose mode
    option_x = (True, False)   # Create an XML statistics file.

class WikiRunnerRunner(FileRunner):
    pass

# The big difference is that HtmlRunner defaults to using
# SetUp and TearDown files. The option will not show up on
# the command line, so it can't be turned off.

class HtmlRunner(BatchBase):
    option_q = (True, "yn")     # Quiet mode
    option_r = (False, False)   # Recursive operation
    option_s = (False, True)    # Use SetUp and TearDown files
    option_v = (True, True)     # Verbose mode
    option_x = (False, False)   # Create an XML statistics file.

class FolderRunner(BatchBase):    
    option_q = (True, "ef")   # Quiet mode
    option_r = (True, False)  # Recursive operation
    option_s = (False, True)  # Use SetUp and TearDown files
    option_v = (True, True)   # Verbose mode
    option_x = (True, False)  # Create an XML statistics file.

# NOTE Runner name NotARunner is reserved for use by the test suite
# to test the ability to use either BatchBase or TestRunner (?_) if
# the runner name is not in this module.

class FitNesseBase(OptionsBase):
    pass

class FitServer(FitNesseBase):
    option_a = (False, "")    # Application Configuration Module Name
    option_b = (False, [])    # Application Configuration Parm List
    option_l = (False, "1.1") # FIT specification level
    option_t = (False, [])    # Run Level Symbols
    option_v = (True, False)  # verbose option
    option_z = (False, [])    # diagnostic options

    parmDict = {"a": ("fo", "appConfigurationModule"),
                "b": ("lo", "appConfigurationParms"),
                "l": ("eo", "standardsLevel"),
                "t": ("lo", "runLevelSymbols"),
                "v": ("bo", "verbose"),
                "z": ("lo", "diagnosticOptions"),
                " defaultRunner": "FitServer",
                }


# Note that several of these options cascade: options h, r and x
#    are only meaningful if option o specifies an output directory,
#    and options e and f are likewise only meaningful if options
#    h or r (or both) are in effect.

class TestRunner(FitNesseBase):
    option_a = (True, "")    # Application Configuration Module Name
    option_b = (True, [])    # Application Configuration Parm List
    option_e = (True, False) # only save files with errors
    option_f = (True, False) # use FitNesse to format output
    option_h = (True, True)  # format results as HTML and save
    option_l = (True, "1.1") # FIT specification level
    option_o = (True, "")    # the directory for output files
    option_p = (True, "") # additional directories to add to the Python path
    option_r = (True, False) # save the raw results to a file
    option_t = (True, [])    # Run Level Symbols
    option_u = (True, "")    # File containing list of pages
    option_v = (True, False) # print test results to stderr file
    option_x = (True, False) # produce XML formatted results file
    option_z = (True, [])    # diagnostic parameters

    parmDict = {"a": ("fo", "appConfigurationModule"),
                "b": ("lo", "appConfigurationParms"),
                "e": ("bo", "onlyError"),
                "f": ("bo", "useFormattingOptions"),
                "h": ("bo", "HTMLOutput"),
                "l": ("eo", "standardsLevel"),
                "o": ("fo", "outputDir"),
                "p": ("po", "pythonPath"),
                "r": ("bo", "rawOutput"),
                "t": ("lo", "runLevelSymbols"),
                "u": ("fo", "listOfFiles"),
                "v": ("bo", "verbose"),
                "x": ("bo", "stats"),
                "z": ("lo", "diagnosticOptions"),
                " defaultRunner": "TestRunner",
                }
