# Music Player example program from PyFit
# copyright 2005, John H. Roth Jr.
# Released under the terms of the GNU General Public License, version 2 or above

import copy
import re
import sys
import types
from fit.Parse import Parse # XXX this violates "doesn't depend on Fit"

def em(msg):
    if msg[-1] != "\n":
        msg += "\n"
    sys.stderr.write(msg)

class EnglishListFixture(object):
    parseRE = re.compile(r",|\sor\s|\sand\s")
    def parse(self, aString):
        aList = self.parseRE.split(aString)
        result = [x.strip() for x in aList
                  if len(x.strip()) != 0]
        return result

    def toString(self, aList):
        aList = [x.strip() for x in aList]
        aString = ", ".join(aList)
        lastComma = aString.rfind(",")
        if lastComma == -1:
            return aString
        begin = aString[:lastComma]
        end = aString[lastComma+1:]
        result = "%s and %s" % (begin.strip(), end.strip())
        return result

class UnorderedListFixture(object):
    def cellParse(self, aCell):
        nodes = Parse(aCell.body, ["ul", "li"])
        result = self._doUL(nodes)
        return result

    def parse(self, aString):
        nodes = Parse(aString, ["ul", "li"])
        result = self._doUL(nodes)
        return result

    def _doUL(self, nodes):
        result = self._doLI(nodes.parts)
        return result

    def _doLI(self, nodes):
        result = []
        while nodes is not None:
            if nodes.parts is not None:
                result.append(self._doUL(nodes.parts))
            elif nodes.body.find(":") > -1:
                parts = [x.strip() for x in nodes.text().split(":", 1)]
                if parts[0].lower() == "time":
                    result.append((parts[0], TimeInSeconds(parts[1])))
                elif parts[0].isdigit():
                    result.append(TimeInSeconds(nodes.text()))
                else:
                    result.append((parts[0], parts[1]))
            else:
                result.append(nodes.text())
            nodes = nodes.more
        return result

    def cellEquals(self, cell, right):
        # the character compare takes place in MethodTarget, so
        # it doesn't ever get here...
        body = cell.body.replace("\n", "")
        left = self.parse(body)
        tOrF = self.equals(left, right)
        if tOrF:
            return tOrF
        right = self.toString(right)
        tOrF = body == right
        return tOrF

    def stringEquals(self, left, right):
        if isinstance(left, types.StringTypes):
            left = self.parse(left)
        return self.equals(left, right)

    def equals(self, left, right):
        errthing = []
        errthing.append(0)
        retCode, retErr = self._equals(left, right, errthing, 0)
        return retCode

    def _equals(self, left, right, errthing, depth):
##        em("\nin _equals depth: '%s' errthing: '%s' left: '%s' right: '%s'"
##           % (depth, errthing, left, right))
        if (isinstance(left, types.StringTypes) and
            isinstance(right, types.StringTypes)):
            return (left == right), errthing
        if type(left) != type(right):
            return False, errthing
        i = 0
        while i < len(left) and i < len(right):
            newErrthing = errthing[:]
            newErrthing.append(i)
            retCode, retErr = self._equals(left[i], right[i],
                                           newErrthing, depth+1)
            if retCode is False:
                return False, retErr
            i += 1
        if len(left) != len(right):
            newErrthing = errthing[:]
            newErrthing.append(i)
            return False, newErrthing
        return True, errthing

    def toString(self, obj):
        parts = []
        self._buildUL(obj, parts)
        return "".join(parts)

    def _buildLI(self, item, parts):
        parts.append("<li>")
        if isinstance(item, types.StringTypes):
            parts.append(item)
        elif isinstance(item, types.TupleType):
            if isinstance(item[1], types.ListType):
                parts.append("%s: " % item[0])
                self._buildUL(item[1], types)
            elif isinstance(item[1], TimeInSeconds):
                parts.append("%s: %s" % (item[0],
                                         item[1].inMinutesAndSeconds()))
            else:
                parts.append("%s: %s" % (item[0], item[1]))
        else:
            self._buildUL(item, parts)
        parts.append("</li>")
        return

    def _buildUL(self, aList, parts):
        parts.append("<ul>")
        for item in aList:
            self._buildLI(item, parts)
        parts.append("</ul>")

class Song(object):
    _typeDict = {}
    _baseTypeDict = {}
    
    def __init__(self, names, fields):
        Song._typeDict = self._baseTypeDict.copy()
