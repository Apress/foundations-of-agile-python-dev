# ExtendedCamelCase from FitLibrary
#legalStuff rm04-05 jr05
# Original version Contains code developed by Rick Mugridge.
# University of Auckland, NZ. Copyright 2004-2005 Rick Mugridge.
# Released under the terms of the General Public License (GPL), Release 2.1 or later
# See license.txt for terms and disclaimer of all warrenties and liability.
# changes Copyright 2005 John H. Roth Jr.
# Last updated for Release 0.8a1
#endLegalStuff

# Note - since this consistes essentially of static methods, the class
#  has been eliminated. 

# Allow for any character in a name, such as a field, method or action.
# Ensure that the name is not a Python key word.
# Map any characters that are not valid in a Python identifier into a word that is, in camel case.
# This includes Unicode.

from fit import FitGlobal

mapSpecChars = { "!": " bang ",
		"\"": " quote ",
		"#": " hash ",
		"$": " dollar ",
		"%": " percent ",
		"&": " ampersand ",
		"'": " single quote ",
		"(": " left parenthesis ",
		")": " right parenthesis ",
		"*": " star ",
		"+": " plus ",
		",": " comma ",
		"-": " minus ",
		".": " dot ",
		"/": " slash ",
		":": " colon ",
		";": " semicolon ",
		"<": " less than ",
		">": " greater than ",
		"=": " equals ",
		"?": " question ",
		"@": " at ",
		"[": " left square bracket ",
		"]": " right square bracket ",
		"\\": " backslash ",
		"^": " caret ",
		"`": " backquote ",
		"{": " left brace ",
		"}": " right brace ",
		"|": " bar ",
		"~": " tilde "
	}
	
pythonKeywords = {
	    "assert": None, "as": None, "break": None,
	    "class": None, "continue": None,
	    "def": None, 
	    "elif": None, "else": None,
	    "except": None,
	    "for": None, "from": None, "False": None,
	    "if": None,
	    "import": None, "is": None, "in": None,
	    "None": None,
	    "return": None,
	    "raise": None,
	    "try": None, "True": None,
	    "while": None
	}

def camel(name):
    return FitGlobal.annotationStyleVariation._extendedLabelMapping(name)

def _camel(name):
    name = name.strip()
    if len(name) == 0:
        return "blank"
    i = 0
    while i < len(name):
        alpha = mapSpecChars.get(name[i])
        if alpha:
            name = name[:i] + alpha + name[i+1:]
        i += 1
        
    if name[0].isdigit():
        name = mapNumber[name[0]] + name[1:]
    
    nameList = name.split()
    i = 1
    while i < len(nameList):
        nameList[i] = nameList[i][0].upper() + nameList[i][1:]
        i += 1
    name = "".join(nameList)
        
    return hidePythonKeyword(translateUnicode(name))

def hidePythonKeyword(name):
    if pythonKeywords.has_key(name):
        return name+"_"
    return name

# Translate any unicode characters into ASCII.
def translateUnicode(name):
    i = 0
    while i < len(name):
        if ord(name[i]) > 127:
            coded = "0000" + hex(ord(name[i])).upper()
            if type(name) == type(u""):
                coded = "u"+coded[-4:]
            else:
                coded = "x"+coded[-2:]
            name = name[:i] + coded + name[i+1:]
        i += 1
                
    return name

mapNumber = {"0": "zero ",
    "1": "one ",
    "2": "two ",
    "3": "three ",
    "4": "four ",
    "5": "five ",
    "6": "six ",
    "7": "seven ",
    "8": "eight ",
    "9": "nine "
    }
    