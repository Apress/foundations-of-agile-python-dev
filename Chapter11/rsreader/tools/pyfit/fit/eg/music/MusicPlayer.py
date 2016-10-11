# Copyright (c) 2002 Cunningham & Cunningham, Inc.
# Read license.txt in this directory.
# Converted to Python 2003/07/24 by John Roth
# Since the original MusicPlayer class had entirely static methods and fields,
#   and instances were never created, I eliminated the class.


##from Music import Music
##import Simulator
##import MusicLibrary

playing = None
paused = 0

##### Controls #######

def play(song):
    global paused
    if paused == 0:
        Music.status = "loading"
        if song == playing:
            seconds = 0.3
        else:
            seconds = 2.5
        Simulator.nextPlayStarted = Simulator.schedule(seconds)
    else:
        Music.status = "playing"
        Simulator.nextPlayComplete = Simulator.schedule(paused)
        paused = 0

def pause():
    global paused
    Music.status = "pause"
    if (playing != None and paused == 0):
        paused = (Simulator.nextPlayComplete - Simulator.time) / 1000.0
        Simulator.nextPlayComplete = 0
        

def stop():
    Simulator.nextPlayStarted = 0
    Simulator.nextPlayComplete = 0
    playComplete()

####### Status ########

def secondsRemaining():
    if paused != 0:
        return paused
    if playing != None:
        return (Simulator.nextPlayComplete - Simulator.time) / 1000.0
    return 0

def minutesRemaining():
    result = round(secondsRemaining() / .6) / 100.0
    return result

########### Events ##############3

def playStarted():
    global playing
    Music.status = "playing"
    playing = MusicLibrary.looking
    Simulator.nextPlayComplete = Simulator.schedule(playing.seconds)

def playComplete():
    global playing
    Music.status = "ready"
    playing = None

