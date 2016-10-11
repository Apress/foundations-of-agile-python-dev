# Variations.py part of Core Fit
#legalStuff jr05-06
# Copyright 2005-2006 John H. Roth Jr.
# Released under the terms of the General Public License (GPL), Release 2.1 or later
# See license.txt for terms and disclaimer of all warrenties and liability.
# Last updated for Release 0.8a1
#endLegalStuff

# 0.8a2 - accept _ as alpha character in camel and GracefulNames

import sys
import types
from fit.FitException import FitException
from fit import FitGlobal
from fit.Utilities import em

try:
    False
except: #pragma: no cover
    True = 1
    False = 0

# These labels are in the process of being moved from Fixture.
# They are still here until several fixtures that use them for
# checking are fixed to call vOpts to do the checking
greenColor = "cfffcf"
redColor = "ffcfcf"
grayColor = "efefef"
yellowColor = "ffffcf"
labelColor = "c08080"
grayLabelColor = "808080"
greenLabelColor = "80c080"

# Note that the following is pretty hacky
# It works because the only significant variation is FitNesse and Batch,
#  and within batch the only significant variation is CSS mode
# This situation is likely to change with the next specification (2.0)

def returnVariation(env = None):
    __pychecker__ = "no-argsused"
    if FitGlobal.Environment == "FitNesse":
        result =  FitNesseVariation()
    elif FitGlobal.Options.standardMode:
        result =  StandardVariation()
    elif FitGlobal.Options.useCSS:
        result = FitVariation()
    else:
        result = StandardVariation()
    FitGlobal.annotationStyleVariation = result
    return result

class VariationsBase(object):
    # Router to invoke the correct label mapping routine
    def mapLabel(self, label, kind=None, default=None):
        result = FitGlobal.appConfigInterface("mapLabel", label)
        if result is None or result[0] is None:
            pass
        elif result[0] == "done":
            return result[1]
        else:
            kind = result[1]
        kind = kind or default or "default"
        if kind == "camel":
            return self._camelLabelMapping(label)
        elif kind == "gracefulNames":
            return self._gracefulNamesLabelMapping(label)
        elif kind == "extended":
            return self._extendedLabelMapping(label)
        elif kind == "default":
            if FitGlobal.Environment == "FitNesse":
                return self._gracefulNamesLabelMapping(label)
            else:
                return self._camelLabelMapping(label)
        raise FitException("InvalidKindForMapLabel", kind)
    
    # camelCase routine. Thanks to Rick Mugridge whose ExtendedCamel
    # routine pointed out several problems with the original camelCase
    # (batch) and gracefulName (FitNesse) routines.
    def _camelLabelMapping(self, name):
        name = name.strip()
        if len(name) == 0:
            return ""
        resultList = []
        state = "first"
        for char in name:
            if char.isalnum() or char == "_":
                if state == "out":
                    char = char.upper()
                resultList.append(char)
                state = "in"
            else:
                state = "out"
        resultList[0] = self._handleFirstCharacter(resultList[0])
        result = "".join(resultList)
        result = self._handleKeywords(result)
        return result

    # This is not quite the version of Graceful Names in
    # FixtureLoader, nor is it the version in the Fitnesse
    # Java version. It differs from camel in that it uppercases
    # letters that follow numbers.

    def _gracefulNamesLabelMapping(self, name):
        name = name.strip()
        if len(name) == 0:
            return ""
        resultList = []
        state = "first"
        for char in name:
            if char.isdigit():
                resultList.append(char)
                state = "out"
            elif (char.isalpha() or char == "_"):
                if state == "out":
                    char = char.upper()
                resultList.append(char)
                state = "in"
            else:
                state = "out"
        resultList[0] = self._handleFirstCharacter(resultList[0])
        result = "".join(resultList)
        result = self._handleKeywords(result)
        return result

    # This is basically the Extended Camel routine from  Fit Library. It
    # differs from the normal mapping by translating otherwise unconvertable
    # characters into their hex escape sequences.

    def _extendedLabelMapping(self, name):
        name = name.strip()
        if len(name) == 0: # uh, what's this?
            return "blank"
        i = 0
        while i < len(name):
            alpha = self._specialCharacterToName.get(name[i])
            if alpha:
                name = name[:i] + alpha + name[i+1:]
            i += 1
            
        if name[0].isdigit():
            name = self._expandDigitTable[int(name[0])] + name[1:]
        
        nameList = name.split()
        i = 1
        while i < len(nameList):
            nameList[i] = nameList[i][0].upper() + nameList[i][1:]
            i += 1
        name = "".join(nameList)
            
        return self._handleKeywords(self._translateUnicode(name))

    def _handleFirstCharacter(self, char):
        if char.isdigit():
            return self._expandDigitTable[int(char)]
        return char

    _expandDigitTable = ["zero", "one", "two", "three", "four", "five",
                         "six", "seven", "eight", "nine"]

    def _translateUnicode(self, name):
        i = 0
        while i < len(name):
            if ord(name[i]) > 127:
                coded = "0000" + hex(ord(name[i])).upper()
                if isinstance(name, types.UnicodeType):
                    coded = "u"+coded[-4:]
                else: #pragma: no cover
                    coded = "x"+coded[-2:]
                name = name[:i] + coded + name[i+1:]
            i += 1

        return name

    def _handleKeywords(self, word):
        if self._keywords.has_key(word):
            return word + "_"
        return word

    _keywords = {
         "and": None,
         "as": None, # Python 3.0
         "assert": None,
         "break": None,
         "class": None,
         "continue": None,
         "def": None,
         "del": None,
         "elif": None,
         "else": None,
         "except": None,
         "exec": None,
         "False": None, # Python 3.0
         "finally": None,
         "for": None,
         "from": None,
         "global": None,
         "if": None,
         "import": None,
         "in": None,
         "is": None,
         "lambda": None,
         "None": None, # Python 2.4
         "not": None,
         "or": None,
         "pass": None,
         "print": None,
         "raise": None,
         "return": None,
         "True": None, # Python 3.0
         "try": None,
         "while": None,
         "yield": None,
         }

    _specialCharacterToName = {
        "!": " bang ",
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
        "~": " tilde ",
        # Currency symbols likely to be found in English tests
        u"\u00a2": " cent ",
        u"\u00a3": " pound ",
        u"\u00a5": " yen ",
        u"\u20ac": " euro ",
        }

    def right(self):
        __pychecker__ = "no-classattr"
        return self.fit_pass

    def wrong(self):
        __pychecker__ = "no-classattr"
        return self.fit_fail

    def ignore(self):
        __pychecker__ = "no-classattr"
        return self.fit_ignore

    def exception(self):
        __pychecker__ = "no-classattr"
        return self.fit_error

    def stackTrace(self, err):
        __pychecker__ = "no-classattr"
        return self.fit_stacktrace % err

    def label(self, aString):
        __pychecker__ = "no-classattr"
        return self.fit_label % aString

    def gray(self, aString):
        __pychecker__ = "no-classattr"
        return self.fit_gray % aString

    def greenlabel(self, aString):
        __pychecker__ = "no-classattr"
        return self.fit_green % aString

    def camel(self, label):
        return self.mapLabel(label, "camel")

    def gracefulName(self, label): #pragma: no cover
        return self.mapLabel(label, "gracefulNames")

