# TypeAdapter Table for FIT
#LegalStuff jr05
# Copyright 2005 John H. Roth Jr.
# Released under the terms of the General Public License (GPL), Release 2.1 or later
# See license.txt for terms and disclaimer of all warrenties and liability.
# Last updated for Release 0.8a1
#endLegalStuff

# This rather skeletal module is for communication between
# the type adapter implementation module, TypeAdapter, and
# the actual type adapters. It's not for applications to
# add their own type adapters. The names are added dynamically
# as the modules are loaded.

typeAdapterTable = {}

typeToAdapter = {}

cellHandlerTable = {}

cellHandlerClassToName = {}

def _isApplicationProtocol(aClass):
    proto = getattr(aClass, "fitAdapterProtocol", False)
    parse = getattr(aClass, "parse", False)
    equals = getattr(aClass, "equals", False)
    toString = getattr(aClass, "toString", False)
    return not(proto or parse or equals or toString)

def _isAdapterProtocol(aClass):
    parse = getattr(aClass, "parse", False)
    equals = getattr(aClass, "equals", False)
    toString = getattr(aClass, "toString", False)
    return parse and equals and toString

