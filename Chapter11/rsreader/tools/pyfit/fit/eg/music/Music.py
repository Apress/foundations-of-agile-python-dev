# Copyright (c) 2002 Cunningham & Cunningham, Inc.
# Released under the terms of the GNU General Public License version 2 or later.
# Converted to Python 2003/07/24 by John Roth

from types import *
from fit.TypeAdapter import TypeAdapter

class DateTime:
    """ A date/time class because we don't have 2.3 yet
        And even if we did, we can't use it and stay compatible with 2.3
    """
    # strive for consistency with the DateTime class in Python 2.3
    # however, just put in what we need
    def __init__(self, dateTime):
        dateList = dateTime.replace("/", " ").replace(":", " ").split()
        self.month, self.day, self.year, self.hour, self.minute, = \
                  map(lambda x: int(x), dateList[:5])
        self.second = 0
        if self.year < 90: # Y2K idiocy
            self.year += 2000
        elif self.year < 100:
            self.year += 1900
        if self.hour == 12:
            self.hour = 0
        if dateList[5] == "PM":
            self.hour += 12

    def __str__(self):
        year = str(self.year)[2:]
        if self.hour > 11:
            hour = self.hour - 12
            ampm = "PM"
        else:
            hour = self.hour
            ampm = "AM"
        if hour == 0: hour = 12
        return ("%s/%s/%s %s:%s %s" % (self.month, self.day, year, hour,
                                       self.minute, ampm))

    def __repr__(self):
        return self.__str__()

    def toList(self):
        return [self.year, self.month, self.day, self.hour, self.minute]

    def __cmp__(self, other):
        return cmp(self.toList(), other.toList())

    def __hash__(self):
        return ((((self.year * 12 + self.month) * 31 + self.day) * 60 +
                  self.hour) * 24 + self.minute)

class DateAdapter(TypeAdapter):
    def __init__(self, instance, name, typeName, metaData = None):
        __pychecker__ = "no-argsused"
        self.typeName = typeName
        self.metaData = metaData
        
    def parse(self, text):
        return DateTime(text)

    def toString(self, obj):
        return str(obj)

# class Music(RowFixture): # does this really need to inherit from RowFixture?
class Music:
    _typeDict = {"date": DateAdapter,
                 "selected": "Boolean",
                 "status": "String",
                 "title": "String",
                 "artist": "String",
                 "album": "String",
                 "genre": "String",
                 "size": "Int",
                 "seconds": "Int",
                 "trackNumber": "Int",
                 "trackCount": "Int",
                 "year": "Int"}
    status = "Ready"
    title = ""
    artist = ""
    album = ""
    genre = ""
    size = 0
    seconds = 0
    trackNumber = 0
    trackCount = 0
    year = 0
    date = "" # should be a Date object!!!
    selected = 0 # should be a Boolean object

    def __init__(self, desc):
        list1 = desc.split("\t")[:10]
        list2 = map(lambda x: x.strip(), list1)
        self.title, self.artist, self.album, self.genre, sSize, \
                    sSeconds, sTrackNumber, sTrackCount, \
               sYear, sDate = list2
        self.size = int(sSize)
        self.seconds = int(sSeconds)
        self.trackNumber = int(sTrackNumber)
        self.trackCount = int(sTrackCount)
        self.year = int(sYear)
        self.date = DateTime(sDate)

    ######## Accessors #########

    _typeDict["track"] = "String"
    def track(self):
        return "%s of %s" % (self.trackNumber, self.trackCount)

    _typeDict["time"] = "Float"
    def time(self):
        return round(self.seconds / 0.6) / 100.0

    _typeDict["toString"] = "String"
    def toString(self):
        if self.title:
            return self.title
        else:
            return super(Music, self).toString()