class FitNesseVariation(VariationsBase):
    fit_pass = ' class="pass"'
    fit_fail = ' class="fail"'
    fit_error = ' class="error"'
    fit_ignore = ' class="ignore"'
    fit_stacktrace = '<hr><div class="fit_stacktrace"><pre><font size=-2>%s</font></pre></div>'
    fit_label = ' <span class="fit_label">%s</span>'
    fit_gray = ' <span class="fit_grey">%s</span>'
    fit_green = ' <span class="fit_grey">%s</span>'

    def tagIsNotAnnotated(self, tag): return tag.find("class=") == -1
    def tagIsRight(self, tag): return tag.find("pass") > -1
    def tagIsWrong(self, tag): return tag.find("fail") > -1
    def tagIsIgnored(self, tag): return tag.find("ignore") > -1
    def tagIsError(self, tag): return tag.find("error") > -1
    def infoIsTrace(self, body): return body.find("fit_stacktrace") > -1
    def infoIsRight(self, body): return body.find("fit_grey") > -1
    def infoIsWrong(self, body): return body.find("fit_label") > -1
    def infoIsIgnored(self, body): return body.find("fit_grey") > -1

    def camel(self, label):
        return self._gracefulNamesLabelMapping(label)

class FitVariation(VariationsBase):
    fit_pass = ' class="fit_pass"'
    fit_fail = ' class="fit_fail"'
    fit_error = ' class="fit_error"'
    fit_ignore = ' class="fit_ignore"'
    fit_stacktrace = '<hr><div class="fit_stacktrace"><pre><font size=-2>%s</font></pre></div>'
    fit_label = ' <span class="fit_label">%s</span>'
    fit_gray = ' <span class="fit_grey">%s</span>'
    fit_green = ' <span class="fit_green">%s</span>'

    def tagIsNotAnnotated(self, tag): return tag.find("class=") == -1
    def tagIsRight(self, tag): return tag.find("fit_pass") > -1
    def tagIsWrong(self, tag): return tag.find("fit_fail") > -1
    def tagIsIgnored(self, tag): return tag.find("fit_ignore") > -1
    def tagIsError(self, tag): return tag.find("fit_error") > -1
    def infoIsTrace(self, body): return body.find("fit_stacktrace") > -1
    def infoIsRight(self, body): return body.find("fit_green") > -1
    def infoIsWrong(self, body): return body.find("fit_label") > -1
    def infoIsIgnored(self, body): return body.find("fit_grey") > -1


class StandardVariation(FitVariation):
    def right(self):
        return ' bgcolor="#%s"' % greenColor

    def wrong(self):
        return ' bgcolor="#%s"' % redColor

    def ignore(self):
        return ' bgcolor="#%s"' % grayColor    

    def exception(self):
        return ' bgcolor="#%s"' % yellowColor

    def stackTrace(self, err):
        return "<hr><pre><font size=-2>%s</font></pre>" % err

    def label(self, aString):
        return (' <font size=-1 color="#%s"><i>%s</i></font>' %
                (labelColor, aString))  

    def gray(self, aString):
        return ' <font color="#%s">%s</font>' % (grayLabelColor, aString)

    def greenlabel(self, aString):
        return (' <font size=-1 color="#%s"><i>%s</i></font>' %
                (greenLabelColor, aString))

    def tagIsNotAnnotated(self, tag): return tag.find("bgcolor=") == -1
    def tagIsRight(self, tag): return tag.find(greenColor) > -1
    def tagIsWrong(self, tag): return tag.find(redColor) > -1
    def tagIsIgnored(self, tag): return tag.find(grayColor) > -1
    def tagIsError(self, tag): return tag.find(yellowColor) > -1
    def infoIsTrace(self, body): return body.find("size=-2") > -1
    def infoIsRight(self, body): return body.find(greenLabelColor) > -1
    def infoIsWrong(self, body): return body.find(labelColor) > -1
    def infoIsIgnored(self, body): return body.find(grayLabelColor) > -1
