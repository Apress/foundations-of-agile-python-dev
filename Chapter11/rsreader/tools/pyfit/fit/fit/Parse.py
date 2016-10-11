# Python translation of FIT.
#legalStuff cc02 sm02 rm05 jr03-05
# Original Java version Copyright 2002 Cunningham and Cunningham, Inc.
# Released under the terms of the General Public License (GPL), Release 2.1 or later
# See license.txt for terms and disclaimer of all warrenties and liability.
# Original translation to Python Copyright 2002 Simon Michael
# Contains code developed by Rick Mugridge.
# University of Auckland, NZ. Copyright 2005 Rick Mugridge.
# changes Copyright 2003-2005 John H. Roth Jr.
# Last updated for Release 0.8a1
#endLegalStuff

import re
import types
from fit import FitGlobal
from fit.Utilities import em

def vOpts():
    return FitGlobal.annotationStyleVariation

# XXX Class ParseException should be depreciated!
class ParseException(Exception):
    def __init__(self, message, offset):
        Exception.__init__(self, (message, offset))
        self.message = message
        self.offset = offset
    def __str__(self):
        return '%s, %s' % (self.message, self.offset)

class Parse(object):
    """
    """
    leader  = ''
    tag     = ''
    body    = ''
    end     = ''
    trailer = ''
    more    = None
    parts   = None
    tags = ("table", "tr", "td")
    footnoteFiles = 0 # static class variable, not instance variable.
    cssCase = "" # values: "Fitnesse", "FIT", "hasStyle", "noStyle"

    # what's the cleanest way to map these to python ?
    #public Parse (String tag, String body, Parse parts, Parse more) {
    #public Parse (String text) throws ParseException {
    #public Parse (String text, String tags[]) throws ParseException {
    #public Parse (String text, String tags[], int level, int offset) throws ParseException {
    def __init__(self,
                 text=None, tags=tags, level=0, offset=0, # use either these
#                 defaultEncoding = None, # obsolete - moved to runners.
                 tag='', body='', parts=None, more=None): # or these
        if text == None:
            if tag == None: tag = ''
            if body == None: body = ''
            self.leader = "\n"
            self.tag = "<"+tag+">"
            self.body = body
            self.end = "</"+tag+">"
            self.trailer = ""
            self.parts = parts
            self.more = more
        else:
            lc = text.lower()
            startTag = lc.find("<"+tags[level])
            endTag = lc.find(">", startTag) + 1
#           startEnd = lc.find("</"+tags[level], endTag)
            startEnd = self.findMatchingEndTag(lc, endTag, tags[level], offset);
            endEnd = lc.find(">", startEnd) + 1
            startMore = lc.find("<"+tags[level], endEnd)
            if (startTag<0 or endTag<0 or startEnd<0 or endEnd<0): #pragma: no cover
                raise ParseException(
                    "Can't find tag: " + tags[level], offset)
            self.leader = text[0:startTag]
            self.tag = text[startTag:endTag]
            self.body = text[endTag:startEnd]
            self.end = text[startEnd:endEnd]
            self.trailer = text[endEnd:]
            self.parts = None
            self.more = None

            if (level+1 < len(tags)):
                self.parts = Parse(self.body, tags, level+1, offset+endTag)
                self.body = ""
            else: # check for embedded table tag. (RM - 2005)
                index = self.body.find("<" + tags[0])
                if (index >= 0):
                    self.parts = Parse(self.body, tags, 0, offset + endTag)
                    self.body = ""

            if (startMore>=0):
                self.more = Parse(self.trailer, tags, level, offset+endEnd)
                self.trailer = None

    # properties to insure invariants for body/parts and trailer/more
    _body = None
    def _setBody(self, body):
        if len(body) == 0:
            if isinstance(self._body, Parse): return
            self._body = None
        else:
            self._body = body
    def _getBody(self):
        if isinstance(self._body, types.StringTypes):
            return self._body
        return ""
    body = property(_getBody, _setBody)

    def _setParts(self, parts):
        if parts is None:
            if isinstance(self._body, types.StringTypes): return
            self._body = None
        else:
            self._body = parts
    def _getParts(self):
        if isinstance(self._body, types.StringTypes):
            return None
        return self._body
    parts = property(_getParts, _setParts)

