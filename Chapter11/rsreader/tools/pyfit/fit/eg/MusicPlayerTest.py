# test module for MusicPlayer
# copyright 2005, John H. Roth Jr.
# Released under the terms of the GNU General Public License, Version 2.
# See license.txt for conditions and exclusion of all warrenties.

import sys
import unittest
from eg.MusicPlayer import MusicPlayer, MusicLibrary, EnglishListFixture, \
     UnorderedListFixture, Song, TimeInSeconds, LoadJam

try:
    False
except:
    True = 1
    False = 0

def em(msg):
    if msg[-1] != "\n":
        msg += "\n"
    sys.stderr.write(msg)

def makeMusicPlayerTest():
    theSuite = unittest.makeSuite(TestInstantiations, 'test')
    theSuite.addTest(unittest.makeSuite(TestLibraryMethods, 'test'))
    theSuite.addTest(unittest.makeSuite(TestEnglishListFixture, 'test'))
    theSuite.addTest(unittest.makeSuite(TestUnorderedListFixture, 'test'))
    theSuite.addTest(unittest.makeSuite(TestSong, 'test'))
    theSuite.addTest(unittest.makeSuite(TestPlayerMethods, 'test'))
##    theSuite.addTest(unittest.makeSuite(TestSimulator, 'test'))
    theSuite.addTest(unittest.makeSuite(TestTimeInSeconds, 'test'))
    theSuite.addTest(unittest.makeSuite(TestLoadJam, 'test'))
    return theSuite

def _verifyMetaDataExists(obj, methodName):
    typeDict = obj._typeDict
    metaData = typeDict[methodName + ".types"]
    return metaData is not None

class TestInstantiations(unittest.TestCase):
    def setUp(self):
        print '%s %s' % (self.id(), self.shortDescription())

    def testInstantiation(self):
        unused = MusicPlayer()

    def testLibraryInstantiation(self):
        unused = MusicLibrary()

class TestLibraryMethods(unittest.TestCase):
    def setUp(self):
        self.musicPlayer = MusicPlayer()
        print '%s %s' % (self.id(), self.shortDescription())

    def testLoadCommand(self):
        obj = self.musicPlayer
        obj.load("eg/music/music.txt")
        assert len(obj._library._trackList) == 37

    def testTotalIn(self):
        obj = self.musicPlayer
        obj.load("eg/music/music.txt")
        assert _verifyMetaDataExists(obj, "totalIn")
        assert obj.totalIn("songs", "library") == 37

    def testFieldsFrom(self):
        obj = self.musicPlayer
        obj.load("eg/music/music.txt")
        assert _verifyMetaDataExists(obj, "fields")
        fieldNames = ["Name", "artist"]
        unused = obj.selectTrack(1)
        result = obj.fields(fieldNames)
##        em("in testFieldsFrom. input: '%s' result: '%s'" %
##           (input, result))
        assert result == ["Name: Akila", "Artist: Toure Kunda"]

class TestEnglishListFixture(unittest.TestCase):
    def setUp(self):
        self.fixture = EnglishListFixture()
        print '%s %s' % (self.id(), self.shortDescription())

    def testParse(self):
        fixture = self.fixture
        for arg, expected in [("line1", ["line1"]),
                              ("line2, word2", ["line2", "word2"]),
                              ("line3 and word2", ["line3", "word2"]),
                              ("line4, word2, and word3",
                                   ["line4", "word2", "word3"]),
                              ("line5 and word2 and word3",
                                   ["line5", "word2", "word3"]),
                              ("magic or wand", ["magic", "wand"]),]:
            result = fixture.parse(arg)
            assert result == expected, ("input: '%s' result: '%s'"
                                        % (arg, result))

    def testToString(self):            
        fixture = self.fixture
        for expected, arg in [("line1", ["line1"]),
                              ("line2 and word2", ["line2", "word2"]),
                              ("line4, word2 and word3",
                                   ["line4", "word2", "word3"]),
                              ]:
            result = fixture.toString(arg)
            assert result == expected, ("input: '%s' result: '%s'"
                                        % (arg, result))