#        self._typeDict = self._baseTypeDict
        nameList = names.split("\t")
        fieldList = fields.split("\t")
        convertSpec = "SSSSIIIIIS"
        i = 0
        while i < 10:
            name = nameList[i]
            value = fieldList[i]
            conv = convertSpec[i]
            name = name.replace(" ", "")
            if name == "Time":
                name = "Seconds"
            if conv == "I":
                self._typeDict[name] = "Int"
                value = int(value)
            else:
                self._typeDict[name] = "String"
            setattr(self, name, value)
            i += 1

    def getTrack(self):
        __pychecker__ = "no-classattr"
        return "%s of %s" % (self.TrackNumber, self.TrackCount)
    _baseTypeDict["Track"] = "String"
    Track = property(getTrack)

    def getTime(self):
        __pychecker__ = "no-classattr" # Seconds
        return TimeInSeconds(self.Seconds).inMinutesAndSeconds()
    _baseTypeDict["Time"] = "String"
    Time = property(getTime)

    def fields(self, fieldList):
##        em("\nin fieldsFrom. list: '%s'" % (fieldList,))
        resultList = []
        for fieldName in fieldList:
            fieldName = fieldName.title()
            fieldValue = getattr(self, fieldName, "unknown field name")
            resultList.append("%s: %s" % (fieldName, fieldValue))
##        em("--- result: '%s'" % resultDict)
        return resultList

    def getField(self, fieldName):
        return getattr(self, fieldName.title(), "unknown field name")

class MusicLibrary(object):
    def load(self, path):
        aFile = open(path, "rt")
        trackList = []
        lineList = aFile.readlines()
        aFile.close()
        nameList = lineList[0]
        for aLine in lineList[1:]:
            trackList.append(Song(nameList, aLine))
        self._trackList = trackList
        self._selectedList = copy.copy(trackList)
        self._trackSelected = None

    def totalIn(self, field, container):
        if field != "songs":
            raise Exception, "Unsupported options"
        if container == "library":
            result = len(self._trackList)
        elif container == "selection":
            result = len(self._selectedList)
        else:
            raise Exception, "Unsupported options"
        return result

    # !!! this may be obsolete since we added fieldsFrom to Song
    def fields(self, fieldList, track):
        songObj = self._trackList[track-1]
        result = songObj.fields(fieldList)
        return result

    def selectTrack(self, aTrack):
        if (0 <= aTrack-1 < len(self._selectedList)):
            self._trackSelected = self._selectedList[aTrack-1]
        else:
            self._trackSelected = None
        return self._trackSelected

    def selectAll(self):
        self._selectedList = copy.copy(self._trackList)

    def findSame(self, field):
        if self._trackSelected is None:
            return False
        value = self._trackSelected.getField(field)
        if value == "unknown field name":
            return False
        selectedList = []
        for aSong in self._trackList:
            if value == aSong.getField(field):
                selectedList.append(aSong)
        self._selectedList = selectedList
        return True

class MusicPlayer(object):
    _typeDict = {}
    _defaultMusicLibrary = MusicLibrary()
    def __init__(self):
        self._library = self._defaultMusicLibrary
        self._status = "ready"
        self._searchStatus = "ready"
##        self._simulator = Simulator()
        self._currentSelection = None
        self._playTimeRemaining = TimeInSeconds(0)
        self._loadTimeRemaining = TimeInSeconds(0)
        self._searchTimeRemaining = TimeInSeconds(0)

# Methods that proxy the MusicLibrary        

    _typeDict["load.types"] = [None, "String"]
    def load(self, path):
        self._library.load(path)

    _typeDict["totalIn.types"] = ["Int", "String", "String"]
    def totalIn(self, field, container):
        return self._library.totalIn(field, container)

    _typeDict["findSame.types"] = ["Boolean", "String"]
    def findSame(self, field):
        self._searchStatus = "searching"
        self._searchTimeRemaining = TimeInSeconds(0)
        return self._library.findSame(field)
    
    _typeDict["selectTrack.types"] = ["Boolean", "Int"]
    def selectTrack(self, aTrack):
        result = self._library.selectTrack(aTrack)
        if result is None:
            return False
        self._currentSelection = result
        return True

    _typeDict["selectAll.types"] = ["Boolean"]
    def selectAll(self):
        self._library.selectAll()
        self._searchStatus = "searching"
        self._searchTimeRemaining = TimeInSeconds(0)
        return True

# Methods that proxy methods on Song objects

    _typeDict["fields.types"] = [UnorderedListFixture,
                                     EnglishListFixture]
    def fields(self, fields):
        if self._currentSelection is None:
            return "No track selected"
        return self._currentSelection.fields(fields)

    _typeDict["currentTrack.types"] = ["String", "String"]
    def currentTrack(self, fieldName):
        if self._currentSelection is None:
            return "No track selected"
        return self._currentSelection.getField(fieldName)