# creates serious problems in Parse, shown by errors in ParseUtility
# problem may have been two assignments to parts, and none to more!
##    _trailer = None            
##    def _setTrailer(self, trailer):
##        if len(trailer) == 0:
##            if isinstance(self._trailer, Parse): return
##            self._trailer = None
##        else:
##            self._trailer = trailer
##    def _getTrailer(self):
##        if isinstance(self._trailer, types.StringTypes):
##            return self._trailer
##        return ""
##    trailer = property(_getTrailer, _setTrailer)
##
##    def _setMore(self, more):
##        if more is None:
##            if isinstance(self._trailer, types.StringTypes): return
##            self._trailer = None
##        else:
##            self._trailer = more
##    def _getMore(self):
##        if isinstance(self._trailer, types.StringTypes):
##            return None
##        return self._trailer
##    more = property(_getMore, _setMore)

    # Added by Rick Mugridge, Feb 2005 
    def findMatchingEndTag(self, lc, matchFromHere, tag, offset):
        fromHere = matchFromHere
        count = 1
        startEnd = 0
        while (count > 0):
            embeddedTag = lc.find("<" + tag, fromHere)
            embeddedTagEnd = lc.find("</" + tag, fromHere)
            # Which one is closer?
            if (embeddedTag < 0) and (embeddedTagEnd < 0):
                raise ParseException("Can't find tag: " + tag, offset)
            if (embeddedTag < 0):
                embeddedTag = len(lc) + 1
            if (embeddedTagEnd < 0):
                embeddedTagEnd = len(lc) + 1
            if (embeddedTag < embeddedTagEnd):
                count += 1
                startEnd = embeddedTag
                fromHere = lc.find(">", embeddedTag) + 1
            elif (embeddedTagEnd < embeddedTag):
                count -= 1
                startEnd = embeddedTagEnd
                fromHere = lc.find(">", embeddedTagEnd) + 1
        return startEnd

    # readTable moved from FitServer, JR Mar 2005 and renamed.
    # returns either an 8-bit or unicode string, not utf-8 encoded
    def oneHTMLTagToString(self):
        more = self.more
        self.more = None
        if self.trailer is None:
            self.trailer = ""
        result = self.toString()
        self.more = more
        return result

    def size(self):
        if self.more:
            return self.more.size()+1
        else:
            return 1

    def last(self):
        if self.more:
            return self.more.last()
        else:
            return self

    def leaf(self):
        if self.parts:
            return self.parts.leaf()
        else:
            return self

    #public Parse at(int i) {
    #public Parse at(int i, int j) {
    #public Parse at(int i, int j, int k) {
    def at(self, i, j=None, k=None):
        node = self._at(self, i)
        if j is None: return node
        node = self._at(node.parts, j)
        if k is None: return node
        return self._at(node.parts, k)

    def _at(self, node, count):
        while count > 0 and node.more is not None:
            count -= 1
            node = node.more
        return node

    def toList(self):
        node = self
        result = []
        while node:
            result.append(node)
            node = node.more
        return result

    #public String text() {
    def text(self):
        return self.htmlToText(self.body)

    def removeNonBreakTags(self):
        s = Parse._normalizeLineBreaks(self.body)
        s = Parse._removeNonBreakTags(s)
        return s

    # ---------------------------
    # static methods to manipulate HTML - may be usable without
    # an actual parse object.

    def htmlToText(s):
        if FitGlobal.Environment == "FitNesse":
            s = Parse._removeTags(s)
        else:
            s = Parse._normalizeLineBreaks(s) # variations on <br> & msWord
            s = Parse._removeNonBreakTags(s) # everything that isn't <br />
            s = Parse.condenseWhitespace(s)
        s = Parse._convertNbspToSpace(s)
        s = s.strip()
        s = Parse.unescape(s)
        return s
    htmlToText = staticmethod(htmlToText)

    br1re = re.compile(r"<\s*br\s*/?\s*>", flags = re.I)
    br2re = re.compile(r"<\s*/\s*p\s*>\s*(<\s*p\s*>|<\s*p .*?>)",
                       flags = re.I)
    def _normalizeLineBreaks(s):
        s = Parse.br1re.sub("<br />", s) # variations on <br..>
        s = Parse.br2re.sub("<br />", s) # MS Word -- </p>...<p>
        return s
    _normalizeLineBreaks = staticmethod(_normalizeLineBreaks)

    def  _removeNonBreakTags(s): # Batch routine
        i = 0
        j = 0
        i = s.find('<', i)
        while i >= 0:
            j = s.find(">", i+1)
            if j < 0:
                break
            if s[i:j+1] != "<br />":
                s = s[:i] + s[j+1:]
            else:
                i += 1
            i = s.find('<', i)
        return s
    _removeNonBreakTags = staticmethod(_removeNonBreakTags)

    def  _removeTags(s): # FitNesse routine
        i = 0
        j = 0
        i = s.find('<', i)
        while i >= 0:
            j = s.find(">", i+1)
            if j < 0:
                break
            s = s[:i] + s[j+1:]
            i = s.find('<', i)
        return s
    _removeTags = staticmethod(_removeTags)

    def unescape(s):
        s = s.replace("<br />", "\n")
        s = Parse._unescapeEntities(s)
        s = Parse._unescapeSmartQuotes(s)
        return s
    unescape = staticmethod(unescape)

    def _unescapeSmartQuotes(s):
        if type(s) == type(""):
            s = s.replace('\x93', '"')
            s = s.replace('\x94', '"')
            s = s.replace('\x91', "'")
            s = s.replace('\x92', "'");
        else:
            s = s.replace(u'\u201c', u'"')
            s = s.replace(u'\u201d', u'"')
            s = s.replace(u'\u2018', u"'")
            s = s.replace(u'\u2019', u"'");
        return s
    _unescapeSmartQuotes = staticmethod(_unescapeSmartQuotes)

    def _unescapeEntities(s):
        s = s.replace("&lt;", "<")
        s = s.replace("&gt;", ">")
        s = s.replace("&nbsp;", " ") # ???
        s = s.replace("&quot;", '"')
        s = s.replace("&amp;", "&")
        return s
    _unescapeEntities = staticmethod(_unescapeEntities)

    lb1re = re.compile(r"\s+")
    def condenseWhitespace(s):
        s = Parse.lb1re.sub(" ", s)
        return s
    condenseWhitespace = staticmethod(condenseWhitespace)

    def _convertNbspToSpace(s):
        if type(s) == type(""):
            s = s.replace(chr(160), ' ')
            s = s.replace("\\u00a0", unichr(160))
        else:
            s = s.replace(unichr(160), u' ')
            s = s.replace(u"\\u00a0", unichr(160))
        s = s.replace("&nbsp;", " ")
        return s
    _convertNbspToSpace = staticmethod(_convertNbspToSpace)

    def _xPrint(aString, label): #pragma: no cover
        bString = aString
        if isinstance(aString, types.UnicodeType):
            bString = aString.encode("Windows-1252", "replace")
        print "%s. Original text: '%s'" % (label, bString)
        print "--- hex equivalent: '%s'" % Parse._xhex(bString)
    _xPrint = staticmethod(_xPrint)

    def _xencode(aString): #pragma: no cover
        aString = aString.encode("Windows-1252", "replace")
        return aString
    _xencode = staticmethod(_xencode)

    def _xhex(aString): #pragma: no cover
        aString = aString.encode("hex_codec")
        return aString
    _xhex = staticmethod(_xhex)