class TestUnorderedListFixture(unittest.TestCase):
    def setUp(self):
        self.fixture = UnorderedListFixture()
        print '%s %s' % (self.id(), self.shortDescription())

    def testParse(self):
        fixture = self.fixture
        for arg, expected in [("<ul><li>line1</li></ul>",
                                     ["line1"]),
                                ("<ul><li>line2</li><li>key2: value2</li></ul>",
                                     ["line2", ("key2", "value2")])
                                ]:
            result = fixture.parse(arg)
            errthing = []
            errthing.append(0)
            retBool, retPtr = fixture._equals(expected, result, errthing, 0)
            assert retBool, "nesting: '%s' result: '%s' expected: '%s'" % (
                retPtr, result, expected)

    def testToString(self):            
        fixture = self.fixture
        for expected, arg in [("<ul><li>line1</li></ul>",
                                     ["line1"]),
                                ("<ul><li>line2</li><li>key2: value2</li></ul>",
                                     ["line2", ("key2", "value2")])
                                ]:
            result = fixture.toString(arg)
            assert result == expected, "expected: '%s' result: '%s'" % (
                expected, result)

    def testStringEquals(self):            
        fixture = self.fixture
        for aString, aStruct in [("<ul><li>line1</li></ul>",
                                     ["line1"]),
                                ("<ul><li>line2</li><li>key2: value2</li></ul>",
                                     ["line2", ("key2", "value2")])
                                ]:
            result = fixture.stringEquals(aString, aStruct)
            assert result, "string: '%s' struct: '%s'" % (
                aString, aStruct)

class TestSong(unittest.TestCase):
    def setUp(self):
        print '%s %s' % (self.id(), self.shortDescription())

    def testSong(self):
        __pychecker__ = "no-classattr no-objattrs"
        names = "Name	Artist	Album	Genre	Size	Time	Track Number	Track Count	Year	Date"
        songLine = "Akila	Toure Kunda	The Toure Kunda Collection	World	5306074	265	9	10	1996	9/9/02 9:01 AM"	
        aSong = Song(names, songLine)
        assert aSong.Name == "Akila"
        assert aSong.Artist == "Toure Kunda"
        assert aSong.Album == "The Toure Kunda Collection"
        assert aSong.Genre == "World"
        assert aSong.Time == "4:25"
        assert aSong.Size == 5306074
        assert aSong.Track == "9 of 10"
        assert aSong.Year == 1996
        assert aSong.Date == "9/9/02 9:01 AM"

