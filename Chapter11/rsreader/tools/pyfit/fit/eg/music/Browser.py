# Copyright (c) 2002 Cunningham & Cunningham, Inc.
# Released under the terms of the GNU General Public License version 2 or later.
# Converted to Python 2003/07/24 John Roth


from fit.Fixture import Fixture

# This is such a mess of recursive imports that I'm moving most of the
# imports here - this is the first module loaded by ActionFixture.
# Then I'm simply going to slam in the correct references after they're
# loaded. The named modules no longer have any imports of their own.
# Notice that this does create a dependency because there are two other
# top level modules: Display and Realtime.

import Dialog
import Music
import MusicLibrary
import MusicPlayer
import Simulator

# Initialize Dialog
Dialog.MusicPlayer = MusicPlayer
# Initialize MusicLibrary
MusicLibrary.Music = Music.Music
MusicLibrary.MusicPlayer = MusicPlayer
MusicLibrary.Simulator = Simulator
# Initialize MusicPlayer
MusicPlayer.Music = Music.Music
MusicPlayer.MusicLibrary = MusicLibrary
MusicPlayer.Simulator = Simulator
# Initialize Simulator
Simulator.Dialog = Dialog.Dialog
Simulator.MusicLibrary = MusicLibrary
Simulator.MusicPlayer = MusicPlayer
# from Music import Music
Music = Music.Music

#
# end of mystical magic
#

class Browser(Fixture):
    _typeDict = {}
    ###### Library ######
    
    _typeDict["library"] = "String"
    def library(self, path):
        MusicLibrary.load(path)

    _typeDict["totalSongs"] = "Int"
    def totalSongs(self):
        return len(MusicLibrary.library)

    ###### Select Detail #######

    _typeDict["playing"] = "String"
    def playing(self):
        return MusicPlayer.playing.title

    _typeDict["select"] = "Int"
    def select(self, i):
        MusicLibrary.select(MusicLibrary.library[i-1])

    _typeDict["title"] = "String"
    def title(self):
        return MusicLibrary.looking.title

    _typeDict["artist"] = "String"
    def artist(self):
        return MusicLibrary.looking.artist

    _typeDict["album"] = "String"
    def album(self):
        return MusicLibrary.looking.album
    
    _typeDict["year"] = "Int"
    def year(self):
        return MusicLibrary.looking.year

    _typeDict["time"] = "Float"
    def time(self):
        return MusicLibrary.looking.time()

    _typeDict["track"] = "String"
    def track(self):
        return MusicLibrary.looking.track()

    ####### Search Buttons #######

    _typeDict["sameAlbum"] = "String"
    def sameAlbum(self):
        MusicLibrary.findAlbum(MusicLibrary.looking.album)

    _typeDict["sameArtist"] = "String"
    def sameArtist(self):
        MusicLibrary.findArtist(MusicLibrary.looking.artist)

    _typeDict["sameGenre"] = "String"
    def sameGenre(self):
        MusicLibrary.findArtist(MusicLibrary.looking.genre)

    _typeDict["sameYear"] = "String"
    def sameYear(self):
        MusicLibrary.findArtist(MusicLibrary.looking.year)

    _typeDict["selectedSongs"] = "Int"
    def selectedSongs(self):
        return MusicLibrary.displayCount()

    _typeDict["showAll"] = "String"
    def showAll(self):
        MusicLibrary.findAll()

    ####### Play Buttons ########

    _typeDict["play"] = "String"
    def play(self):
        MusicPlayer.play(MusicLibrary.looking)

    _typeDict["pause"] = "String"
    def pause(self):
        MusicPlayer.pause()

    _typeDict["status"] = "String"
    def status(self):
        return Music.status

    _typeDict["remaining"] = "Float"
    _typeDict["remaining.precision"] = 2
    def remaining(self):
        return MusicPlayer.minutesRemaining()