# Annotation Routines. Moved here from Fixture.

    def right (self, actual=None):
        self.addToTag(vOpts().right())
        self.addGreenLabel(actual)

    def addGreenLabel(self, actual):
        if actual is None: return
        if not isinstance(actual, types.StringTypes):
            actual = str(actual)
        self.addToBody(self.greenlabel("expected") + "<hr>" +
                       self.escape(actual) + self.greenlabel("actual"))

    def wrong (self, actual=None, escape=True):
        self.addToTag(vOpts().wrong())
        if escape: # hack!
            self.body = self.escape(self.text())
        self.addRedLabel(actual, escape)

    def addRedLabel(self, actual, escape=True):
        if actual is None: return
        if not isinstance(actual, types.StringTypes):
            actual = str(actual)
        if escape:
            actual = self.escape(actual)
        self.addToBody(self.label("expected") + "<hr>" +
                       actual + self.label("actual"))
    
    def ignore (self):
        self.addToTag(vOpts().ignore())

    # New in 1.1
    def error(self, msg):
        self.addToTag(vOpts().exception())
        self.body = self.escape(self.text())
        self.addToBody("<hr><pre>%s</pre>" % self.escape(msg))

    def info(self, msg = None):
        if msg is None:
            self.body = self.gray(self.body)
        else:
            self.addToBody(self.gray(self.escape(msg)))

    def exception(self, msg, exc=True, bkg="exception"):
        if exc:
            self.addToBody(vOpts().stackTrace(msg))
        else:
            self.addToBody("<hr>%s" % msg)
        if bkg == "exception":
            self.addToTag(vOpts().exception())
        elif bkg == "right":
            self.addToTag(vOpts().right())
        else:
            self.addToTag(vOpts().wrong())

    def label (self, aString):
        return vOpts().label(aString)
    
    def gray (self, aString):
        return vOpts().gray(aString)

    def greenlabel(self, aString):
        return vOpts().greenlabel(aString)

    def escape(self, aString):
        aString = aString.replace("&", "&amp;");
        aString = aString.replace("<", "&lt;");
        aString = aString.replace("  ", " &nbsp;")
        aString = aString.replace("\r\n", "<br />")
