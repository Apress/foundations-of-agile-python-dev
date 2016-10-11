# Copyright (c) 2002 Cunningham & Cunningham, Inc.
# Read license.txt in this directory.
# Converted to Python 2003/07/24 by John Roth
# Note - since all the variables and methods in this were static, I
#   converted it to a pure module with no class.


##from Music import Music
##import Simulator
##import MusicPlayer

looking = None
library = []

def load(pathName):
    global library
    library = []
    fileObj = open(pathName, 'r')
    libList = fileObj.readlines()
    del libList[0]
    for song in libList:
        library.append(Music(song[:-2])) # looks like a tab on the end!!!

def select(music):
    global looking
    looking = music

def search(time):
    Music.status = "searching"
    nextTime = Simulator.schedule(time)
    Simulator.nextSearchComplete = nextTime

def searchComplete():
    if MusicPlayer.playing == None:
        Music.status = "ready"
    else:
        Music.status = "playing"

def findAll():
    search(3.2) # ???
    for song in library:
        song.selected = 1 # S/B true

def findArtist(artistName):
    search(2.3)
    for song in library:
        song.selected = (song.artist == artistName)

def findAlbum(albumName):
    search(1.1)
    for song in library:
        song.selected = (song.album == albumName)

def findGenre(genreName):
    search(0.2)
    for song in library:
        song.selected = (song.genre == genreName)

def findYear(year):
    search(0.8)
    for song in library:
        song.selected = (song.year == year)

def displayCount():
    count = 0
    for song in library:
        if song.selected: count += 1
    return count

def displayContents():
    return filter(lambda x: x.selected, library)