class TestPlayerMethods(unittest.TestCase):
    def setUp(self):
        self.musicPlayer = MusicPlayer()
        self.musicPlayer.load("eg/music/music.txt")
        print '%s %s' % (self.id(), self.shortDescription())

    def testSelectTrack(self):
        obj = self.musicPlayer
        assert _verifyMetaDataExists(obj, "selectTrack")
        assert obj.selectTrack(2)
        assert obj._currentSelection.Time == "3:42"
        assert not obj.selectTrack(0)
        assert not obj.selectTrack(38)

    def testPlay(self):
        obj = self.musicPlayer
        assert _verifyMetaDataExists(obj, "play")
        assert obj.selectTrack(2)
        assert obj.play()

    def testPlay2(self):        
        obj = self.musicPlayer
        obj.selectTrack(2)
        obj._status = "paused"
        assert obj.play()
        assert obj._status == "playing"

    def testPlayerStatus(self):
        obj = self.musicPlayer
        assert _verifyMetaDataExists(obj, "playerStatus")
        assert obj.playerStatus() == "ready"
        assert obj.selectTrack(2)
        assert obj.play()
        assert obj.playerStatus() == "loading"

    def testWait(self):
        obj = self.musicPlayer
        assert _verifyMetaDataExists(obj, "wait")
        obj.wait(2)

    def testCurrentTrack(self):
        obj = self.musicPlayer
        assert _verifyMetaDataExists(obj, "currentTrack")
        obj.selectTrack(2)
        assert obj.currentTrack("name") == "American Tango"

    def testPause(self):        
        obj = self.musicPlayer
        assert _verifyMetaDataExists(obj, "pause")
        obj.pause()
        assert obj.playerStatus() == "paused"

    def testPlaySetsTimeRemaining(self):
        obj = self.musicPlayer
        assert _verifyMetaDataExists(obj, "timeRemaining")
        obj.selectTrack(2)
        obj.play()
        assert obj.timeRemaining() == "3:42"

    def testWaitDecrementsTimeRemaining(self):
        obj = self.musicPlayer
        obj.selectTrack(2)
        obj.play()
        assert obj.timeRemaining() == "3:42"
        assert obj.playerStatus() == "loading"
        obj.wait(4)
        assert obj.playerStatus() == "playing"
        assert obj.timeRemaining() == "3:42"
        obj.wait(10)
        assert obj.timeRemaining() == "3:32"

    def testWaitFor(self):
        obj = self.musicPlayer
        assert _verifyMetaDataExists(obj, "waitFor")
        obj.selectTrack(2)
        obj.play()
        obj.wait(4)
        assert obj.playerStatus() == "playing"
        obj.waitFor("track complete")
        assert obj.playerStatus() == "unloading"
        assert obj.timeRemaining() == "0:00"
        obj.wait(4)
        assert obj.playerStatus() == "ready"

    def testFailMethod(self):
        obj = self.musicPlayer
        assert _verifyMetaDataExists(obj, "fail")
        obj.selectTrack(2)
        obj.play()
        result = obj.fail("load jam")
        assert isinstance(result, LoadJam)

    def testFindSameAlbum(self):
        obj = self.musicPlayer
        assert _verifyMetaDataExists(obj, "findSame")
        obj.selectTrack(2)
        obj.findSame("album")
        obj.wait(4)
        assert obj.totalIn("songs", "selection") == 2

    def testSearchStatus(self):
        obj = self.musicPlayer
        assert _verifyMetaDataExists(obj, "searchStatus")
        obj.selectTrack(3)
        obj.findSame("album")
        assert obj.searchStatus() == "searching"
        obj.wait(4)
        assert obj.searchStatus() == "ready"

    def testWaitForSearchComplete(self):        
        obj = self.musicPlayer
        obj.selectTrack(3)
        obj.findSame("album")
        assert obj.searchStatus() == "searching"
        obj.waitFor("search complete")
        assert obj.searchStatus() == "ready"

    def testDisplay(self):
        obj = self.musicPlayer
        assert _verifyMetaDataExists(obj, "display")
        obj.selectTrack(3)
        obj.findSame("album")
        print obj.display(["artist", "year"])

    def testVerify(self):
        obj = self.musicPlayer
        assert _verifyMetaDataExists(obj, "verify")
        # there doesn't seem to be any way of testing this!

class TestTimeInSeconds(unittest.TestCase):
    def setUp(self):
        print '%s %s' % (self.id(), self.shortDescription())

    def testInitInSeconds(self):
        tis = TimeInSeconds("59")
        assert tis.inSeconds() == "59"
        assert tis.inMinutesAndSeconds() == "0:59"

    def testInitInMinutesAndSeconds(self):
        tis = TimeInSeconds("3:25")
        assert tis.inSeconds() == "205"
        assert tis.inMinutesAndSeconds() == "3:25"

    def testAddSeconds(self):
        tis = TimeInSeconds("2:20")
        assert tis.addSeconds(20) == 160
        assert tis.inMinutesAndSeconds() == "2:40"

    def testSubtractSeconds(self):
        tis = TimeInSeconds("99")
        assert tis.subtractSeconds(50) == 49
        assert tis.inSeconds() == "49"

    def testOverdraw(self):
        tis = TimeInSeconds("88")
        assert tis.subtractSeconds(100) == -12
        assert tis.inSeconds() == "0"

class TestLoadJam(unittest.TestCase):
    def setUp(self):
        print '%s %s' % (self.id(), self.shortDescription())

    def testMessage(self):
        obj = LoadJam(None)
        assert _verifyMetaDataExists(obj, "message")
        assert obj.message() == "load jammed"

    def testPressOK(self):
        obj = LoadJam("returntoken")
        assert _verifyMetaDataExists(obj, "press")
        assert obj.press("ok") == "returntoken"
        


if __name__ == '__main__':
    unittest.main(defaultTest='makeMusicPlayerTest')