#        aString = aString.replace("\n\r", "<br />")
        aString = aString.replace("\r", "<br />")
        aString = aString.replace("\n", "<br />")
        return aString

# ------- Annotation Check Routines --------------

    def tagIsNotAnnotated(self): return vOpts().tagIsNotAnnotated(self.tag)
    def tagIsRight(self): return vOpts().tagIsRight(self.tag)
    def tagIsWrong(self): return vOpts().tagIsWrong(self.tag)
    def tagIsIgnored(self): return vOpts().tagIsIgnored(self.tag)
    def tagIsError(self): return vOpts().tagIsError(self.tag)
    def infoIsTrace(self): return vOpts().infoIsTrace(self.body)
    def infoIsRight(self): return vOpts().infoIsRight(self.body)
    def infoIsWrong(self): return vOpts().infoIsWrong(self.body)
    def infoIsIgnored(self): return vOpts().infoIsIgnored(self.body)

# ------- End of Annotation Routines -------------

    #public void addToTag(String text) {
    def addToTag(self,text):
        self.tag = self.tag[:-1] + text + ">"

    #public void addToBody(String text) {
    def addToBody(self,text):
        self.body = self.body + text

    def _concat(self, a, b):
        if type(a) == type(b):
            result = a + b
        elif isinstance(a, types.StringType):
            result = a.decode("latin-1") + b
        else:
            result = a + b.decode("latin-1")
        return result

    def toString(self):
        "toString returns either an 8bit string or a unicode string, as appropriate"
        s = self.leader
        s = self._concat(s, self.tag)
        if self.parts:
            s = self._concat(s, self.parts.toString())
        else:
            s = self._concat(s, self.body)
        s = self._concat(s, self.end)
        if self.more:
            s = self._concat(s, self.more.toString())
        else:
            s = self._concat(s, self.trailer)
        return s
        
    def toPrint(self):
        s = self.toString()
        if isinstance(s, types.UnicodeType):
            s = s.encode("utf-8")
        return s

    #public void print(PrintWriter out) {
    # str() always returns an 8-bit string. This bites!
    def __str__(self):
        "str() always returns an 8bit string, even if you're expecting unicode"
        s = self.leader
        s += self.tag
        if self.parts:
            s += str(self.parts)
        else:
            s += self.body
        s += self.end
        if self.more:
            s += str(self.more)
        else:
            s += self.trailer
        return s

    def toNodeList(self):
        resultList = []
        self._repr(resultList)
        printList = []
        i = 1
        for node in resultList:
            leader = self._nodeNum(None, node.leader, resultList)
            parts = self._nodeNum(node.parts, node.body, resultList)
            more = self._nodeNum(node.more, node.trailer, resultList)
            line = ("Node #%3s, %12s, %7s, %12s, %8s, %12s" % (i, leader,
                                                  node.tag, parts,
                                                  node.end, more))
            printList.append(line)
            i += 1
        print "in __repr__ len(printList): '%s'" % len(printList)
        joined = "\n".join(printList)
        print " --- # of newlines: '%s'" % joined.count("\n")
        return joined

    def _nodeNum(self, nextNode, aString, resultList):
        if nextNode is None:
            result = aString[:10]
            return "'%s'" % result.replace("\n", "").strip()
        try:
            index = resultList.index(nextNode)
        except ValueError: #pragma: no cover
            index = 999
        return "Node # %i " % (index + 1)

    def _repr(self, resultList):
        resultList.append(self)
        if self.parts:
            self.parts._repr(resultList)
        if self.more:
            self.more._repr(resultList)

    def __ne__(self, other):
        return not self.__eq__(other)

    def __eq__(self, other):
        if other is None:
            return False
        if not isinstance(other, Parse):
            return False
        return (self.tag == other.tag and
                self.leader == other.leader and
                self.body == other.body and
                self.trailer == other.trailer and
                self.more == other.more and 
                self.parts == other.parts)

    # This assumes that the current directory is fit/, and that the
    # browser is set to one directory above fit/. This may not be true.
    # XXX this routine is due for replacement.

    def footnote(self): #pragma: no cover
        if Parse.footnoteFiles >= 25:
            return "[=]"
        Parse.footnoteFiles += 1
        thisFootnote = Parse.footnoteFiles
        html = "footnotes/%s.html" % (thisFootnote,)
        aFile = open("fat/Reports/" + html, "wt")
        aFile.write(str(self))
        aFile.close()
        return "<a href='%s'>[%s]</a>" % (html, thisFootnote)

    __call__ = toString