# Methods for the Music Player proper

    _typeDict["wait.types"] = ["Boolean", "Int"]
    def wait(self, seconds):
        residual = seconds
        if self._status == "loading":
            residual = self._loadTimeRemaining.subtractSeconds(residual)
            if residual <= 0:
                self._status = "playing"
                self._loadTimeRemaining = TimeInSeconds(0)
                residual = 0 - residual
        if self._status == "playing":
            residual = self._playTimeRemaining.subtractSeconds(residual)
            if residual <= 0:
                self._loadTimeRemaining = TimeInSeconds(4)
                self._status = "unloading"
                residual = 0 - residual
        if self._status == "unloading":
            residual = self._loadTimeRemaining.subtractSeconds(residual)
            if residual <= 0:
                self._status = "ready"
                self._loadTimeRemaining = TimeInSeconds(0)

        if self._searchStatus == "searching":
            residual = self._searchTimeRemaining.subtractSeconds(seconds)
            if residual <= 0:
                self._searchStatus = "ready"
                self._searchTimeRemaining = TimeInSeconds(0)
        return True

    _typeDict["play.types"] = ["Boolean"]
    def play(self):
        if self._currentSelection is None:
            return False
        if self._status == "ready":
            self._status = "loading"
            self._playTimeRemaining = TimeInSeconds(
                self._currentSelection.getField("time"))
            self._loadTimeRemaining = TimeInSeconds(4)
            return True
        elif self._status == "paused":
            self._status = "playing"
            return True
        return False

    _typeDict["playerStatus.types"] = ["String"]
    def playerStatus(self):
        return self._status

    _typeDict["pause.types"] = ["Boolean"]
    def pause(self):
        self._status = "paused"
        return True

    _typeDict["searchStatus.types"] = ["String"]
    def searchStatus(self):
        return self._searchStatus

    _typeDict["timeRemaining.types"] = ["String"]
    def timeRemaining(self):
            return self._playTimeRemaining.inMinutesAndSeconds()

    _typeDict["waitFor.types"] = ["Boolean", "String"]
    def waitFor(self, event):
        if event == "track complete":
            if self._status not in ("loading", "playing"):
                return False
            residual = (self._loadTimeRemaining._seconds +
                        self._playTimeRemaining._seconds)
            self.wait(residual)
        elif event == "search complete":
            if self._searchStatus != "searching":
                return False
            residual = self._searchTimeRemaining._seconds
            self.wait(residual)
        else:
            return False
        return True

    _typeDict["fail.types"] = ["$SUT", "String"]
    def fail(self, failureType):
        if failureType != "load jam":
##            em("\nin fail: returned None")
            return None
        return LoadJam(self)

    _typeDict["display.types"] = ["$Display", EnglishListFixture]
    def display(self, fieldList):
        return self._library._selectedList, fieldList, Song._typeDict

    _typeDict["verify.types"] = ["$Row"]
    def verify(self):
        return self._library._selectedList, Song._typeDict

class LoadJam(object):
    _typeDict = {}
    def __init__(self, invoker):
        self._invoker = invoker

    _typeDict["message.types"] = ["String"]
    def message(self):
        return "load jammed"

    _typeDict["press.types"] = ["$SUT", "String"]
    def press(self, what):
        if what.lower() != "ok":
            return "OK is the only availible button!"
        return self._invoker

class TimeInSeconds(object):
    def __init__(self, seconds):
        if not isinstance(seconds, types.StringTypes):
            self._seconds = seconds
        elif seconds.find(":") > -1:
            parts = [int(x) for x in seconds.split(":")]
            self._seconds = parts[0] * 60 + parts[1]
        else:
            self._seconds = int(seconds)

    def inSeconds(self):
        return "%s" % self._seconds

    def inMinutesAndSeconds(self):
        return "%d:%02d" % divmod(self._seconds, 60)

    def addSeconds(self, anInt):
        self._seconds += anInt
        return self._seconds

    def subtractSeconds(self, anInt):
        result = self._seconds - anInt
        self._seconds = max(0, result)
        return result

    def __eq__(self, other):
        if isinstance(other, TimeInSeconds):
            return self._seconds == other._seconds
        return self._seconds == other

    def __ne__(self, other):
        if isinstance(other, TimeInSeconds):
            return self._seconds != other._seconds
        return self._seconds != other

    def __lt__(self, other):
        if isinstance(other, TimeInSeconds):
            return self._seconds < other._seconds
        return self._seconds < other

    def __gt__(self, other):
        if isinstance(other, TimeInSeconds):
            return self._seconds > other._seconds
        return self._seconds > other

    def __le__(self, other):
        if isinstance(other, TimeInSeconds):
            return self._seconds <= other._seconds
        return self._seconds <= other

    def __ge__(self, other):
        if isinstance(other, TimeInSeconds):
            return self._seconds >= other._seconds
        return self._seconds >= other        
